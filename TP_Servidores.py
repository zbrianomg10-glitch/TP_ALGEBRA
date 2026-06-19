
import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint

st.set_page_config(
    page_title="Optimizador de Servidores",
    layout="wide"
)

st.title("🌎 Optimización Global de Servidores")

st.markdown("""
Esta aplicación determina la mejor distribución de servidores
entre América, Europa y Asia maximizando el rendimiento total.
""")

# =========================
# ENTRADAS
# =========================

col1, col2 = st.columns(2)

with col1:
    cant_servidores = st.number_input(
        "Cantidad total de servidores",
        min_value=1,
        value=100
    )

    presupuesto = st.number_input(
        "Presupuesto máximo (USD)",
        min_value=10000,
        value=200000,
        step=10000
    )

with col2:
    latencia_max = st.number_input(
        "Latencia máxima",
        min_value=1000,
        value=3500,
        step=100
    )

    capacidad_min = st.number_input(
        "Capacidad mínima de red",
        min_value=1000,
        value=9000,
        step=100
    )

confiabilidad_min = st.number_input(
    "Confiabilidad mínima",
    min_value=1000,
    value=8500,
    step=100
)

# =========================
# DATOS DEL PROBLEMA
# =========================

paises = [
    "Estados Unidos",
    "Brasil",
    "Canadá",
    "Alemania",
    "Francia",
    "Países Bajos",
    "Japón",
    "Singapur",
    "India"
]

rendimiento = [120,80,110,140,130,145,135,115,70]

costos = [
    2400,1660,2080,
    2620,2510,2290,
    2400,2020,1220
]

latencias = [
    20,45,25,
    18,20,15,
    22,28,60
]

capacidad_red = [
    100,50,80,
    120,100,130,
    110,90,40
]

confiabilidad = [
    95,75,90,
    97,94,98,
    96,92,65
]

if st.button("Resolver"):

    c = [-x for x in rendimiento]

    A = [
        [1,1,1,1,1,1,1,1,1],
        costos,
        [1,1,1,0,0,0,0,0,0],
        [0,0,0,1,1,1,0,0,0],
        [0,0,0,0,0,0,1,1,1],
        latencias,
        capacidad_red,
        confiabilidad
    ]

    bl = [
        cant_servidores,
        0,
        20,
        20,
        20,
        -np.inf,
        capacidad_min,
        confiabilidad_min
    ]

    bu = [
        cant_servidores,
        presupuesto,
        np.inf,
        np.inf,
        np.inf,
        latencia_max,
        np.inf,
        np.inf
    ]

    constraints = LinearConstraint(A, bl, bu)

    bounds = Bounds(
        [0]*9,
        [np.inf]*9
    )

    res = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=np.ones(9, dtype=int)
    )

    # =========================
    # SOLUCIÓN
    # =========================

    if res.success:

        st.success("Se encontró una solución óptima")

        asignacion = np.round(res.x).astype(int)

        df = pd.DataFrame({
            "País": paises,
            "Servidores": asignacion
        })

        st.subheader("Distribución óptima")
        st.dataframe(df, use_container_width=True)

        st.subheader("Gráfico")

        grafico = df.set_index("País")
        st.bar_chart(grafico)

        costo_total = np.dot(asignacion, costos)
        capacidad_total = np.dot(asignacion, capacidad_red)
        latencia_total = np.dot(asignacion, latencias)
        confiabilidad_total = np.dot(asignacion, confiabilidad)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Rendimiento",
            round(-res.fun,2)
        )

        col2.metric(
            "Costo Total",
            f"${costo_total:,.0f}"
        )

        col3.metric(
            "Latencia",
            round(latencia_total,2)
        )

        col4.metric(
            "Confiabilidad",
            round(confiabilidad_total,2)
        )

    else:

        st.error("❌ No existe una solución factible")

        st.write("### Restricciones ingresadas")

        st.write(f"Cantidad servidores: {cant_servidores}")
        st.write(f"Presupuesto: ${presupuesto:,.0f}")
        st.write(f"Latencia máxima: {latencia_max}")
        st.write(f"Capacidad mínima: {capacidad_min}")
        st.write(f"Confiabilidad mínima: {confiabilidad_min}")

        costo_minimo_teorico = cant_servidores * min(costos)

        st.write("### Diagnóstico")

        if presupuesto < costo_minimo_teorico:
            st.warning(
                f"El presupuesto es demasiado bajo.\n\n"
                f"Para {cant_servidores} servidores "
                f"se requieren al menos "
                f"${costo_minimo_teorico:,.0f}"
            )

        else:
            st.warning(
                "Las restricciones combinadas "
                "de latencia, capacidad o confiabilidad "
                "impiden encontrar una solución."
            )

        st.info(
            "Probá aumentando el presupuesto, "
            "la latencia máxima o reduciendo "
            "las exigencias de capacidad y confiabilidad."
        )
