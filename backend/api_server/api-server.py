
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
            # Получаем текущий статус всех контроллеров
            statuses = is_controller_running(CONTROLLER_NAMES)
            status = {
                "controllers": [
                    {
                        "controller_name": controller_name,
                        "status": "running" if status else "stopped"
                    }
                    for controller_name, status in statuses.items()
                ]
            }

            # Отправляем статус на клиент
            await websocket.send_json(status)
            
            # Получаем данные с контроллеров (давление, уровень и другие параметры)
            controller_data = await get_controller_data()
            await websocket.send_json(controller_data)

            # Ждём 1 секунду перед повторной проверкой статуса
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print(f"WebSocket соединение закрыто")

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

async def get_controller_data():
    """Получает данные с контроллеров (давление, уровень и другие параметры)."""
    async with Client(url=OPCUA_SERVER_URL) as client:
        try:
            nsidx = await client.get_namespace_index(OPCUA_NAMESPACE)
            
            # Получаем ссылки на переменные
            var_pressure1 = await client.nodes.root.get_child(
                f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Pressure_0"
            )

            var_level1 = await client.nodes.root.get_child(
                f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:LiqLevel_0"
            )

            # Чтение значений с контроллеров
            pressure = await var_pressure1.get_value()
            level = await var_level1.get_value()

            # Возвращаем данные с контроллеров
            return {
                "pressure": pressure,
                "level": level,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка получения данных с контроллеров: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)