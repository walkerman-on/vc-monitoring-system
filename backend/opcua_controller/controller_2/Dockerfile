# Образ для сборки
FROM python:3.12-alpine AS builder

# Установим рабочую директорию
WORKDIR /app

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1
ENV PYFILE=controller-2.py

# Установим необходимые инструменты
RUN apk add --no-cache binutils

# Установка зависимостей
COPY opcua_controller/requirements_controller.txt . 
COPY opcua_controller/regulators.py .                 
RUN pip install --no-cache-dir -r requirements_controller.txt

# Копируем всю папку opcua_controller
COPY opcua_controller /app/opcua_controller

# Получение основного файла программы
COPY opcua_controller/controller_2/$PYFILE .                       
RUN pyinstaller --onefile --hidden-import=asyncua --name=pyprog $PYFILE

# Финальный минимальный образ
FROM alpine:latest

# Установим рабочую директорию
WORKDIR /app

# Установим PYTHONPATH
ENV PYTHONPATH="/app/opcua_controller"

# Копируем исполнимый файл и все необходимые файлы Python
COPY --from=builder /app/opcua_controller /app/opcua_controller
COPY --from=builder /app/dist/pyprog /app/pyprog

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1

# Определение команды по умолчанию с полным путем
CMD ["/app/pyprog"]
