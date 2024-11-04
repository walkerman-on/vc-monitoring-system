from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import psutil
import docker

app = FastAPI()

# Настройки
CONTROLLER_NAME = "backend-opcua-controller-1"

def is_controller_running():
    """Проверяет, работает ли контроллер."""
    for proc in psutil.process_iter(['pid', 'name']):
        if CONTROLLER_NAME in proc.info['name']:
            return True
    return False

def restart_controller():
    client = docker.from_env()  # Инициализируем клиент Docker
    print("Перезапуск контроллера...")
    client.containers.get(CONTROLLER_NAME).restart()  # Перезапускаем контейнер

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
