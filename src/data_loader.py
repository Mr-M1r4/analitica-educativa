"""
Módulo de carga de datos para el proyecto de Analítica Educativa
"""
import pandas as pd
from pathlib import Path
from typing import Optional
from .config import RAW_DATA_DIR, PROCESSED_DATA_DIR


def cargar_datos_estudiantes(
    archivo: Optional[str] = None,
    ruta: Optional[Path] = None
) -> pd.DataFrame:
    """
    Carga el dataset de estudiantes.
    
    Args:
        archivo: Nombre del archivo CSV
        ruta: Ruta específica del archivo
    
    Returns:
        DataFrame con los datos de estudiantes
    """
    if ruta:
        filepath = ruta
    elif archivo:
        filepath = RAW_DATA_DIR / archivo
    else:
        filepath = RAW_DATA_DIR / "estudiantes.csv"
    
    df = pd.read_csv(filepath)
    print(f"Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
    return df


def cargar_datos_academicos(
    archivo: Optional[str] = None,
    ruta: Optional[Path] = None
) -> pd.DataFrame:
    """
    Carga el dataset de rendimiento académico.
    
    Args:
        archivo: Nombre del archivo CSV
        ruta: Ruta específica del archivo
    
    Returns:
        DataFrame con datos académicos
    """
    if ruta:
        filepath = ruta
    elif archivo:
        filepath = RAW_DATA_DIR / archivo
    else:
        filepath = RAW_DATA_DIR / "rendimiento_academico.csv"
    
    df = pd.read_csv(filepath)
    print(f"Datos académicos cargados: {len(df)} registros")
    return df


def cargar_todos_los_datos() -> dict:
    """
    Carga todos los datasets disponibles.
    
    Returns:
        Diccionario con DataFrames
    """
    datos = {}
    
    for nombre_archivo in RAW_DATA_DIR.glob("*.csv"):
        nombre = nombre_archivo.stem
        datos[nombre] = pd.read_csv(nombre_archivo)
        print(f"  - {nombre}: {len(datos[nombre])} registros")
    
    return datos


def guardar_datos_procesados(
    df: pd.DataFrame,
    nombre: str
) -> Path:
    """
    Guarda DataFrame procesado.
    
    Args:
        df: DataFrame a guardar
        nombre: Nombre del archivo sin extensión
    
    Returns:
        Ruta del archivo guardado
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = PROCESSED_DATA_DIR / f"{nombre}.csv"
    df.to_csv(filepath, index=False)
    print(f"Datos guardados en: {filepath}")
    return filepath
