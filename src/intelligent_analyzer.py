"""
Módulo de análisis inteligente - detecta problemas y genera recomendaciones
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def detectar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta materias que funcionan como 'filtros' (mucha gente las repite o abandona).
    Retorna materias con alta tasa de reprobación Y deserción combinadas.
    """
    stats = df.groupby("nombre_asignatura").agg(
        total=("id_estudiante", "count"),
        reprobados=("calificacion", lambda x: (x < 60).sum()),
        desertores=("deserto", "sum"),
        promedio=("calificacion", "mean")
    ).reset_index()

    stats["tasa_perdida"] = ((stats["reprobados"] + stats["desertores"]) / stats["total"] * 100).round(1)
    stats["tasa_reprobacion"] = (stats["reprobados"] / stats["total"] * 100).round(1)

    # Filtrar solo materias con suficientes datos y alto impacto
    filtros = stats[stats["total"] >= 30].copy()
    filtros = filtros.sort_values("tasa_perdida", ascending=False)

    return filtros[["nombre_asignatura", "total", "reprobados", "desertores",
                     "tasa_perdida", "tasa_reprobacion", "promedio"]].head(10)


def tendencia_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula si las cosas están mejorando o empeorando por semestre.
    """
    por_semestre = df.groupby("semestre").agg(
        registros=("id_estudiante", "count"),
        promedio=("calificacion", "mean"),
        tasa_aprobacion=("aprobado", "mean"),
        tasa_desercion=("deserto", "mean")
    ).reset_index()

    por_semestre["semestre_orden"] = por_semestre["semestre"].apply(
        lambda x: int(x.split("-")[0]) * 10 + int(x.split("-")[1])
    )
    por_semestre = por_semestre.sort_values("semestre_orden")

    # Calcular tendencia (últimos 4 vs primeros 4 semestres)
    if len(por_semestre) >= 8:
        primeros = por_semestre.head(4)
        ultimos = por_semestre.tail(4)

        cambio_promedio = ultimos["promedio"].mean() - primeros["promedio"].mean()
        cambio_aprobacion = (ultimos["tasa_aprobacion"].mean() - primeros["tasa_aprobacion"].mean()) * 100
        cambio_desercion = (ultimos["tasa_desercion"].mean() - primeros["tasa_desercion"].mean()) * 100

        return por_semestre, {
            "cambio_promedio": round(cambio_promedio, 2),
            "cambio_aprobacion": round(cambio_aprobacion, 2),
            "cambio_desercion": round(cambio_desercion, 2),
            "direccion": "mejorando" if cambio_aprobacion > 0 and cambio_desercion < 0 else "empeorando"
        }

    return por_semestre, {"direccion": "datos insuficientes"}


def comparar_facultades(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compara rendimiento entre facultades con contexto.
    """
    stats = df.groupby("facultad").agg(
        registros=("id_estudiante", "count"),
        carreras=("carrera", "nunique"),
        promedio=("calificacion", "mean"),
        tasa_aprobacion=("aprobado", "mean"),
        tasa_desercion=("deserto", "mean")
    ).round(3).reset_index()

    stats["tasa_aprobacion"] = (stats["tasa_aprobacion"] * 100).round(1)
    stats["tasa_desercion"] = (stats["tasa_desercion"] * 100).round(1)

    # Promedio general para comparar
    promedio_general = stats["promedio"].mean()
    stats["vs_promedio"] = (stats["promedio"] - promedio_general).round(2)

    return stats.sort_values("promedio", ascending=False)


def comparar_carreras(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compara rendimiento entre carreras.
    """
    stats = df.groupby(["facultad", "carrera"]).agg(
        registros=("id_estudiante", "count"),
        promedio=("calificacion", "mean"),
        tasa_aprobacion=("aprobado", "mean"),
        tasa_desercion=("deserto", "mean")
    ).round(3).reset_index()

    stats["tasa_aprobacion"] = (stats["tasa_aprobacion"] * 100).round(1)
    stats["tasa_desercion"] = (stats["tasa_desercion"] * 100).round(1)

    promedio_general = df["calificacion"].mean()
    stats["vs_promedio"] = (stats["promedio"] - promedio_general).round(2)

    return stats.sort_values("promedio", ascending=False)


def detectar_crisis_por_facultad(df: pd.DataFrame) -> List[Dict]:
    """
    Detecta situaciones críticas que requieren atención inmediata.
    """
    crisis = []

    # 1. Materias con >40% de pérdida
    materias_crisis = detectar_filtros(df)
    for _, row in materias_crisis.iterrows():
        if row["tasa_perdida"] > 40:
            crisis.append({
                "tipo": "CRÍTICO",
                "area": row["nombre_asignatura"],
                "problema": f"Tasa de pérdida del {row['tasa_perdida']}%",
                "detalle": f"{row['reprobados']} reprobados + {row['desertores']} desertores de {row['total']} inscritos",
                "accion": "Revisar metodología, agregar tutoría o ajustar evaluación"
            })

    # 2. Carreras con deserción >15%
    por_carrera = df.groupby("carrera")["deserto"].mean() * 100
    carreras_crisis = por_carrera[por_carrera > 15]
    for carrera, tasa in carreras_crisis.items():
        crisis.append({
            "tipo": "ALERTA",
            "area": carrera,
            "problema": f"Deserción del {tasa:.1f}%",
            "detalle": "Superan el 15% de deserción",
            "accion": "Implementar programas de retención y acompañamiento"
        })

    # 3. Facultades con promedio <70
    por_facultad = df.groupby("facultad")["calificacion"].mean()
    facultades_bajas = por_facultad[por_facultad < 70]
    for facultad, prom in facultades_bajas.items():
        crisis.append({
            "tipo": "ADVERTENCIA",
            "area": facultad,
            "problema": f"Promedio general de {prom:.1f}",
            "detalle": "Por debajo del umbral aceptable (70)",
            "accion": "Revisar plan de estudios y nivel de exigencia"
        })

    return crisis


def generar_recomendaciones智能(df: pd.DataFrame) -> List[Dict]:
    """
    Genera recomendaciones basadas en datos, no solo filtros.
    """
    recomendaciones = []

    # Analizar tendencia
    _, tendencia = tendencia_temporal(df)
    if tendencia.get("direccion") == "empeorando":
        recomendaciones.append({
            "prioridad": "ALTA",
            "area": "Tendencia General",
            "recomendacion": "Los indicadores están empeorando. Se requiere plan de mejora integral.",
            "evidencia": f"Cambio en aprobación: {tendencia.get('cambio_aprobacion', 0):+.1f}%"
        })

    # Materias más problemáticas
    filtros = detectar_filtros(df)
    if len(filtros) > 0:
        top3 = filtros.head(3)
        nombres = ", ".join(top3["nombre_asignatura"].tolist())
        recomendaciones.append({
            "prioridad": "ALTA",
            "area": "Materias Críticas",
            "recomendacion": f"Priorizar intervención en: {nombres}",
            "evidencia": f"Tasa de pérdida promedio: {top3['tasa_perdida'].mean():.1f}%"
        })

    # Carreras con mejor/peor rendimiento
    por_carrera = comparar_carreras(df)
    mejor = por_carrera.iloc[0]
    peor = por_carrera.iloc[-1]

    recomendaciones.append({
        "prioridad": "MEDIA",
        "area": "Mejores Prácticas",
        "recomendacion": f"Replicar estrategias de {mejor['carrera']} (promedio: {mejor['promedio']:.1f})",
        "evidencia": f"Promedio general: {df['calificacion'].mean():.1f}"
    })

    if peor["promedio"] < df["calificacion"].mean() - 5:
        recomendaciones.append({
            "prioridad": "MEDIA",
            "area": "Carrera en Alerta",
            "recomendacion": f"{peor['carrera']} tiene promedio bajo ({peor['promedio']:.1f}). Revisar recursos y apoyo.",
            "evidencia": f"Diferencia con promedio: {peor['vs_promedio']:.1f} puntos"
        })

    # Análisis por género (solo si la columna existe)
    if "genero" in df.columns:
        por_genero = df.groupby("genero")["deserto"].mean() * 100
        if len(por_genero) > 1:
            diff = por_genero.max() - por_genero.min()
            if diff > 3:
                recomendaciones.append({
                    "prioridad": "MEDIA",
                    "area": "Equidad de Género",
                    "recomendacion": "Hay diferencia significativa en deserción por género. Investigar causas.",
                    "evidencia": f"Diferencia: {diff:.1f} puntos porcentuales"
                })

    return recomendaciones


def generar_alertas_automaticas(df: pd.DataFrame) -> Dict:
    """
    Genera un resumen ejecutivo con alertas automáticas.
    """
    total = len(df)
    aprobados = df["aprobado"].sum()
    desertores = df["deserto"].sum()

    alertas = {
        "resumen": {
            "total_registros": total,
            "aprobados": int(aprobados),
            "reprobados": int(total - aprobados),
            "desertores": int(desertores),
            "tasa_aprobacion": round(aprobados / total * 100, 1),
            "tasa_desercion": round(desertores / total * 100, 1),
            "promedio_general": round(df["calificacion"].mean(), 1)
        },
        "crisis": detectar_crisis_por_facultad(df),
        "recomendaciones": generar_recomendaciones智能(df),
        "filtros": detectar_filtros(df).to_dict("records"),
        "comparativa_facultades": comparar_facultades(df).to_dict("records")
    }

    return alertas
