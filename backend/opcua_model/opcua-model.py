#from scipy.integrate import odeint
import time
import json
import scipy
import asyncio
import numpy as np
from scipy import optimize
from asyncua import Client
import os

# Ссылка для подключения
url = os.getenv('OPCUA_MAIN_SERVER')
# Пространство имён для чтения
namespace = os.getenv('OPCUA_MAIN_NAMESPACE')

async def main():
    print(f"Подключаюсь к {url} ...")
    async with Client(url=url) as client:

        # Ищем индекс пространства имен
        nsidx = await client.get_namespace_index(namespace)
        print(f"Индекс пространства имен '{namespace}': {nsidx}")

        n = 0

        # Получаем ссылку на переменную
        var_upr1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_{n}/{nsidx}:Input1_{n}"
        )

        # Получаем ссылку на переменную
        var_upr2 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_{n}/{nsidx}:Input2_{n}"
        )

        # Получаем ссылку на переменную
        var_upr3 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_{n}/{nsidx}:Input3_{n}"
        )

        # Давление в системе
        var_pressure1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_{n}/{nsidx}:Pressure_{n}"
        )

        # Мольная доля отгона w
        var_molar1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_{n}/{nsidx}:Molar_{n}"
        )

        # Входной расход смеси
        var_flow_mix_in1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_{n}/{nsidx}:FlowMixIn_{n}"
        )

        # Выходной расход газа
        var_flow_gas_out1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_{n}/{nsidx}:FlowGasOut_{n}"
        )

        # Выходной расход жидкости
        var_flow_liq_out1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_{n}/{nsidx}:FlowLiqOut_{n}"
        )

        # Уровень жидкости
        var_liq_level1 = await client.nodes.root.get_child(
            f"0:Objects/{nsidx}:SEPARATOR_{n}/{nsidx}:LiqLevel_{n}"
        )



        # Первое значение управляющего воздействия (по умолчанию)
        u1,u2,u3 = await var_upr1.get_value(), await var_upr2.get_value(), await var_upr3.get_value()

        with open('thermo_db.json', encoding='utf-8') as f:
            data = json.load(f)

        #инициализация
        comp_list =  ['C2H6','C3H8','H2O']

        # Мольные доли всех компонентов
        z = [0.2, 0.7, 0.1]

        sep_vol = 10
        sep_diam = 1.5
        init_fluid_in = 30.325

        # Граничные условия
        press_input = 1400000
        press_output_gas = 1100000
        press_output_liq = 1100000
        press_sep = 1100000

        # Начальная температура (изотермический)
        T_init = 295.5

        # Коэф мест сопр
        KMS = [0.03, 0.1, 0.3]

        # Начальное значение моль в-ва (газ+жидкость)
        mol_in_sep = 30325

        molar_mass = []
        density_liquid_20 = []
        antoine_coefs = {}

        for i in comp_list:
            molar_mass.append(float(data[i]['molar_mass']))
            density_liquid_20.append(int(data[i]['density_liquid_20']))
            antoine_coefs[i] = [float(data[i]['antoine_A']), float(data[i]['antoine_B']), float(data[i]['antoine_C'])]

        # давление насыщенных паров [Па]
        sat_press = [] 
        for i in comp_list:
            sat_press.append(np.exp(antoine_coefs[i][0]-(antoine_coefs[i][1])/(antoine_coefs[i][2]+T_init))*133.3)

        # k_balance = [] #константа равновсия
        # for i in comp_list:
        #     k_balance.append(sat_press[i]/press_sep)

        def Rachford_Rice(z,p_res):
            k_balance = []
            for i in range(len(comp_list)):
                k_balance.append(sat_press[i]/p_res)
            K = np.array(k_balance)  # постоянная равновесия
            n = len(z)
            if (sum(np.array(z * K)) > 1) and (sum(np.array(z / K)) > 1):  # двухфазная область
                def w1(w2):
                    result = np.array(sum(z * (1 - K) / (1 + (K - 1) * w2)))
                    return float(result)
                w = float(optimize.fsolve(w1, 0.5))  # Уравнение Речфорда-Райса
                x = np.array(z / (1 + (K - 1) * w))
                y = np.array(K * x).tolist()  # Мольная доля компонентов в газе
            elif sum(np.array(z * K)) <= 1:
                w = 0
                x = z
                y = [0] * n
            elif sum(np.array(z / K)) <= 1:
                w = 1
                y = z
                x = [0] * n
            return w, x, y

        def density_gas(P, T, y, Molar_mass):
            R0 = 0
            ro = []
            for i in range(len(Molar_mass)):
                ro.append(P*Molar_mass[i]/(8.314*T))
                R0 += ro[i]*y[i]
            return R0, ro
        
        def density_fluid(T, density_20,x):
            R0 = 0
            ro = []
            T = T - 273.15
            for i in range(len(density_20)):
                ro.append(density_20[i] - 0.58/(density_20[i]/1000)*(T-20) -
                        abs(T-1200*(density_20[i]/1000 - 0.68))/1000*(T-20))
                R0 += ro[i]*x[i]
            return R0, ro
        
        def density_mix(w, x, y, z, density_gas, density_fluid, Molar_mass):
            M_mix = 0
            summ = 0
            for i in range(len(Molar_mass)):
                M_mix += z[i]*Molar_mass[i]
                summ +=(y[i]*w/density_gas[i] + x[i]*(1-w)/density_fluid[i])*Molar_mass[i]
            ro = M_mix/summ
            return ro

        def molar_flow(U, P_in, P_out, D,ro_mix, KMS, Molar_mass):
            U1= U/100
            d_P = P_in-P_out
            Ksi =(106.7189-465.8533*U1+788.3688*U1*U1-600.8218*U1*U1*U1+172.5874*U1*U1*U1*U1)*KMS #пропускная способность входит как произведение
            return (ro_mix*(np.pi*(D**2)/4)*((2*d_P/(Ksi*ro_mix))**(1/2)))/sum(Molar_mass)

        def p_resevoir(x,mu):
            R = 8.31

            y = np.zeros(2)
            M_cm = sum(np.array(z)*np.array(molar_mass))
            for i in range(len(comp_list)):
                    # Где x[0] - Давление, x[1] - доля отгона w
                y[0] += (z[i]*(sat_press[i]/x[0]-1))/(1+(sat_press[i]/x[0]-1)*x[1])
            for i in range(len(comp_list)):
                y[1] += ((z[i]*sat_press[i]*x[1]/((x[0]+sat_press[i]*x[1]-x[0]*x[1])*(x[0]*molar_mass[i]/(R*T_init))))+(z[i]*(1-x[1])/((1+x[1]*(sat_press[i]/x[0] - 1))*d_fld_comp[i])))*molar_mass[i]
            y[1] = sep_vol*M_cm/y[1] - M_cm*mu
            return y

        def main(P_init, w_init,T, density_20,z,mu):
            P_resevoir = scipy.optimize.fsolve(p_resevoir,(P_init, w_init), args=(mu))[0]
            w_out, x_out, y_out = Rachford_Rice(z,P_resevoir)
            d_fluid, d_fld_comp = density_fluid(T, density_20,x_out)
            d_gas, d_gas_comp = density_gas(P_resevoir, T, y_out, molar_mass)
            d_cm = density_mix(w_out, x_out, y_out, z, d_gas_comp, d_fld_comp, molar_mass)
            F_in = molar_flow(persentage_open[0], press_input, P_resevoir, 0.05, d_cm, KMS[0], molar_mass)
            F_gas_out = molar_flow(persentage_open[1], P_resevoir, press_output_gas, 0.05, d_gas, KMS[1], molar_mass)
            F_oil_out = molar_flow(persentage_open[2], P_resevoir, press_output_liq, 0.05, d_fluid, KMS[2], molar_mass)
            level = (sep_vol/(np.pi*(sep_diam*sep_diam)/4))*(1 - w_out)
            mu = mu + (F_in - F_gas_out - F_oil_out)
            return P_resevoir, w_out, x_out, y_out, d_fluid, d_gas, d_cm, F_in, F_gas_out, F_oil_out, level, mu, d_fld_comp

        # Начальные значения степени открытия клапанов
        global persentage_open
        persentage_open = [u1, u2, u3]

        # 0 - вход
        # 1 - газ
        # 2 - жидкость
        
        w, x, y = Rachford_Rice(z,press_sep)
        global d_fld_comp
        d_fluid, d_fld_comp = density_fluid(T_init, density_liquid_20,x)


        # w_out = 1 - начальное условие доли отгона
        data = main(press_sep, 1, T_init, density_liquid_20, z, mol_in_sep)

        P_resevoir = data[0]
        w_out = data[1]
        x_out = data[2]
        y_out = data[3]
        d_fluid = data[4]
        d_gas = data[5]
        d_cm = data[6]
        F_in = data[7]
        F_gas_out = data[8]
        F_oil_out = data[9]
        level = data[10]
        mu = data[11]


        # Первое значение выхода (по умолчанию - 0)
        await var_pressure1.write_value(float(data[0]))
        print(data[0])

        while True:
            u1,u2,u3 = await var_upr1.get_value(), await var_upr2.get_value(), await var_upr3.get_value()
            persentage_open = [u1, u2, u3]

            data = main(P_resevoir, w_out,T_init, density_liquid_20, z, mu)

            P_resevoir = data[0]
            w_out = data[1]
            x_out = data[2]
            y_out = data[3]
            d_fluid = data[4]
            d_gas = data[5]
            d_cm = data[6]
            F_in = data[7]
            F_gas_out = data[8]
            F_oil_out = data[9]
            level = data[10]
            mu = data[11]   
            d_fld_comp = data[12]

            await var_pressure1.write_value(round(float(data[0])/1000, 2))
            await var_molar1.write_value(round(float(data[1]), 2))
            await var_flow_mix_in1.write_value(round(float(data[7]), 2))
            await var_flow_gas_out1.write_value(round(float(data[8]), 2))
            await var_flow_liq_out1.write_value(round(float(data[9]), 2))
            await var_liq_level1.write_value(round(float(data[10]), 2))

            time.sleep(0.2)
            print()
            print(f"Setting value of var_pressure1 to {data[0]} ...")
            print(f"Setting value of var_molar1 to {data[1]} ...")
            print()


if __name__ == "__main__":
    asyncio.run(main())