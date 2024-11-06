from fastapi import FastAPI, HTTPException
import docker

app = FastAPI()

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

@app.get("/status")
def get_status():
    """Возвращает статус контроллера."""
    running = is_controller_running()
    return {"status": "running" if running else "stopped"}

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
