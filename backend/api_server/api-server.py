from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import docker
import asyncio

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
CONTROLLER_NAMES = ["backend-opcua-controller-1-1", "backend-opcua-controller-2-1"]

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
    """Обрабатывает WebSocket-соединение для передачи статуса контроллеров."""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
