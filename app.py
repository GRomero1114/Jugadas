import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestor de Quinielas con Memoria", layout="wide")

# ARCHIVO PARA GUARDAR DATOS
DB_FILE = "datos_quiniela.csv"

def guardar_datos(df_predicciones, config_partidos):
    # Guardamos las predicciones y metadatos básicos en un CSV
    df_predicciones.to_csv(DB_FILE, index=False)
    st.sidebar.success("✅ ¡Datos guardados automáticamente!")

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return None

# --- MENÚ LATERAL ---
st.sidebar.title("Configuración y Memoria")
modo_juego = st.sidebar.radio(
    "Selecciona el Modo de Juego:",
    ("Partidos Individuales", "Por Totales de Todos")
)

if st.sidebar.button("🗑️ Borrar todo y empezar de cero"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    st.rerun()

st.title(f"🏆 Quiniela: Modo {modo_juego}")

# --- SECCIÓN 1: CONFIGURACIÓN DE CRUCES ---
st.header("1. Configuración de los Cruces")
# Intentamos cargar datos previos para pre-configurar la cantidad de partidos
df_previo = cargar_datos()
default_num = 3
if df_previo is not None:
    # Contamos columnas que no son 'Participante' ni 'Puntos en Juego'
    cols_especiales = ['Participante', 'Puntos en Juego', 'Puntos que puede ganar']
    nombres_previos = [c for c in df_previo.columns if c not in cols_especiales]
    default_num = len(nombres_previos) if nombres_previos else 3

num_partidos = st.number_input("¿Cuántos cruces hay?", min_value=1, max_value=20, value=default_num)

nombres_partidos = []
puntos_partidos = []

if modo_juego == "Partidos Individuales":
    col_n, col_p = st.columns([3, 1])
    for i in range(num_partidos):
        with col_n:
            val_n = df_previo.columns[i+1] if (df_previo is not None and i+1 < len(df_previo.columns)) else f"Cruce {i+1}"
            nombres_partidos.append(st.text_input(f"Cruce {i+1}", val_n, key=f"n_{i}"))
        with col_p:
            puntos_partidos.append(st.number_input(f"Puntos P{i+1}", min_value=1, value=10, key=f"p_{i}"))
else:
    for i in range(num_partidos):
        val_n = df_previo.columns[i+2] if (df_previo is not None and i+2 < len(df_previo.columns)) else f"Cruce {i+1}"
        nombres_partidos.append(st.text_input(f"Cruce {i+1}", val_n, key=f"n_{i}"))

# --- SECCIÓN 2: RESULTADOS REALES ---
st.divider()
st.header("2. Resultados Reales")
res_data = {"Partido": nombres_partidos, "Resultado Real": ["1"] * num_partidos}
df_res_reales = pd.DataFrame(res_data)

edit_res_reales = st.data_editor(
    df_res_reales, 
    column_config={
        "Resultado Real": st.column_config.SelectboxColumn("Resultado Real", options=["1", "X", "2"], required=True),
        "Partido": st.column_config.TextColumn(disabled=True)
    },
    hide_index=True, key="editor_reales"
)
resultados_reales = edit_res_reales["Resultado Real"].tolist()

# --- SECCIÓN 3: PREDICCIONES ---
st.divider()
st.header("3. Participantes y Predicciones")
st.info("La tabla se guarda automáticamente al editar las celdas y hacer clic fuera.")

if df_previo is not None:
    df_para_editar = df_previo
else:
    # Crear estructura inicial si no hay archivo
    num_personas = 4
    data = {"Participante": [f"Jugador {i+1}" for i in range(num_personas)]}
    if modo_juego == "Por Totales de Todos":
        data["Puntos en Juego"] = [0] * num_personas
    for nombre in nombres_partidos:
        data[nombre] = ["1"] * num_personas
    df_para_editar = pd.DataFrame(data)

# Mostramos el editor
edited_df = st.data_editor(df_para_editar, use_container_width=True, key="main_editor")

# Guardar automáticamente cada vez que hay un cambio en el editor
if st.sidebar.button("💾 Guardar Cambios"):
    guardar_datos(edited_df, nombres_partidos)

# --- SECCIÓN 4: CÁLCULO FINAL ---
if st.button("🚀 Calcular Resultados Finales"):
    st.divider()
    # (Misma lógica de cálculo anterior...)
    filas_finales = []
    suma_puntos_totales = 0
    
    for index, row in edited_df.iterrows():
        aciertos = 0
        for i in range(num_partidos):
            nombre_p = nombres_partidos[i]
            pred = str(row[nombre_p]).strip().upper()
            real = str(resultados_reales[i]).strip().upper()
            
            acierto_valido = False
            if pred == "0": acierto_valido = True
            elif pred == "1X": acierto_valido = real in ["1", "X"]
            elif pred == "X2": acierto_valido = real in ["X", "2"]
            elif pred == "12": acierto_valido = real in ["1", "2"]
            else: acierto_valido = (pred == real)
            
            if acierto_valido: aciertos += 1
        
        todo_acertado = (aciertos == num_partidos)
        puntos_col = "Puntos en Juego" if modo_juego == "Por Totales de Todos" else None
        puntos_asignados = (row[puntos_col] if puntos_col else sum(puntos_partidos)) if todo_acertado else 0
        
        if todo_acertado: suma_puntos_totales += puntos_asignados
        
        filas_finales.append({
            "Participante": row["Participante"],
            "Aciertos": f"{aciertos}/{num_partidos}",
            "Estado": "✅ GANÓ" if todo_acertado else "❌ PIERDE",
            "Puntaje": puntos_asignados
        })

    st.table(pd.DataFrame(filas_finales))
    st.metric(label="TOTAL DE PUNTOS DE GANADORES", value=f"{suma_puntos_totales} pts")
    if suma_puntos_totales > 0: st.balloons()
