from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import docker
import asyncio

app = FastAPI()

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000"],  # Здесь укажите фронтенд-URL
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройки
CONTROLLER_NAME = "backend-opcua-controller-1"

# Инициализируем клиент Docker
client = docker.from_env()

def is_controller_running():
    """Проверяет, работает ли контейнер контроллера."""
    try:
        container = client.containers.get(CONTROLLER_NAME)
        return container.status == "running"
    except docker.errors.NotFound:
        return False

def restart_controller():
    """Перезапускает контейнер контроллера."""
    try:
        container = client.containers.get(CONTROLLER_NAME)
        container.restart()
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Контейнер не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при перезапуске контейнера: {e}")

@app.websocket("/status")
async def websocket_status(websocket: WebSocket):
    """Обрабатывает WebSocket-соединение для передачи статуса контроллера."""
    await websocket.accept()
    try:
        while True:
            # Получаем текущий статус контроллера
            running = is_controller_running()
            status = {"status": "running" if running else "stopped"}
            
            # Отправляем статус на клиент
            await websocket.send_json(status)
            
            # Ждём 1 секунду перед повторной проверкой статуса
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        print("WebSocket соединение закрыто")

@app.post("/restart")
def restart():
    """Перезапускает контроллер."""
    if not is_controller_running():
        restart_controller()
        return {"message": "Контроллер перезапущен"}
    else:
        raise HTTPException(status_code=400, detail="Контроллер уже работает")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
