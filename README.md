# Analítica Educativa

Proyecto de análisis de datos para instituciones educativas, enfocado en tomar decisiones informadas sobre oferta académica, deserción estudiantil y rendimiento.

## Objetivos

- Analizar patrones de deserción estudiantil
- Evaluar el rendimiento académico por asignatura
- Identificar asignaturas con alta/baja demanda
- Generar recomendaciones para la toma de decisiones

## Estructura del Proyecto

```
analitica-educativa/
├── data/
│   ├── raw/           # Datos originales
│   └── processed/     # Datos procesados
├── notebooks/         # Notebooks Jupyter
├── src/               # Código fuente
├── dashboard/         # Aplicación Streamlit
├── reports/           # Reportes generados
└── requirements.txt
```

## Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Análisis en Notebook
```bash
jupyter notebook notebooks/
```

### Dashboard Interactivo
```bash
streamlit run dashboard/app.py
```

## Módulos

- `data_loader.py`: Carga de datos desde CSV
- `preprocessor.py`: Limpieza y preprocesamiento
- `analyzer.py`: Análisis estadístico y métricas
- `visualizer.py`: Generación de gráficas

## Datos Requeridos

### Dataset de Estudiantes
- id_estudiante, genero, edad, estado_civil, nacionalidad, modo_admision, becado

### Dataset de Rendimiento Académico
- id_estudiante, semestre, ano_academico, id_asignatura, nombre_asignatura, creditos, calificacion, aprobado, deserto

### Dataset de Demanda
- id_asignatura, semestre, ano_academico, cupos_disponibles, inscritos, demanda

## Dashboard

El dashboard incluye:
- Vista general con métricas clave
- Análisis de deserción por múltiples dimensiones
- Rendimiento por asignatura
- Evolución temporal
- Recomendaciones automatizadas

## Licencia

MIT
