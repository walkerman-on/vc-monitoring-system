# Образ для сборки
FROM python:3.12-alpine AS builder
# Установим рабочую директорию
WORKDIR /app
# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1
ENV PYFILE=opcua-server.py
# Установим необходимые инструменты
RUN apk add --no-cache binutils
# Установка зависимостей
COPY opcua_server/requirements_server.txt .

RUN pip install --no-cache-dir -r requirements_server.txt
# Получение основного файла программы
COPY opcua_server/$PYFILE .
RUN pyinstaller --onefile --name=pyprog $PYFILE

# Финальный минимальный образ
FROM alpine:latest
# Установим рабочую директорию
WORKDIR /app
# Скопируем программу после сборки в рабочую директорию
COPY --from=builder /app/dist/pyprog /app/pyprog
# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1
# Определение команды по умолчанию с полным путем
CMD ["/app/pyprog"]