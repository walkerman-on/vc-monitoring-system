import asyncio
#import logging
from asyncua import Server, ua
from asyncua.common.methods import uamethod
import os

@uamethod
def func(parent, value):
    return value * 2

async def main():
    # Настройка логгирования
    #_logger = logging.getLogger(__name__)

    # Инициализация сервера
    server = Server()
    await server.init()
    
    # Точка входа
    server.set_endpoint(os.getenv('OPCUA_MAIN_SERVER'))

    # Создаем пространство имён
    uri = os.getenv('OPCUA_MAIN_NAMESPACE')
    idx = await server.register_namespace(uri)

    # Заполняем пространство имён объектами
    # server.nodes, содержит ссылки на очень распространенные узлы, такие как objects и root
    N_SEPS = 1
    sep_set = ['Input1', 'Input2', 'Input3', 'Pressure', 'Molar',
                'FlowMixIn','FlowGasOut','FlowLiqOut','LiqLevel']
    for n in range(N_SEPS):
        if n==0:
            objs = []
        obj = await server.nodes.objects.add_object(idx, f"SEPARATOR_{n}")
        objs.append(obj)
        for m in range(len(sep_set)): 
            if m < 4:
                sep_var = await objs[n].add_variable(idx, f"{sep_set[m]}_{n}", 45.0)
            else:
                sep_var = await objs[n].add_variable(idx, f"{sep_set[m]}_{n}", 0.0)
            await sep_var.set_writable()

    N_PIDS = 2
    pid_set = ['sp','mode','kp', 'ki', 'kd', 'dt', 'int', 'pr_err']
    pid_float_set = [2, 1, 0, 0.1, 0, 0]
    for n in range(N_PIDS):
        if n==0:
            pids = []
        pid_obj = await server.nodes.objects.add_object(idx, f"PID_{n}")
        pids.append(pid_obj)

        for m in range(len(pid_set)): 
            
            if (n==0) and (m==0):
                pid_var = await pids[n].add_variable(idx, f"{pid_set[m]}_{n}", 1150.0)
            elif (n==1) and (m==0):
                pid_var = await pids[n].add_variable(idx, f"{pid_set[m]}_{n}", 4.5)
            else:
                pid_var = await pids[n].add_variable(idx, f"{pid_set[m]}_{n}", 0.0)  
             
            await pid_var.set_writable()

    await server.nodes.objects.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName("ServerMethod", idx),
        func,
        [ua.VariantType.String],
        [ua.VariantType.String],
    )

    #_logger.info("Запуск сервера!")

    async with server:
        while True:
            await asyncio.sleep(0.150)

if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(), debug=True)