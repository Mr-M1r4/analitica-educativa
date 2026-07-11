"""
Módulo de análisis estadístico y métricas educativas
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def metricas_generales(df_estudiantes: pd.DataFrame, df_academico: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula métricas generales de la institución.
    
    Args:
        df_estudiantes: DataFrame de estudiantes
        df_academico: DataFrame de rendimiento académico
    
    Returns:
        Diccionario con métricas clave
    """
    total_estudiantes = len(df_estudiantes)
    total_asignaturas = df_academico["nombre_asignatura"].nunique() if "nombre_asignatura" in df_academico.columns else df_academico.shape[1]
    tasa_aprobacion = (df_academico["aprobado"].sum() / len(df_academico) * 100).round(2) if "aprobado" in df_academico.columns else 0
    tasa_desercion = (df_academico["deserto"].sum() / len(df_academico) * 100).round(2) if "deserto" in df_academico.columns else 0
    promedio_general = df_academico["calificacion"].mean().round(2) if "calificacion" in df_academico.columns else 0
    
    return {
        "total_estudiantes": total_estudiantes,
        "total_asignaturas": total_asignaturas,
        "tasa_aprobacion": tasa_aprobacion,
        "tasa_desercion": tasa_desercion,
        "promedio_general": promedio_general,
    }


def analizar_desercion(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Análisis completo de deserción estudiantil.
    
    Args:
        df: DataFrame con datos académicos y demográficos
    
    Returns:
        Diccionario con diferentes análisis de deserción
    """
    resultados = {}
    
    # Deserción por género
    resultados["por_genero"] = df.groupby("genero").agg({
        "deserto": ["sum", "mean", "count"]
    }).round(4)
    resultados["por_genero"].columns = ["total_desertores", "tasa_desercion", "total_estudiantes"]
    
    # Deserción por semestre
    resultados["por_semestre"] = df.groupby("semestre").agg({
        "deserto": ["sum", "mean"]
    }).round(4)
    resultados["por_semestre"].columns = ["total_desertores", "tasa_desercion"]
    
    # Deserción por asignatura (top materias con mayor deserción)
    desertores_asignatura = df.groupby("nombre_asignatura").agg({
        "deserto": ["sum", "mean", "count"]
    }).round(4)
    desertores_asignatura.columns = ["desertores", "tasa", "inscritos"]
    resultados["por_asignatura"] = desertores_asignatura.sort_values(
        "tasa", ascending=False
    ).head(10)
    
    # Deserción por rango de edad
    df["rango_edad"] = pd.cut(
        df["edad"],
        bins=[0, 18, 22, 25, 100],
        labels=["<18", "18-22", "23-25", ">25"]
    )
    resultados["por_edad"] = df.groupby("rango_edad", observed=True).agg({
        "deserto": ["sum", "mean", "count"]
    }).round(4)
    resultados["por_edad"].columns = ["desertores", "tasa_desercion", "total"]
    
    return resultados


def analizar_rendimiento(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Análisis de rendimiento académico.
    
    Args:
        df: DataFrame con datos académicos
    
    Returns:
        Diccionario con análisis de rendimiento
    """
    resultados = {}
    
    # Rendimiento por asignatura
    resultados["por_asignatura"] = df.groupby("nombre_asignatura").agg({
        "calificacion": ["mean", "median", "std", "min", "max", "count"]
    }).round(2)
    resultados["por_asignatura"].columns = [
        "promedio", "mediana", "desviacion", "min", "max", "n_alumnos"
    ]
    
    # Distribución de calificaciones
    resultados["distribucion"] = pd.cut(
        df["calificacion"],
        bins=[0, 60, 70, 80, 90, 100],
        labels=["<60", "60-70", "70-80", "80-90", "90-100"]
    ).value_counts().sort_index()
    
    # Top estudiantes con mejor rendimiento
    rendimiento_estudiantes = df.groupby("id_estudiante").agg({
        "calificacion": ["mean", "count"],
        "aprobado": "sum"
    }).round(2)
    rendimiento_estudiantes.columns = ["promedio", "asignaturas_cursadas", "asignaturas_aprobadas"]
    rendimiento_estudiantes["tasa_aprobacion"] = (
        rendimiento_estudiantes["asignaturas_aprobadas"] / 
        rendimiento_estudiantes["asignaturas_cursadas"] * 100
    ).round(2)
    resultados["mejores_estudiantes"] = rendimiento_estudiantes.sort_values(
        "promedio", ascending=False
    ).head(20)
    
    return resultados


def analizar_demanda_asignaturas(df_demanda: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Análisis de demanda de asignaturas.
    
    Args:
        df_demanda: DataFrame con datos de demanda
    
    Returns:
        Diccionario con análisis de demanda
    """
    resultados = {}
    
    # Asignaturas con mayor demanda
    resultados["mayor_demanda"] = df_demanda.groupby("nombre_asignatura").agg({
        "demanda": "sum",
        "inscritos": "sum",
        "cupos_disponibles": "sum"
    }).sort_values("demanda", ascending=False).head(10)
    
    # Tasa de ocupación
    resultados["ocupacion"] = df_demanda.copy()
    resultados["ocupacion"]["tasa_ocupacion"] = (
        resultados["ocupacion"]["inscritos"] / 
        resultados["ocupacion"]["cupos_disponibles"] * 100
    ).round(2)
    
    # Asignaturas subutilizadas (baja demanda)
    resultados["baja_demanda"] = df_demanda.groupby("nombre_asignatura").agg({
        "demanda": "mean",
        "inscritos": "mean"
    }).sort_values("demanda", ascending=True).head(10)
    
    return resultados


def generar_recomendaciones(
    metricas: Dict[str, Any],
    desercion: Dict[str, pd.DataFrame],
    demanda: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Genera recomendaciones basadas en el análisis.
    
    Args:
        metricas: Métricas generales
        desercion: Análisis de deserción
        demanda: Análisis de demanda
    
    Returns:
        DataFrame con recomendaciones
    """
    recomendaciones = []
    
    # Recomendaciones basadas en deserción
    if desercion["por_genero"]["tasa_desercion"].max() > 0.2:
        recomendaciones.append({
            "area": "Deserción",
            "hallazgo": "Alta tasa de deserción en un género específico",
            "accion": "Implementar programas de apoyo y mentoría",
            "prioridad": "Alta"
        })
    
    # Recomendaciones basadas en demanda
    if not demanda["baja_demanda"].empty:
        top_baja = demanda["baja_demanda"].index[0]
        recomendaciones.append({
            "area": "Oferta Académica",
            "hallazgo": f"Baja demanda en asignatura: {top_baja}",
            "accion": "Revisar plan de estudios o fusionar secciones",
            "prioridad": "Media"
        })
    
    return pd.DataFrame(recomendaciones)
