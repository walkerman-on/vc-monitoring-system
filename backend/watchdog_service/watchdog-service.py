import time
import subprocess
import docker
import logging

# Настройки
CONTROLLER_NAMES = ["backend-main-controller-1-1"]
CHECK_INTERVAL = 5  # Интервал проверки состояния (в секундах)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_docker():
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, check=True)
        logging.info(f"Docker доступен: {result.stdout.strip()}")
    except FileNotFoundError:
        logging.error("Docker не найден!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка при выполнении команды docker: {e}")

def is_controller_running(controller_name):
    """Проверяет, работает ли контейнер с указанным именем."""
    client = docker.from_env()
    try:
        container = client.containers.get(controller_name)
        if container.status == "running":
            logging.info(f"Контейнер {controller_name} работает.")
            return True
        else:
            logging.info(f"Контейнер {controller_name} не запущен (статус: {container.status}).")
            return False
    except docker.errors.NotFound:
        logging.error(f"Контейнер {controller_name} не найден.")
        return False
    except Exception as e:
        logging.error(f"Ошибка при проверке состояния контейнера {controller_name}: {e}")
        return False

def restart_controller(controller_name):
    """Перезапускает контейнер с указанным именем."""
    client = docker.from_env()  # Инициализируем клиент Docker
    try:
        logging.info(f"Перезапуск контроллера {controller_name}...")
        container = client.containers.get(controller_name)
        container.restart()  # Перезапускаем контейнер
        logging.info(f"Контейнер {controller_name} перезапущен.")
    except docker.errors.NotFound:
        logging.error(f"Контейнер {controller_name} не найден.")
    except Exception as e:
        logging.error(f"Ошибка при перезапуске контейнера {controller_name}: {e}")

def monitor_controllers():
    """Мониторит состояние обоих контроллеров и перезапускает их при необходимости."""
    while True:
        for controller_name in CONTROLLER_NAMES:
            if not is_controller_running(controller_name):
                logging.warning(f"Контроллер {controller_name} отключен. Попытка перезапуска...")
                restart_controller(controller_name)
            else:
                logging.info(f"Контроллер {controller_name} работает.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    check_docker()
    monitor_controllers()
