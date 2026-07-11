"""
Módulo de visualizaciones para el proyecto de Analítica Educativa
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional
from .config import COLORES, ESTILO_GRAFICO


def configurar_estilo():
    """Configura el estilo de las gráficas."""
    plt.rcParams.update(ESTILO_GRAFICO)
    sns.set_palette([COLORES["primario"], COLORES["secundario"], COLORES["acento"]])
    sns.set_style("whitegrid")


def graficar_tasa_desercion(
    df: pd.DataFrame,
    columna_grupo: str = "genero",
    titulo: Optional[str] = None,
    guardar: bool = False,
    ruta: Optional[str] = None
) -> plt.Figure:
    """
    Gráfica de barras con tasa de deserción por grupo.
    
    Args:
        df: DataFrame con datos
        columna_grupo: Columna para agrupar
        titulo: Título de la gráfica
        guardar: Si True, guarda la imagen
        ruta: Ruta para guardar
    
    Returns:
        Figura de matplotlib
    """
    configurar_estilo()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    datos = df.groupby(columna_grupo)["deserto"].mean() * 100
    datos = datos.sort_values(ascending=False)
    
    bars = ax.bar(datos.index, datos.values, color=[COLORES["primario"], COLORES["secundario"]])
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    ax.set_title(titulo or f"Tasa de Deserción por {columna_grupo.title()}")
    ax.set_xlabel(columna_grupo.title())
    ax.set_ylabel("Tasa de Deserción (%)")
    
    if guardar and ruta:
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
    
    return fig


def graficar_rendimiento_asignaturas(
    df: pd.DataFrame,
    top_n: int = 10,
    titulo: Optional[str] = None,
    guardar: bool = False,
    ruta: Optional[str] = None
) -> plt.Figure:
    """
    Gráfica de rendimiento por asignatura.
    
    Args:
        df: DataFrame con datos académicos
        top_n: Número de asignaturas a mostrar
        titulo: Título de la gráfica
        guardar: Si True, guarda la imagen
        ruta: Ruta para guardar
    
    Returns:
        Figura de matplotlib
    """
    configurar_estilo()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    rendimiento = df.groupby("nombre_asignatura")["calificacion"].mean()
    rendimiento = rendimiento.sort_values(ascending=True).tail(top_n)
    
    colors = [COLORES["exito"] if x >= 70 else COLORES["acento"] if x >= 60 
              else COLORES["alerta"] for x in rendimiento.values]
    
    ax.barh(rendimiento.index, rendimiento.values, color=colors)
    ax.axvline(x=70, color='gray', linestyle='--', alpha=0.5, label='Umbral aprobación')
    
    ax.set_title(titulo or f"Top {top_n} Asignaturas por Promedio")
    ax.set_xlabel("Promedio de Calificación")
    ax.set_ylabel("Asignatura")
    ax.legend()
    
    if guardar and ruta:
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
    
    return fig


def graficar_evolucion_temporal(
    df: pd.DataFrame,
    columna_fecha: str = "semestre",
    columna_valor: str = "calificacion",
    titulo: Optional[str] = None,
    guardar: bool = False,
    ruta: Optional[str] = None
) -> plt.Figure:
    """
    Gráfica de evolución temporal de métricas.
    
    Args:
        df: DataFrame con datos
        columna_fecha: Columna de tiempo
        columna_valor: Columna a graficar
        titulo: Título de la gráfica
        guardar: Si True, guarda la imagen
        ruta: Ruta para guardar
    
    Returns:
        Figura de matplotlib
    """
    configurar_estilo()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    datos = df.groupby(columna_fecha)[columna_valor].agg(["mean", "std"])
    
    ax.plot(datos.index, datos["mean"], marker='o', color=COLORES["primario"], 
            linewidth=2, markersize=8, label='Promedio')
    ax.fill_between(datos.index, 
                    datos["mean"] - datos["std"],
                    datos["mean"] + datos["std"],
                    alpha=0.2, color=COLORES["primario"])
    
    ax.set_title(titulo or f"Evolución de {columna_valor.title()} por Período")
    ax.set_xlabel(columna_fecha.title())
    ax.set_ylabel(columna_valor.title())
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    if guardar and ruta:
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
    
    return fig


def graficar_distribucion_calificaciones(
    df: pd.DataFrame,
    titulo: Optional[str] = None,
    guardar: bool = False,
    ruta: Optional[str] = None
) -> plt.Figure:
    """
    Histograma de distribución de calificaciones.
    
    Args:
        df: DataFrame con datos académicos
        titulo: Título de la gráfica
        guardar: Si True, guarda la imagen
        ruta: Ruta para guardar
    
    Returns:
        Figura de matplotlib
    """
    configurar_estilo()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(df["calificacion"], bins=20, color=COLORES["primario"], 
            edgecolor='white', alpha=0.7)
    ax.axvline(x=df["calificacion"].mean(), color=COLORES["acento"], 
               linestyle='--', linewidth=2, label=f'Media: {df["calificacion"].mean():.1f}')
    
    ax.set_title(titulo or "Distribución de Calificaciones")
    ax.set_xlabel("Calificación")
    ax.set_ylabel("Frecuencia")
    ax.legend()
    
    if guardar and ruta:
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
    
    return fig


def graficar_mapa_calor_correlaciones(
    df: pd.DataFrame,
    columnas: Optional[list] = None,
    titulo: Optional[str] = None,
    guardar: bool = False,
    ruta: Optional[str] = None
) -> plt.Figure:
    """
    Mapa de calor de correlaciones entre variables numéricas.
    
    Args:
        df: DataFrame con datos
        columnas: Lista de columnas a incluir
        titulo: Título de la gráfica
        guardar: Si True, guarda la imagen
        ruta: Ruta para guardar
    
    Returns:
        Figura de matplotlib
    """
    configurar_estilo()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    if columnas:
        df_corr = df[columnas].corr()
    else:
        df_corr = df.select_dtypes(include=[np.number]).corr()
    
    mask = np.triu(np.ones_like(df_corr, dtype=bool))
    
    sns.heatmap(df_corr, mask=mask, annot=True, cmap='RdYlBu_r', center=0,
                square=True, linewidths=0.5, ax=ax, vmin=-1, vmax=1)
    
    ax.set_title(titulo or "Correlaciones entre Variables")
    
    if guardar and ruta:
        fig.savefig(ruta, dpi=300, bbox_inches='tight')
    
    return fig
