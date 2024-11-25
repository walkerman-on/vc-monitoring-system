from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import docker
import asyncio
import os
from asyncua import Client

app = FastAPI()

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем клиент Docker
client = docker.from_env()

# Список контейнеров для отслеживания
CONTROLLER_NAMES = ["backend-main-controller-1-1", "backend-backup-controller-1-1"]

def is_controller_running(controller_names):
    """Проверяет, работает ли указанные контейнеры."""
    statuses = {}
    for controller_name in controller_names:
        try:
            container = client.containers.get(controller_name)
            statuses[controller_name] = container.status == "running"
        except docker.errors.NotFound:
            statuses[controller_name] = False
    return statuses

def restart_controller(controller_name: str):
    """Перезапускает контейнер контроллера."""
    try:
        container = client.containers.get(controller_name)
        container.restart()
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Контейнер {controller_name} не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при перезапуске контейнера {controller_name}: {e}")

@app.websocket("/status")
async def websocket_status(websocket: WebSocket):
    """Обрабатывает WebSocket-соединение для передачи статуса контроллеров и данных с OPC UA."""
    await websocket.accept()
    try:
        while True:
            statuses = is_controller_running(CONTROLLER_NAMES)
            status = {
                "controllers": []
            }

            for controller_name, is_running in statuses.items():
                if is_running:
                    try:
                        data = await get_controller_data(controller_name)
                        controller_status = {
                            "controller_name": controller_name,
                            "status": "running",
                            "data": data
                        }
                    except HTTPException as e:
                        controller_status = {
                            "controller_name": controller_name,
                            "status": "running",
                            "data": {"error": f"Ошибка получения данных: {e.detail}"}
                        }
                    except Exception as e:
                        controller_status = {
                            "controller_name": controller_name,
                            "status": "running",
                            "data": {"error": f"Неизвестная ошибка: {str(e)}"}
                        }
                else:
                    controller_status = {
                        "controller_name": controller_name,
                        "status": "stopped",
                        "data": {}
                    }
                status["controllers"].append(controller_status)

            # Отправляем статус на клиент
            await websocket.send_json(status)
            
            # Ждем 1 секунду перед повторной проверкой статуса
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print(f"WebSocket соединение закрыто")
    except Exception as e:
        print(f"Ошибка при обработке WebSocket: {e}")
        await websocket.send_text(f"Ошибка при обработке запроса: {e}")
        await websocket.close()


async def get_controller_data(controller_name: str):
    if controller_name == "backend-main-controller-1-1":
        server_url = OPCUA_SERVER_URL
        namespace = OPCUA_NAMESPACE
    elif controller_name == "backend-backup-controller-1-1":
        server_url = OPCUA_BACKUP_SERVER_URL
        namespace = OPCUA_BACKUP_NAMESPACE
    else:
        raise ValueError(f"Контроллер {controller_name} не найден")

    async with Client(url=server_url) as client:
        try:
            nsidx = await client.get_namespace_index(namespace)
            var_pressure = await client.nodes.root.get_child(
                f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Pressure_0"
            )
            var_level = await client.nodes.root.get_child(
                f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:LiqLevel_0"
            )
            sp_pressure = await client.nodes.root.get_child(
                f"0:Objects/{nsidx}:PID_0/{nsidx}:sp_0"
            )
            sp_level = await client.nodes.root.get_child(
                f"0:Objects/{nsidx}:PID_1/{nsidx}:sp_1"
            )
            upr1 = await client.nodes.root.get_child(
                f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Input2_0"
            )
            upr2 = await client.nodes.root.get_child(
                f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Input3_0"
            )

            # Считываем данные с OPC UA сервера
            pressure = await var_pressure.get_value()
            level = await var_level.get_value()
            pressure_setpoint = await sp_pressure.get_value()
            level_setpoint = await sp_level.get_value()
            upr1_value = await upr1.get_value()
            upr2_value = await upr2.get_value()

            # Возвращаем все данные, включая управляющие воздействия
            return {
                "pressure": pressure,
                "level": level,
                "setpoints": {
                    "pressure": pressure_setpoint,
                    "level": level_setpoint
                },
                "control": {
                    "uprav1": upr1_value,
                    "uprav2": upr2_value
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")

@app.post("/restart/{controller_name}")
def restart(controller_name: str):
    """Перезапускает указанный контроллер."""
    if controller_name in CONTROLLER_NAMES:
        if not is_controller_running([controller_name])[controller_name]:
            restart_controller(controller_name)
            return {"message": f"Контроллер {controller_name} перезапущен"}
        else:
            raise HTTPException(status_code=400, detail=f"Контроллер {controller_name} уже работает")
    else:
        raise HTTPException(status_code=404, detail=f"Контроллер с именем {controller_name} не найден")


# Настройки OPC UA
OPCUA_SERVER_URL = os.getenv("OPCUA_MAIN_SERVER")
OPCUA_NAMESPACE = os.getenv("OPCUA_MAIN_NAMESPACE")
OPCUA_BACKUP_SERVER_URL = os.getenv("OPCUA_BACKUP_SERVER")
OPCUA_BACKUP_NAMESPACE = os.getenv("OPCUA_BACKUP_NAMESPACE")


async def update_setpoint(controller_name: str, setpoint_type: str, value: float):
    """Обновляет значение уставки на OPC UA сервере."""
    async with Client(url=OPCUA_SERVER_URL) as client:
        try:
            nsidx = await client.get_namespace_index(OPCUA_NAMESPACE)
            if setpoint_type == "pressure":
                var_sp = await client.nodes.root.get_child(
                    f"0:Objects/{nsidx}:PID_0/{nsidx}:sp_0"
                )
            elif setpoint_type == "level":
                var_sp = await client.nodes.root.get_child(
                    f"0:Objects/{nsidx}:PID_1/{nsidx}:sp_1"
                )
            else:
                raise ValueError("Недопустимый тип уставки. Используйте 'pressure' или 'level'.")

            await var_sp.write_value(float(value))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка обновления уставки: {e}")

@app.post("/setpoint/{controller_name}/{setpoint_type}")
async def setpoint(controller_name: str, setpoint_type: str, value: float):
    """Обновляет уставку для указанного контроллера."""
    if controller_name not in CONTROLLER_NAMES:
        raise HTTPException(status_code=404, detail=f"Контроллер {controller_name} не найден")
    try:
        await update_setpoint(controller_name, setpoint_type, value)
        return {"message": f"Уставка {setpoint_type} для контроллера {controller_name} обновлена на {value}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
