"""
Dashboard de Analítica Educativa - Versión Inteligente
Enfoque: Problemas, Tendencias, Decisiones
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.intelligent_analyzer import (
    generar_alertas_automaticas,
    detectar_filtros,
    tendencia_temporal,
    comparar_facultades,
    comparar_carreras,
)

st.set_page_config(page_title="Analítica Educativa", page_icon="🎓", layout="wide")

@st.cache_data
def cargar_datos():
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    df_est = pd.read_csv(data_dir / "estudiantes.csv")
    df_acad = pd.read_csv(data_dir / "rendimiento_academico.csv")
    return df_est, df_acad


def fig_barra_simple(valores, etiquetas, titulo, color="#2E86AB"):
    fig, ax = plt.subplots(figsize=(10, 4))
    barras = ax.barh(etiquetas, valores, color=color, edgecolor="white")
    ax.set_title(titulo, fontsize=13, fontweight="bold")
    ax.set_xlabel("Tasa (%)")
    for barra, val in zip(barras, valores):
        ax.text(barra.get_width() + 0.5, barra.get_y() + barra.get_height()/2,
                f"{val:.1f}%", va="center", fontsize=9)
    plt.tight_layout()
    return fig


def main():
    df_estudiantes, df_academico = cargar_datos()

    # ── Sidebar ───────────────────────────────────────────────────
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

    # Aplicar filtros
    df = df_academico.copy()
    if facultad != "Todas":
        df = df[df["facultad"] == facultad]
    if carrera != "Todas":
        df = df[df["carrera"] == carrera]
    if semestre != "Todos":
        df = df[df["semestre"] == semestre]

    ids = df["id_estudiante"].unique()
    df_est_filtrado = df_estudiantes[df_estudiantes["id_estudiante"].isin(ids)]

    # ── Título ────────────────────────────────────────────────────
    st.title("🎓 Panel Ejecutivo - Analítica Educativa")
    filtro_texto = " | ".join([f for f in [facultad, carrera, semestre] if f != "Todas" and f != "Todos"])
    if filtro_texto:
        st.caption(f"🔍 {filtro_texto}  •  {len(df):,} registros analizados")
    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # SECCIÓN 1: RESUMEN EJECUTIVO
    # ══════════════════════════════════════════════════════════════
    st.header("📊 Resumen Ejecutivo")

    alertas = generar_alertas_automaticas(df)
    res = alertas["resumen"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Estudiantes", f"{len(df_est_filtrado):,}")
    with c2:
        st.metric("Aprobación", f"{res['tasa_aprobacion']}%")
    with c3:
        st.metric("Deserción", f"{res['tasa_desercion']}%")
    with c4:
        st.metric("Promedio", f"{res['promedio_general']}")

    # Indicador de tendencia
    _, tendencia = tendencia_temporal(df)
    if tendencia.get("direccion") == "mejorando":
        st.success(f"📈 **Tendencia: Mejorando** — Aprobación subió {tendencia.get('cambio_aprobacion', 0):+.1f}% | Deserción bajó {tendencia.get('cambio_desercion', 0):+.1f}%")
    elif tendencia.get("direccion") == "empeorando":
        st.error(f"📉 **Tendencia: Empeorando** — Aprobación bajó {tendencia.get('cambio_aprobacion', 0):+.1f}% | Deserción subió {tendencia.get('cambio_desercion', 0):+.1f}%")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # SECCIÓN 2: ALERTAS AUTOMÁTICAS
    # ══════════════════════════════════════════════════════════════
    crisis = alertas["crisis"]
    if crisis:
        st.header("🚨 Alertas Detectadas")
        for i, c in enumerate(crisis[:5]):
            if c["tipo"] == "CRÍTICO":
                st.error(f"**{c['tipo']}** — {c['area']}: {c['problema']}")
            elif c["tipo"] == "ALERTA":
                st.warning(f"**{c['tipo']}** — {c['area']}: {c['problema']}")
            else:
                st.info(f"**{c['tipo']}** — {c['area']}: {c['problema']}")
            st.caption(f"   → {c['accion']}")
        st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # SECCIÓN 3: DÓNDE ESTÁ EL PROBLEMA
    # ══════════════════════════════════════════════════════════════
    st.header("🔍 Dónde Están los Problemas")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Materias con Mayor Pérdida")
        filtros = detectar_filtros(df)
        if len(filtros) > 0:
            fig = fig_barra_simple(
                filtros["tasa_perdida"].head(8).values,
                filtros["nombre_asignatura"].head(8).values,
                "Top 8 Materias Más Perdidas (Reprobados + Desertores)",
                color="#C73E1D"
            )
            st.pyplot(fig)
            plt.close()

    with col2:
        st.subheader("Comparación entre Facultades")
        facultades_comp = comparar_facultades(df)
        if len(facultades_comp) > 1:
            fig = fig_barra_simple(
                facultades_comp["promedio"].values,
                facultades_comp["facultad"].values,
                "Promedio por Facultad (Línea: Promedio General)",
                color="#2E86AB"
            )
            promedio_gen = df["calificacion"].mean()
            ax = fig.axes[0]
            ax.axvline(x=promedio_gen, color="#F18F01", linestyle="--", linewidth=2, label=f"General: {promedio_gen:.1f}")
            ax.legend()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("Selecciona 'Todas' las facultades para comparar")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # SECCIÓN 4: CÓMO EVOLUCIONA
    # ══════════════════════════════════════════════════════════════
    st.header("📈 Cómo Evoluciona")

    por_semestre, _ = tendencia_temporal(df)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4))

    axes[0].plot(por_semestre["semestre"], por_semestre["tasa_aprobacion"] * 100,
                 marker="o", color="#2E86AB", linewidth=2)
    axes[0].set_title("Tasa de Aprobación por Semestre", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("%")
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(por_semestre["semestre"], por_semestre["tasa_desercion"] * 100,
                 marker="o", color="#C73E1D", linewidth=2)
    axes[1].set_title("Tasa de Deserción por Semestre", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("%")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # SECCIÓN 5: RANKING DE CARRERAS
    # ══════════════════════════════════════════════════════════════
    st.header("🏆 Ranking de Carreras")

    carreras_comp = comparar_carreras(df)
    if facultad == "Todas":
        carreras_comp = carreras_comp[["facultad", "carrera", "registros", "promedio",
                                        "tasa_aprobacion", "tasa_desercion", "vs_promedio"]]
    else:
        carreras_comp = carreras_comp[["carrera", "registros", "promedio",
                                        "tasa_aprobacion", "tasa_desercion", "vs_promedio"]]

    # Resaltar columnas clave
    st.dataframe(
        carreras_comp.style.applymap(
            lambda v: "color: green" if isinstance(v, (int, float)) and v > 0 else "color: red" if isinstance(v, (int, float)) and v < 0 else "",
            subset=["vs_promedio"]
        ),
        use_container_width=True,
        height=400
    )

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # SECCIÓN 6: RECOMENDACIONES
    # ══════════════════════════════════════════════════════════════
    st.header("💡 Recomendaciones")

    for rec in alertas["recomendaciones"]:
        prioridad = rec["prioridad"]
        if prioridad == "ALTA":
            st.error(f"**[{prioridad}]** {rec['recomendacion']}")
        else:
            st.warning(f"**[{prioridad}]** {rec['recomendacion']}")
        st.caption(f"   Evidencia: {rec['evidencia']}")

    # ══════════════════════════════════════════════════════════════
    # SECCIÓN 7: DETALLE POR ASIGNATURA (expandible)
    # ══════════════════════════════════════════════════════════════
    with st.expander("📋 Ver detalle completo de todas las asignaturas"):
        stats_asig = df.groupby("nombre_asignatura").agg(
            inscritos=("id_estudiante", "count"),
            promedio=("calificacion", "mean"),
            reprobados=("calificacion", lambda x: (x < 60).sum()),
            desertores=("deserto", "sum")
        ).round(2)
        stats_asig["tasa_perdida"] = ((stats_asig["reprobados"] + stats_asig["desertores"]) / stats_asig["inscritos"] * 100).round(1)
        stats_asig = stats_asig.sort_values("tasa_perdida", ascending=False)
        st.dataframe(stats_asig, use_container_width=True, height=500)


if __name__ == "__main__":
    main()
