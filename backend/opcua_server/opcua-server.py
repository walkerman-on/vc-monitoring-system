import asyncio
import os
import logging
from asyncua import Server, ua
from asyncua.common.methods import uamethod

# Настройка логирования
logging.basicConfig(level=logging.INFO)

@uamethod
def func(parent, value):
    return value * 2

async def main():
    try:
        # Инициализация сервера
        server = Server()
        await server.init()

        # Настройка точки входа
        server_endpoint = os.getenv('OPCUA_MAIN_SERVER', 'opc.tcp://0.0.0.0:4840')
        server.set_endpoint(server_endpoint)
        logging.info(f"Server endpoint set to: {server_endpoint}")

        # Создаем пространство имён
        uri = os.getenv('OPCUA_MAIN_NAMESPACE', 'http://example.org')
        idx = await server.register_namespace(uri)
        logging.info(f"Namespace registered: {uri}")

        # Заполняем пространство имён объектами
        N_SEPS = 1
        sep_set = ['Input1', 'Input2', 'Input3', 'Pressure', 'Molar',
                   'FlowMixIn', 'FlowGasOut', 'FlowLiqOut', 'LiqLevel']
        objs = []  # Переносим создание списка объектов за пределы цикла
        for n in range(N_SEPS):
            try:
                obj = await server.nodes.objects.add_object(idx, f"SEPARATOR_{n}")
                objs.append(obj)
                for m in range(len(sep_set)):
                    initial_value = 45.0 if m < 4 else 0.0
                    sep_var = await objs[n].add_variable(idx, f"{sep_set[m]}_{n}", initial_value)
                    await sep_var.set_writable()
            except Exception as e:
                logging.error(f"Ошибка при добавлении объекта SEPARATOR_{n}: {e}")

        N_PIDS = 2
        pid_set = ['sp', 'mode', 'kp', 'ki', 'kd', 'dt', 'int', 'pr_err']
        pid_float_set = [2, 1, 0, 0.1, 0, 0]
        pids = []  # Переносим создание списка PID объектов за пределы цикла
        for n in range(N_PIDS):
            try:
                pid_obj = await server.nodes.objects.add_object(idx, f"PID_{n}")
                pids.append(pid_obj)

                for m in range(len(pid_set)):
                    initial_value = 1150.0 if (n == 0 and m == 0) else (4.5 if (n == 1 and m == 0) else 0.0)
                    pid_var = await pids[n].add_variable(idx, f"{pid_set[m]}_{n}", initial_value)
                    await pid_var.set_writable()
            except Exception as e:
                logging.error(f"Ошибка при добавлении объекта PID_{n}: {e}")

        # Добавляем метод
        try:
            await server.nodes.objects.add_method(
                ua.NodeId("ServerMethod", idx),
                ua.QualifiedName("ServerMethod", idx),
                func,
                [ua.VariantType.String],
                [ua.VariantType.String],
            )
            logging.info("Method 'ServerMethod' added.")
        except Exception as e:
            logging.error(f"Ошибка при добавлении метода: {e}")

        # Запуск сервера
        async with server:
            logging.info("Server is running...")
            while True:
                await asyncio.sleep(0.150)

    except Exception as e:
        logging.error(f"Ошибка в процессе работы сервера: {e}")

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
