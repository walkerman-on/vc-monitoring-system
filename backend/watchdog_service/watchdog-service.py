import time
import subprocess
import docker
import logging

# Настройки
CONTROLLER_NAMES = {
    "main": "backend-main-controller-1-1",
    "backup": "backend-backup-controller-1-1"
}

ACTIVE_CONTROLLER = "main"  # Начальный активный контроллер
CHECK_INTERVAL = 5  # Интервал проверки состояния (в секундах)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def switch_to_backup():
    """Переключение на резервный контроллер."""
    global ACTIVE_CONTROLLER
    ACTIVE_CONTROLLER = "backup"
    logging.warning("Переключение на резервный контроллер.")

def switch_to_main():
    """Возврат к основному контроллеру."""
    global ACTIVE_CONTROLLER
    ACTIVE_CONTROLLER = "main"
    logging.info("Основной контроллер восстановлен. Возвращаемся к основному.")

def check_docker():
    """Проверка доступности Docker на машине."""
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
    """Мониторит состояние контроллеров и перезапускает их при необходимости."""
    global ACTIVE_CONTROLLER

    while True:
        main_running = is_controller_running(CONTROLLER_NAMES["main"])
        backup_running = is_controller_running(CONTROLLER_NAMES["backup"])

        if not main_running:
            logging.warning("Основной контроллер отключен.")
            if not backup_running:
                logging.warning("Резервный контроллер тоже неактивен. Перезапускаем оба контроллера.")
                restart_controller(CONTROLLER_NAMES["main"])
                restart_controller(CONTROLLER_NAMES["backup"])
            else:
                if ACTIVE_CONTROLLER != "backup":
                    switch_to_backup()  # Переключаемся на резервный контроллер
        else:
            if ACTIVE_CONTROLLER == "backup":
                switch_to_main()  # Возвращаемся к основному контроллеру

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    check_docker()
    monitor_controllers()
