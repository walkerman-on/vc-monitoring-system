# Образ для сборки
FROM python:3.12-alpine AS builder

# Установим рабочую директорию
WORKDIR /app

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1
ENV PYFILE=api-server.py

# Установим необходимые инструменты
RUN apk add --no-cache build-base gcc musl-dev linux-headers python3-dev

# Установка зависимостей
COPY api_server/requirements_api.txt .

RUN pip install --no-cache-dir -r requirements_api.txt

# Установка PyInstaller
RUN pip install --no-cache-dir pyinstaller

# Получение основного файла программы
COPY api_server/$PYFILE .
RUN pyinstaller --onefile --name=api_server $PYFILE

# Финальный минимальный образ
FROM alpine:latest

# Установим рабочую директорию
WORKDIR /app

# Скопируем программу после сборки в рабочую директорию
COPY --from=builder /app/dist/api_server /app/api_server

# Установим дополнительные зависимости, если необходимо
# RUN apk add --no-cache <дополнительные зависимости>

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1

# Определение команды по умолчанию с полным путем
CMD ["/app/api_server"]
