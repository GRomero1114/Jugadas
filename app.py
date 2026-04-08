import streamlit as st

def main():
    st.title("🏆 Verificador de Quiniela: ¿Ganaste o Perdiste?")
    st.markdown("""
    Ingresa los resultados reales y compáralos con tus predicciones.  
    **(1)** Victoria Local | **(X)** Empate | **(2)** Victoria Visitante
    """)

    # 1. Configuración de la cantidad de partidos
    num_partidos = st.number_input("¿Cuántos cruces hubo en total?", min_value=1, max_value=20, value=5)

    st.divider()

    col1, col2 = st.columns(2)
    
    resultados_reales = []
    predicciones_usuario = []

    # 2. Entrada de datos
    with col1:
        st.subheader("Resultados Reales")
        for i in range(num_partidos):
            res = st.selectbox(f"Partido {i+1} - Real", ["1", "X", "2"], key=f"real_{i}")
            resultados_reales.append(res)

    with col2:
        st.subheader("Tus Predicciones")
        for i in range(num_partidos):
            pred = st.selectbox(f"Partido {i+1} - Tu apuesta", ["1", "X", "2"], key=f"pred_{i}")
            predicciones_usuario.append(pred)

    # 3. Lógica de validación
    st.divider()
    if st.button("Verificar Resultados"):
        aciertos = 0
        for r, p in zip(resultados_reales, predicciones_usuario):
            if r == p:
                aciertos += 1
        
        # Mostrar resultado final
        if aciertos == num_partidos:
            st.balloons()
            st.success(f"¡GANASTE! Acertaste los {num_partidos} resultados.")
        else:
            st.error(f"PIERDES. Acertaste {aciertos} de {num_partidos}. ¡Sigue intentando!")

if __name__ == "__main__":
    main()
