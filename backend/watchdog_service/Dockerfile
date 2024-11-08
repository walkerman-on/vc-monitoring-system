# Образ для сборки
FROM python:3.12-alpine AS builder

# Установим рабочую директорию
WORKDIR /app

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1
ENV PYFILE=watchdog-service.py

# Установим необходимые инструменты
RUN apk add --no-cache build-base
# Установим необходимые инструменты и заголовочные файлы
RUN apk add --no-cache gcc python3-dev musl-dev linux-headers

# Установка зависимостей
COPY watchdog_service/requirements_watchdog.txt .

RUN pip install --no-cache-dir -r requirements_watchdog.txt

# Установка PyInstaller
RUN pip install --no-cache-dir pyinstaller
# Получение основного файла программы
COPY watchdog_service/$PYFILE .
RUN pyinstaller --onefile --name=watchdog_service $PYFILE

# Финальный минимальный образ
FROM alpine:latest

# Установим рабочую директорию
WORKDIR /app

# Скопируем программу после сборки в рабочую директорию
COPY --from=builder /app/dist/watchdog_service /app/watchdog_service

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1

# Определение команды по умолчанию с полным путем
CMD ["/app/watchdog_service"]
