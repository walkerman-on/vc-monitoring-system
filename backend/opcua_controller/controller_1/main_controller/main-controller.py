import os
import asyncio
from asyncua import Client
from opcua_controller.regulators import PID_REGULATOR

async def main():
    # Ссылка для подключения
    url = os.getenv('OPCUA_MAIN_SERVER')
    # Пространство имён для чтения
    namespace = os.getenv('OPCUA_MAIN_NAMESPACE')

    print(f"Подключаюсь по ссылке {url} и к пространству имён {namespace} ...")

    async with Client(url=url) as client:
        # Ищем индекс пространства имен
        nsidx = await client.get_namespace_index(namespace)
        print(f"Индекс пространства имен '{namespace}': {nsidx}")

        # Получаем ссылки на переменные
        var_uprav1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Input2_0"
        )
        var_uprav2 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Input3_0"
        )

        var_pressure1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:Pressure_0"
        )

        var_level1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_0/{nsidx}:LiqLevel_0"
        )

        var_sp_pressure1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:PID_0/{nsidx}:sp_0"
        )

        var_sp_level1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:PID_1/{nsidx}:sp_1"
        )

        var_mode_pressure1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:PID_0/{nsidx}:mode_0"
        )

        var_mode_level1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:PID_1/{nsidx}:mode_1"
        )

        dt = 0.1

        # Настройка PID
        OP_MAX = 100
        OP_MIN = 0
        TAU_FILT = 0

        kP1 = 1.2
        kI1 = 0.3
        kD1 = 0

        kP2 = 8
        kI2 = 4
        kD2 = 0

        SP1 = await var_sp_pressure1.get_value()
        SP2 = await var_sp_level1.get_value()

        pid1 = PID_REGULATOR(dt, kP1, kI1, kD1, OP_MAX, OP_MIN, TAU_FILT)
        pid2 = PID_REGULATOR(dt, kP2, kI2, kD2, OP_MAX, OP_MIN, TAU_FILT)

        # Первый шаг регулирования
        PV1 = await var_pressure1.get_value()
        print(PV1)
        u1 = pid1.control(SP1, PV1)
        await var_uprav1.write_value(float(u1))
        print(f"Read Pressure: {PV1} - Set value {u1}")

        PV2 = await var_level1.get_value()
        print(PV2)
        u2 = pid2.control(SP2, PV2)
        await var_uprav2.write_value(float(u2))
        print(f"Read Level: {PV2} - Set value {u2}")

        while True:
            mode_pressure1 = await var_mode_pressure1.get_value()
            mode_level1 = await var_mode_level1.get_value()

            if mode_pressure1 == 0:
                SP1 = await var_sp_pressure1.get_value()
                PV1 = await var_pressure1.get_value()
                print(PV1)
                u1 = pid1.control(SP1, PV1)
                await var_uprav1.write_value(float(u1))
                print(f"Read Pressure: {PV1} - Set value {u1}")
            else:
                pid1.clear()

            if mode_level1 == 0:
                SP2 = await var_sp_level1.get_value()
                PV2 = await var_level1.get_value()
                print(PV2)
                u2 = pid2.control(SP2, PV2)
                await var_uprav2.write_value(float(u2))
                print(f"Read Level: {PV2} - Set value {u2}")
            else:
                pid2.clear()

            await asyncio.sleep(dt)

if __name__ == "__main__":
    asyncio.run(main())
