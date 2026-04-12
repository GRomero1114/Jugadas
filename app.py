import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestor de Quinielas Pro", layout="wide")

# --- MENÚ LATERAL ---
st.sidebar.title("Configuración")
modo_juego = st.sidebar.radio(
    "Selecciona el Modo de Juego:",
    ("Partidos Individuales", "Por Totales de Todos")
)

st.title(f"🏆 Quiniela: Modo {modo_juego}")

# --- SECCIÓN 1: CONFIGURACIÓN DE CRUCES ---
st.header("1. Configuración de los Cruces")
num_partidos = st.number_input("¿Cuántos cruces hay?", min_value=1, max_value=20, value=3)

nombres_partidos = []
puntos_partidos = []

if modo_juego == "Partidos Individuales":
    col_n, col_p = st.columns([3, 1])
    for i in range(num_partidos):
        with col_n:
            nombres_partidos.append(st.text_input(f"Cruce {i+1}", f"Cruce {i+1}", key=f"n_{i}"))
        with col_p:
            puntos_partidos.append(st.number_input(f"Puntos P{i+1}", min_value=1, value=10, key=f"p_{i}"))
else:
    for i in range(num_partidos):
        nombres_partidos.append(st.text_input(f"Cruce {i+1}", f"Cruce {i+1}", key=f"n_{i}"))

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
st.info("Opciones válidas: 1, X, 2, 1X, X2, 12 y 0 (No seleccionado / Comodín)")
num_personas = st.number_input("¿Cuántas personas participan?", min_value=1, value=4)

data = {"Participante": [f"Jugador {i+1}" for i in range(num_personas)]}

if modo_juego == "Por Totales de Todos":
    data["Puntos en Juego"] = [0] * num_personas

for nombre in nombres_partidos:
    data[nombre] = ["1"] * num_personas

df_predicciones = pd.DataFrame(data)
edited_df = st.data_editor(df_predicciones, use_container_width=True)

# --- SECCIÓN 4: CÁLCULO FINAL ---
if st.button("🚀 Calcular Resultados Finales"):
    st.divider()
    filas_finales = []
    suma_puntos_totales = 0
    
    for index, row in edited_df.iterrows():
        aciertos = 0
        
        for i in range(num_partidos):
            pred = str(row[nombres_partidos[i]]).strip().upper()
            real = str(resultados_reales[i]).strip().upper()
            
            # LÓGICA DE COMPARACIÓN CON COMODÍN 0
            acierto_valido = False
            
            if pred == "0":
                acierto_valido = True  # El 0 siempre es acierto
            elif pred == "1X":
                acierto_valido = real in ["1", "X"]
            elif pred == "X2":
                acierto_valido = real in ["X", "2"]
            elif pred == "12":
                acierto_valido = real in ["1", "2"]
            else:
                acierto_valido = (pred == real)
            
            if acierto_valido:
                aciertos += 1
        
        todo_acertado = (aciertos == num_partidos)
        
        if modo_juego == "Partidos Individuales":
            puntos_asignados = sum(puntos_partidos) if todo_acertado else 0
        else:
            puntos_asignados = row["Puntos en Juego"] if todo_acertado else 0
        
        if todo_acertado:
            suma_puntos_totales += puntos_asignados
        
        filas_finales.append({
            "Participante": row["Participante"],
            "Aciertos": f"{aciertos}/{num_partidos}",
            "Estado": "✅ GANÓ" if todo_acertado else "❌ PIERDE",
            "Puntaje": puntos_asignados
        })

    st.table(pd.DataFrame(filas_finales))
    st.metric(label="TOTAL DE PUNTOS DE GANADORES", value=f"{suma_puntos_totales} pts")
    
    if suma_puntos_totales > 0:
        st.balloons()
