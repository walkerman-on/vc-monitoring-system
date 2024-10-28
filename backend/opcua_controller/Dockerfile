# Образ для сборки
FROM python:3.12-alpine AS builder

# Установим рабочую директорию
WORKDIR /app

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1
ENV PYFILE=opcua-controller.py

# Установим необходимые инструменты
RUN apk add --no-cache binutils

# Установка зависимостей
COPY opcua_controller/requirements_controller.txt . 
COPY opcua_controller/regulators.py .                 
RUN pip install --no-cache-dir -r requirements_controller.txt

# Получение основного файла программы
COPY opcua_controller/$PYFILE .                       
RUN pyinstaller --onefile --name=pyprog $PYFILE

# Финальный минимальный образ
FROM alpine:latest

# Установим рабочую директорию
WORKDIR /app

COPY --from=builder /app/regulators.py .             
COPY --from=builder /app/dist/pyprog /app/pyprog      

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1

# Определение команды по умолчанию с полным путем
CMD ["/app/pyprog"]
