"""
Dashboard de Analítica Educativa
Ejecutar con: streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.analyzer import (
    metricas_generales,
    analizar_desercion,
    analizar_rendimiento,
    generar_recomendaciones
)
from src.visualizer import (
    graficar_tasa_desercion,
    graficar_rendimiento_asignaturas,
    graficar_evolucion_temporal,
    graficar_distribucion_calificaciones
)

st.set_page_config(page_title="Analítica Educativa", page_icon="🎓", layout="wide")
st.title("🎓 Panel de Analítica Educativa")
st.markdown("---")

@st.cache_data
def cargar_datos_demo():
    np.random.seed(42)
    n_estudiantes = 500
    n_registros = 2000
    asignaturas = ['Matemáticas', 'Física', 'Química', 'Programación', 'Base de Datos', 'Redes']
    
    df_estudiantes = pd.DataFrame({
        'id_estudiante': range(1, n_estudiantes + 1),
        'genero': np.random.choice(['M', 'F'], n_estudiantes),
        'edad': np.random.randint(16, 30, n_estudiantes),
        'estado_civil': np.random.choice(['Soltero', 'Casado'], n_estudiantes, p=[0.7, 0.3]),
        'becado': np.random.choice([True, False], n_estudiantes, p=[0.3, 0.7])
    })
    
    df_academico = pd.DataFrame({
        'id_estudiante': np.random.choice(range(1, n_estudiantes + 1), n_registros),
        'semestre': np.random.choice(['2023-1', '2023-2', '2024-1', '2024-2'], n_registros),
        'ano_academico': np.random.choice([2023, 2024], n_registros),
        'nombre_asignatura': np.random.choice(asignaturas, n_registros),
        'creditos': np.random.choice([3, 4, 5], n_registros),
        'calificacion': np.random.normal(72, 15, n_registros).clip(0, 100).round(1),
        'aprobado': np.random.choice([True, False], n_registros, p=[0.7, 0.3]),
        'deserto': np.random.choice([True, False], n_registros, p=[0.15, 0.85])
    })
    return df_estudiantes, df_academico

def main():
    df_estudiantes, df_academico = cargar_datos_demo()
    
    st.sidebar.header("Filtros")
    semestre_seleccionado = st.sidebar.selectbox("Semestre", ['Todos'] + list(df_academico['semestre'].unique()))
    asignatura_seleccionada = st.sidebar.selectbox("Asignatura", ['Todas'] + list(df_academico['nombre_asignatura'].unique()))
    
    df_filtrado = df_academico.copy()
    if semestre_seleccionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['semestre'] == semestre_seleccionado]
    if asignatura_seleccionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['nombre_asignatura'] == asignatura_seleccionada]
    
    st.header("Métricas Generales")
    col1, col2, col3, col4 = st.columns(4)
    metricas = metricas_generales(df_estudiantes, df_filtrado)
    
    with col1:
        st.metric("Total Estudiantes", f"{metricas['total_estudiantes']:,}")
    with col2:
        st.metric("Tasa de Aprobación", f"{metricas['tasa_aprobacion']}%")
    with col3:
        st.metric("Tasa de Deserción", f"{metricas['tasa_desercion']}%")
    with col4:
        st.metric("Promedio General", f"{metricas['promedio_general']}")
    
    st.markdown("---")
    st.header("Análisis de Deserción")
    
    df_completo = df_filtrado.merge(
        df_estudiantes[['id_estudiante', 'genero', 'edad', 'becado']],
        on='id_estudiante', how='left'
    )
    analisis_desercion = analizar_desercion(df_completo)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Deserción por Género")
        fig = graficar_tasa_desercion(df_completo, 'genero')
        st.pyplot(fig)
    with col2:
        st.subheader("Top Asignaturas con Mayor Deserción")
        st.dataframe(analisis_desercion['por_asignatura'])
    
    st.markdown("---")
    st.header("Rendimiento Académico")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución de Calificaciones")
        fig = graficar_distribucion_calificaciones(df_filtrado)
        st.pyplot(fig)
    with col2:
        st.subheader("Evolución por Semestre")
        fig = graficar_evolucion_temporal(df_filtrado, 'semestre', 'calificacion')
        st.pyplot(fig)
    
    st.subheader("Rendimiento por Asignatura")
    fig = graficar_rendimiento_asignaturas(df_filtrado)
    st.pyplot(fig)

if __name__ == "__main__":
    main()
