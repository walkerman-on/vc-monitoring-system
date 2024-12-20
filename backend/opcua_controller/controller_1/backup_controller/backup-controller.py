import os
import asyncio
import logging
from asyncua import Client
from opcua_controller.regulators import PID_REGULATOR

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Хранилище последних значений от основного контроллера
last_state = {
    "pressure": 0.0,
    "level": 0.0,
    "uprav1": 0.0,
    "uprav2": 0.0,
}

async def main():
    # Ссылка и пространство имён для подключения
    url = os.getenv('OPCUA_BACKUP_SERVER')
    namespace = os.getenv('OPCUA_BACKUP_NAMESPACE')


    logger.info(f"Подключаюсь к резервному серверу {url} и пространству имён {namespace} ...")

    async with Client(url=url) as client:
        nsidx = await client.get_namespace_index(namespace)
        logger.info(f"Индекс пространства имен '{namespace}': {nsidx}")

        # Ищем ссылки на переменные
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

        # Используем последние данные от основного контроллера
        PV1 = last_state["pressure"]
        PV2 = last_state["level"]
        u1 = last_state["uprav1"]
        u2 = last_state["uprav2"]

        await var_uprav1.write_value(float(u1))
        await var_uprav2.write_value(float(u2))

        while True:
            try:
                mode_pressure1 = await var_mode_pressure1.get_value()
                mode_level1 = await var_mode_level1.get_value()

                if mode_pressure1 == 0:
                    SP1 = await var_sp_pressure1.get_value()
                    u1 = pid1.control(SP1, PV1)
                    await var_uprav1.write_value(float(u1))

                if mode_level1 == 0:
                    SP2 = await var_sp_level1.get_value()
                    u2 = pid2.control(SP2, PV2)
                    await var_uprav2.write_value(float(u2))

                await asyncio.sleep(dt)

            except Exception as e:
                logger.error(f"Ошибка резервного контроллера: {e}")
                pass

if __name__ == "__main__":
    asyncio.run(main())
