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
)
from src.visualizer import (
    graficar_tasa_desercion,
    graficar_rendimiento_asignaturas,
    graficar_evolucion_temporal,
    graficar_distribucion_calificaciones
)

st.set_page_config(page_title="Analítica Educativa", page_icon="🎓", layout="wide")

@st.cache_data
def cargar_datos():
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    df_estudiantes = pd.read_csv(data_dir / "estudiantes.csv")
    df_academico = pd.read_csv(data_dir / "rendimiento_academico.csv")
    df_asignaturas = pd.read_csv(data_dir / "asignaturas.csv")
    return df_estudiantes, df_academico, df_asignaturas

def main():
    df_estudiantes, df_academico, df_asignaturas = cargar_datos()

    # ── Sidebar: filtros ──────────────────────────────────────────
    st.sidebar.title("🎓 Filtros")

    facultades = sorted(df_academico["facultad"].unique())
    facultad = st.sidebar.selectbox("Facultad", ["Todas"] + facultades)

    if facultad != "Todas":
        carreras = sorted(df_academico[df_academico["facultad"] == facultad]["carrera"].unique())
    else:
        carreras = sorted(df_academico["carrera"].unique())
    carrera = st.sidebar.selectbox("Carrera", ["Todas"] + carreras)

    if carrera != "Todas":
        semestres = sorted(df_academico[df_academico["carrera"] == carrera]["semestre"].unique(),
                           key=lambda x: (int(x.split("-")[0]), int(x.split("-")[1])))
    else:
        semestres = sorted(df_academico["semestre"].unique(),
                           key=lambda x: (int(x.split("-")[0]), int(x.split("-")[1])))
    semestre = st.sidebar.selectbox("Semestre", ["Todos"] + semestres)

    if carrera != "Todas":
        asignaturas = sorted(df_academico[df_academico["carrera"] == carrera]["nombre_asignatura"].unique())
    else:
        asignaturas = sorted(df_academico["nombre_asignatura"].unique())
    asignatura = st.sidebar.selectbox("Asignatura", ["Todas"] + asignaturas)

    # ── Aplicar filtros ───────────────────────────────────────────
    df_filtrado = df_academico.copy()
    if facultad != "Todas":
        df_filtrado = df_filtrado[df_filtrado["facultad"] == facultad]
    if carrera != "Todas":
        df_filtrado = df_filtrado[df_filtrado["carrera"] == carrera]
    if semestre != "Todos":
        df_filtrado = df_filtrado[df_filtrado["semestre"] == semestre]
    if asignatura != "Todas":
        df_filtrado = df_filtrado[df_filtrado["nombre_asignatura"] == asignatura]

    # Filtro de estudiantes consistente
    ids_filtrados = df_filtrado["id_estudiante"].unique()
    df_est_filtrado = df_estudiantes[df_estudiantes["id_estudiante"].isin(ids_filtrados)]

    # ── Título ────────────────────────────────────────────────────
    st.title("🎓 Panel de Analítica Educativa")
    filtros_activos = []
    if facultad != "Todas": filtros_activos.append(facultad)
    if carrera != "Todas": filtros_activos.append(carrera)
    if semestre != "Todos": filtros_activos.append(semestre)
    if asignatura != "Todas": filtros_activos.append(asignatura)
    if filtros_activos:
        st.caption(f"Filtros: {' → '.join(filtros_activos)}  |  {len(df_filtrado):,} registros")
    st.markdown("---")

    # ── Métricas generales ────────────────────────────────────────
    st.header("📊 Métricas Generales")
    metricas = metricas_generales(df_est_filtrado, df_filtrado)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Estudiantes", f"{metricas['total_estudiantes']:,}")
    with c2:
        st.metric("Asignaturas", f"{metricas['total_asignaturas']}")
    with c3:
        st.metric("Aprobación", f"{metricas['tasa_aprobacion']}%")
    with c4:
        st.metric("Deserción", f"{metricas['tasa_desercion']}%")
    with c5:
        st.metric("Promedio", f"{metricas['promedio_general']}")

    st.markdown("---")

    # ── Deserción ─────────────────────────────────────────────────
    st.header("📉 Análisis de Deserción")

    df_completo = df_filtrado.merge(
        df_est_filtrado[["id_estudiante", "genero", "edad", "becado"]],
        on="id_estudiante", how="left"
    )
    analisis_desercion = analizar_desercion(df_completo)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Deserción por Género")
        fig = graficar_tasa_desercion(df_completo, "genero")
        st.pyplot(fig)
    with c2:
        st.subheader("Top Asignaturas con Mayor Deserción")
        st.dataframe(analisis_desercion["por_asignatura"], use_container_width=True)

    st.markdown("---")

    # ── Rendimiento académico ─────────────────────────────────────
    st.header("📈 Rendimiento Académico")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribución de Calificaciones")
        fig = graficar_distribucion_calificaciones(df_filtrado)
        st.pyplot(fig)
    with c2:
        st.subheader("Evolución por Semestre")
        fig = graficar_evolucion_temporal(df_filtrado, "semestre", "calificacion")
        st.pyplot(fig)

    st.subheader("Rendimiento por Asignatura")
    fig = graficar_rendimiento_asignaturas(df_filtrado)
    st.pyplot(fig)

    # ── Tabla resumen por carrera ─────────────────────────────────
    if facultad != "Todas" and carrera == "Todas":
        st.markdown("---")
        st.header("📋 Resumen por Carrera")
        resumen = df_filtrado.groupby("carrera").agg(
            registros=("id_estudiante", "count"),
            promedio=("calificacion", "mean"),
            aprobados=("aprobado", "sum"),
            desertores=("deserto", "sum")
        ).round(2)
        resumen["tasa_aprobacion"] = (resumen["aprobados"] / resumen["registros"] * 100).round(1)
        resumen["tasa_desercion"] = (resumen["desertores"] / resumen["registros"] * 100).round(1)
        resumen = resumen.sort_values("registros", ascending=False)
        st.dataframe(resumen, use_container_width=True)

    # ── Tabla resumen por facultad ────────────────────────────────
    if facultad == "Todas":
        st.markdown("---")
        st.header("📋 Resumen por Facultad")
        resumen = df_filtrado.groupby("facultad").agg(
            registros=("id_estudiante", "count"),
            carreras=("carrera", "nunique"),
            promedio=("calificacion", "mean"),
            aprobados=("aprobado", "sum"),
            desertores=("deserto", "sum")
        ).round(2)
        resumen["tasa_aprobacion"] = (resumen["aprobados"] / resumen["registros"] * 100).round(1)
        resumen["tasa_desercion"] = (resumen["desertores"] / resumen["registros"] * 100).round(1)
        resumen = resumen.sort_values("registros", ascending=False)
        st.dataframe(resumen, use_container_width=True)

if __name__ == "__main__":
    main()
