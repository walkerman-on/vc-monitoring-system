# Образ для сборки
FROM python:3.12-alpine AS builder

# Установим рабочую директорию
WORKDIR /app

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1
ENV PYFILE=opcua-model.py

# Установим необходимые инструменты и зависимости для сборки
RUN apk add --no-cache \
	build-base \
	musl-dev \
	libffi-dev \
	openblas-dev \
	gfortran

# Установка зависимостей
COPY requirements_model.txt .
RUN pip install --no-cache-dir -r requirements_model.txt

# Получение основного файла программы
COPY $PYFILE .
RUN pyinstaller --onefile --name=pyprog $PYFILE

# Финальный минимальный образ
FROM alpine:latest

# Установим рабочую директорию
WORKDIR /app

# Файл для работы модели сепаратора
COPY thermo_db.json .

# Скопируем программу после сборки в рабочую директорию
COPY --from=builder /app/dist/pyprog /app/pyprog

# Отключение буферизации вывода Python
ENV PYTHONUNBUFFERED=1

# Определение команды по умолчанию с полным путем
CMD ["/app/pyprog"]
