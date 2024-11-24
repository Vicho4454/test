import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

# Ruta del archivo CSV
ROOT = 'STRIKE_REPORTS.csv'

# Función para cargar datos con caché
@st.cache_data
def cargar_datos():
    return pd.read_csv(ROOT, low_memory=False)

# Función para convertir columnas de fecha y hora
def procesar_fechas_y_horas(df):
    df['INCIDENT_DATE'] = pd.to_datetime(df['INCIDENT_DATE'], errors='coerce')
    df['TIME'] = pd.to_datetime(df['TIME'], format='%H:%M', errors='coerce').dt.time
    df['TIME'] = df['TIME'].apply(lambda x: x.strftime('%H') if pd.notnull(x) else None)
    return df

# Funciones de análisis
def analisis_mensual(df):
    return df.groupby('INCIDENT_MONTH')['INDEX_NR'].count()

def analisis_anual(df):
    return df.groupby('INCIDENT_YEAR')['INDEX_NR'].count()

def analisis_hora(df):
    return df.groupby('TIME')['INDEX_NR'].count()

def analisis_por_columna(df, columna):
    return df[columna].value_counts()

# Cargar y procesar los datos
df = cargar_datos()
df = procesar_fechas_y_horas(df)

# Interfaz de usuario con Streamlit
st.title("Incidentes por colisión de aves en aeronaves")
st.subheader("En el territorio estadounidense")
st.markdown("\nBienvenido usuario, la interfaz interactiva de la página le permitirá visualizar información relevante en histogramas, tablas, mapas de ubicación y si lo requiere, descargar bases de datos sobre los incidentes, filtradas.")

# Filtros
columnas_filtros = ["FAAREGION", "STATE"]
filtros = st.multiselect("Selecciona las columnas para filtrar por esta:", options=columnas_filtros)

# Gráficos de análisis
def mostrar_grafico(df, columna, titulo, color, figsize=(18, 6)):
    fig, ax = plt.subplots(figsize=figsize)
    df.plot(kind='bar', color=color, edgecolor='black', ax=ax)
    ax.set_title(titulo)
    ax.set_xlabel(columna)
    ax.set_ylabel("Cantidad de Incidentes")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Análisis y visualización
# Análisis y gráficos por año
df_year = analisis_anual(df)
mostrar_grafico(df_year, "Año", "Número de Incidentes por Año", 'lightcoral')

# Análisis y gráficos por mes
df_month = analisis_mensual(df)
mostrar_grafico(df_month, "Mes", "Número de Incidentes por Mes", 'skyblue')

# Análisis y gráficos por hora
df_hora = analisis_hora(df)
mostrar_grafico(df_hora, "Hora del Día", "Distribución de Incidentes por Hora del Día", 'mediumseagreen')


# Análisis de incidentes por fase de vuelo
df_phase_of_flight = analisis_por_columna(df, 'PHASE_OF_FLIGHT')
mostrar_grafico(df_phase_of_flight, "Fase de Vuelo", "Número de Incidentes por Fase de Vuelo", 'cyan', figsize=(8, 4))

# Análisis de incidentes por nivel de daño
df_damage_level = analisis_por_columna(df, 'DAMAGE_LEVEL')
mostrar_grafico(df_damage_level, "Nivel de Daño", "Número de Incidentes por Nivel de Daño", 'red', figsize=(8, 4))

# Mapa interactivo con Folium
st.subheader("Mapa interactivo de incidentes")
# Verificar si existen columnas de latitud y longitud
if 'LATITUDE' in df.columns and 'LONGITUDE' in df.columns:
    # Crear el mapa centrado en un punto específico (por ejemplo, en los EE.UU.)
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)  # Coordenadas aproximadas del centro de EE. UU.

    # Añadir marcadores de incidentes
    for _, row in df.dropna(subset=['LATITUDE', 'LONGITUDE']).iterrows():
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=5,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6
        ).add_to(m)

    # Mostrar el mapa en la aplicación Streamlit
    st_folium(m, width=700, height=500)
else:
    st.warning("No se encontraron columnas de latitud y longitud en los datos.")
