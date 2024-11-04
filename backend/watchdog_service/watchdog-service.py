import time
import subprocess
import psutil
import docker
import logging

# Настройки
CONTROLLER_NAME = "backend-opcua-controller-1"
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

def is_controller_running():
    """Проверяет, работает ли контроллер."""
    for proc in psutil.process_iter(['pid', 'name']):
        if CONTROLLER_NAME in proc.info['name']:
            logging.info(f"Найден процесс контроллера: {proc.info['name']} (PID: {proc.info['pid']})")
            return True
    logging.info("Контроллер не запущен.")
    return False

def restart_controller():
    client = docker.from_env()  # Инициализируем клиент Docker
    try:
        logging.info("Перезапуск контроллера...")
        container = client.containers.get(CONTROLLER_NAME)
        container.restart()  # Перезапускаем контейнер
        logging.info(f"Контейнер {CONTROLLER_NAME} перезапущен.")
    except docker.errors.NotFound:
        logging.error(f"Контейнер {CONTROLLER_NAME} не найден.")
    except Exception as e:
        logging.error(f"Ошибка при перезапуске контейнера: {e}")

def monitor_controller():
    """Мониторит состояние контроллера и перезапускает его при необходимости."""
    while True:
        if not is_controller_running():
            logging.warning("Контроллер отключен. Попытка перезапуска...")
            restart_controller()
        else:
            logging.info("Контроллер работает.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    check_docker()
    monitor_controller()
