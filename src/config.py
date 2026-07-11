"""
Configuración del proyecto de Analítica Educativa
"""
from pathlib import Path

# Rutas del proyecto
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Columnas esperadas del dataset
COLUMNAS_ESTUDIANTES = [
    "id_estudiante",
    "genero",
    "edad",
    "estado_civil",
    "nacionalidad",
    "modo_admision",
    "becado",
    "telefono",
    "correo",
    "direccion",
]

COLUMNAS_ACADEMICAS = [
    "id_estudiante",
    "semestre",
    "ano_academico",
    "id_asignatura",
    "nombre_asignatura",
    "creditos",
    "calificacion",
    "aprobado",
    "deserto",
]

COLUMNAS_DEMANDA = [
    "id_asignatura",
    "semestre",
    "ano_academico",
    "cupos_disponibles",
    "inscritos",
    "demanda",
]

# Configuración de visualización
COLORES = {
    "primario": "#2E86AB",
    "secundario": "#A23B72",
    "acento": "#F18F01",
    "exito": "#C73E1D",
    "alerta": "#3B1F2B",
}

ESTILO_GRAFICO = {
    "figure.figsize": (12, 6),
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "font.size": 10,
}
