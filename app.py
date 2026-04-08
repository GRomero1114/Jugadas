import streamlit as st
import pandas as pd

st.set_page_config(page_title="Super Quiniela Pro", layout="wide")

st.title("🏆 Verificador de Quiniela Pro")
st.markdown("Configura los partidos, asigna puntos y evalúa múltiples predicciones a la vez.")

# --- SECCIÓN 1: CONFIGURACIÓN DE PARTIDOS ---
st.header("1. Configuración de la Jornada")
num_partidos = st.number_input("¿Cuántos partidos hay?", min_value=1, max_value=20, value=3)

col_config, col_puntos = st.columns([3, 1])

nombres_partidos = []
puntos_partidos = []

with col_config:
    st.subheader("Nombres de los Cruces")
    for i in range(num_partidos):
        nombre = st.text_input(f"Partido {i+1}", f"Equipo A vs Equipo B {i+1}", key=f"n_{i}")
        nombres_partidos.append(nombre)

with col_puntos:
    st.subheader("Valor (Puntos)")
    for i in range(num_partidos):
        pts = st.number_input(f"Puntos P{i+1}", min_value=1, value=10, key=f"p_{i}")
        puntos_partidos.append(pts)

# --- SECCIÓN 2: RESULTADOS REALES ---
st.divider()
st.header("2. Resultados Reales")
opciones = ["1", "X", "2", "1X", "X2"]
resultados_reales = st.multiselect("Selecciona el resultado real de cada partido (en orden):", 
                                   options=opciones, 
                                   max_selections=num_partidos,
                                   placeholder="Selecciona uno por uno...")

# Validar que se hayan ingresado todos los resultados reales
if len(resultados_reales) < num_partidos:
    st.warning(f"Por favor selecciona los {num_partidos} resultados reales arriba.")
else:
    # --- SECCIÓN 3: PREDICCIONES MÚLTIPLES ---
    st.divider()
    st.header("3. Predicciones de Participantes")
    num_personas = st.number_input("¿Cuántas personas participaron?", min_value=1, max_value=50, value=2)

    # Creamos un diccionario para armar una tabla
    data = {"Participante": [f"Persona {i+1}" for i in range(num_personas)]}
    for nombre in nombres_partidos:
        data[nombre] = ["1"] * num_personas

    df_predicciones = pd.DataFrame(data)
    
    st.subheader("Edita las predicciones en la tabla:")
    # El editor de datos permite que el usuario cambie los valores como en Excel
    edited_df = st.data_editor(df_predicciones, use_container_width=True, num_rows="fixed")

    if st.button("🚀 Calcular Ganadores"):
        st.header("📊 Tabla de Resultados Finales")
        
        filas_finales = []
        
        for index, row in edited_df.iterrows():
            aciertos = 0
            puntos_acumulados = 0
            total_posible = sum(puntos_partidos)
            
            # Comparar cada predicción con el resultado real
            for i in range(num_partidos):
                prediccion = row[nombres_partidos[i]]
                real = resultados_reales[i]
                
                if prediccion == real:
                    aciertos += 1
                    puntos_acumulados += puntos_partidos[i]
            
            # Lógica de "Gana todo o nada"
            gano_todo = aciertos == num_partidos
            puntaje_final = total_posible if gano_todo else 0
            estado = "✅ ¡GANÓ!" if gano_todo else "❌ Perdió"
            
            filas_finales.append({
                "Participante": row["Participante"],
                "Aciertos": f"{aciertos}/{num_partidos}",
                "Estado": estado,
                "Puntaje Total": puntaje_final
            })
        
        res_df = pd.DataFrame(filas_finales)
        st.table(res_df)

        # Mostrar confeti si alguien ganó
        if any("GANÓ" in e for e in res_df["Estado"]):
            st.balloons()
            st.success("¡Tenemos ganadores que acertaron el 100%!")
