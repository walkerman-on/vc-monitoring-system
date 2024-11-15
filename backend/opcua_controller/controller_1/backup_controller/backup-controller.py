import os
import asyncio
from asyncua import Client
from opcua_controller.regulators import PID_REGULATOR

async def main():
    # Подключение к OPC UA серверу
    url = os.getenv('OPCUA_MAIN_SERVER')
    namespace = os.getenv('OPCUA_MAIN_NAMESPACE')

    print(f"Подключение ко второму контроллеру по ссылке {url} и к пространству имен {namespace}...")

    async with Client(url=url) as client:
        # Поиск индекса пространства имен
        nsidx = await client.get_namespace_index(namespace)
        print(f"Индекс пространства имен '{namespace}': {nsidx}")

        # Получаем ссылки на переменные
        var_uprav3 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Input4_0"
        )
        var_uprav4 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Input5_0"
        )
        
        var_pressure2 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Pressure_1"
        )
        var_level2 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:LiqLevel_1"
        )

        var_sp_pressure2 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:PID_2/{nsidx}:sp_2"
        )

        var_sp_level2 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:PID_3/{nsidx}:sp_3"
        )

        var_mode_pressure2 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:PID_2/{nsidx}:mode_2"
        )

        var_mode_level2 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:PID_3/{nsidx}:mode_3"
        )

        # Время дискретизации
        dt = 0.1

        # Настроечные параметры PID для второго контроллера
        OP_MAX = 100
        OP_MIN = 0
        TAU_FILT = 0

        kP3 = 1.2
        kI3 = 0.3
        kD3 = 0

        kP4 = 8
        kI4 = 4
        kD4 = 0

        SP3 = await var_sp_pressure2.get_value()
        SP4 = await var_sp_level2.get_value()

        pid3 = PID_REGULATOR(dt, kP3, kI3, kD3, OP_MAX, OP_MIN, TAU_FILT)
        pid4 = PID_REGULATOR(dt, kP4, kI4, kD4, OP_MAX, OP_MIN, TAU_FILT)

        # Первый шаг регулирования
        PV3 = await var_pressure2.get_value()
        print(PV3)
        u3 = pid3.control(SP3, PV3)
        await var_uprav3.write_value(float(u3))
        print(f"Read Pressure: {PV3} - Set value {u3}")

        PV4 = await var_level2.get_value()
        print(PV4)
        u4 = pid4.control(SP4, PV4)
        await var_uprav4.write_value(float(u4))
        print(f"Read Level: {PV4} - Set value {u4}")

        while True:
            mode_pressure2 = await var_mode_pressure2.get_value()
            mode_level2 = await var_mode_level2.get_value()

            if mode_pressure2 == 0:
                SP3 = await var_sp_pressure2.get_value()
                PV3 = await var_pressure2.get_value()
                print(PV3)
                u3 = pid3.control(SP3, PV3)
                await var_uprav3.write_value(float(u3))
                print(f"Read Pressure: {PV3} - Set value {u3}")
            else:
                pid3.clear()

            if mode_level2 == 0:
                SP4 = await var_sp_level2.get_value()
                PV4 = await var_level2.get_value()
                print(PV4)
                u4 = pid4.control(SP4, PV4)
                await var_uprav4.write_value(float(u4))
                print(f"Read Level: {PV4} - Set value {u4}")
            else:
                pid4.clear()

            await asyncio.sleep(dt)

if __name__ == "__main__":
    asyncio.run(main())
