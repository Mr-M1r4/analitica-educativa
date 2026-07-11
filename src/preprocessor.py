"""
Módulo de preprocesamiento de datos
"""
import pandas as pd
import numpy as np
from typing import Tuple, List


def analizar_calidad_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analiza la calidad del dataset: nulos, duplicados, tipos.
    
    Args:
        df: DataFrame a analizar
    
    Returns:
        DataFrame con resumen de calidad
    """
    resumen = pd.DataFrame({
        "columna": df.columns,
        "tipo": df.dtypes.values,
        "nulos": df.isnull().sum().values,
        "pct_nulos": (df.isnull().sum() / len(df) * 100).round(2).values,
        "unicos": df.nunique().values,
        "ejemplo": [df[col].dropna().iloc[0] if not df[col].dropna().empty else None 
                    for col in df.columns]
    })
    return resumen


def tratar_valores_nulos(
    df: pd.DataFrame,
    estrategia: str = "auto"
) -> pd.DataFrame:
    """
    Trata valores nulos según la estrategia especificada.
    
    Args:
        df: DataFrame con valores nulos
        estrategia: "auto", "eliminar", "media", "mediana", "moda"
    
    Returns:
        DataFrame sin valores nulos
    """
    df_limpio = df.copy()
    
    if estrategia == "eliminar":
        df_limpio = df_limpio.dropna()
    
    elif estrategia == "auto":
        for col in df_limpio.columns:
            if df_limpio[col].isnull().sum() > 0:
                if df_limpio[col].dtype in ["int64", "float64"]:
                    df_limpio[col].fillna(df_limpio[col].median(), inplace=True)
                else:
                    df_limpio[col].fillna(df_limpio[col].mode()[0], inplace=True)
    
    elif estrategia in ["media", "mediana", "moda"]:
        for col in df_limpio.select_dtypes(include=[np.number]).columns:
            if estrategia == "media":
                df_limpio[col].fillna(df_limpio[col].mean(), inplace=True)
            elif estrategia == "mediana":
                df_limpio[col].fillna(df_limpio[col].median(), inplace=True)
            elif estrategia == "moda":
                df_limpio[col].fillna(df_limpio[col].mode()[0], inplace=True)
    
    nulos_originales = df.isnull().sum().sum()
    nulos_finales = df_limpio.isnull().sum().sum()
    print(f"Nulos eliminados: {nulos_originales} -> {nulos_finales}")
    
    return df_limpio


def detectar_outliers(
    df: pd.DataFrame,
    columna: str,
    metodo: str = "iqr"
) -> pd.DataFrame:
    """
    Detecta valores atípicos en una columna.
    
    Args:
        df: DataFrame
        columna: Nombre de la columna a analizar
        metodo: "iqr" o "zscore"
    
    Returns:
        DataFrame con máscara de outliers
    """
    if metodo == "iqr":
        Q1 = df[columna].quantile(0.25)
        Q3 = df[columna].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        mask = (df[columna] < limite_inferior) | (df[columna] > limite_superior)
    
    elif metodo == "zscore":
        from scipy import stats
        z_scores = np.abs(stats.zscore(df[columna].dropna()))
        mask = z_scores > 3
    
    outliers = df[mask]
    print(f"Outliers detectados en '{columna}': {len(outliers)} registros")
    
    return outliers


def calcular_tasa_desercion(
    df: pd.DataFrame,
    columna_estado: str = "deserto"
) -> pd.Series:
    """
    Calcula la tasa de deserción por grupo.
    
    Args:
        df: DataFrame con datos académicos
        columna_estado: Columna que indica deserción
    
    Returns:
        Series con tasas de deserción
    """
    tasa = df.groupby(columna_estado).size() / len(df) * 100
    return tasa.round(2)


def calcular_tasa_aprobacion(
    df: pd.DataFrame,
    columna_aprobado: str = "aprobado"
) -> float:
    """
    Calcula la tasa general de aprobación.
    
    Args:
        df: DataFrame con datos académicos
        columna_aprobado: Columna que indica aprobación
    
    Returns:
        Porcentaje de aprobación
    """
    total = len(df)
    aprobados = df[columna_aprobado].sum()
    tasa = (aprobados / total) * 100
    return round(tasa, 2)


def agrupar_por_periodo(
    df: pd.DataFrame,
    columna_fecha: str = "semestre",
    columna_valor: str = "calificacion"
) -> pd.DataFrame:
    """
    Agrupa métricas por período académico.
    
    Args:
        df: DataFrame
        columna_fecha: Columna de período
        columna_valor: Columna a agrupar
    
    Returns:
        DataFrame con métricas por período
    """
    metricas = df.groupby(columna_fecha).agg({
        columna_valor: ["mean", "median", "std", "count"]
    }).round(2)
    
    metricas.columns = ["promedio", "mediana", "desviacion", "cantidad"]
    return metricas
