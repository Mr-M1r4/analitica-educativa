-- ============================================================================
-- MODELO RELACIONAL - UNIVERSIDAD
-- Base de datos: analitica_educativa
-- Fecha: 2025
-- ============================================================================

-- Tabla: semestres
CREATE TABLE semestres (
    id_semestre SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    ano_academico INTEGER NOT NULL,
    periodo INTEGER NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    activo BOOLEAN DEFAULT FALSE
);

-- Tabla: profesores
CREATE TABLE profesores (
    id_profesor SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100),
    antiguedad_anos INTEGER,
    nivel_estudios VARCHAR(50),
    contrato VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla: asignaturas
CREATE TABLE asignaturas (
    id_asignatura SERIAL PRIMARY KEY,
    nombre_asignatura VARCHAR(100) NOT NULL,
    carrera VARCHAR(100) NOT NULL,
    facultad VARCHAR(100) NOT NULL,
    creditos INTEGER NOT NULL
);

-- Tabla: estudiantes
CREATE TABLE estudiantes (
    id_estudiante SERIAL PRIMARY KEY,
    genero CHAR(1) NOT NULL,
    edad INTEGER NOT NULL,
    estado_civil VARCHAR(20),
    nacionalidad VARCHAR(20),
    modo_admision VARCHAR(50),
    becado BOOLEAN DEFAULT FALSE,
    facultad VARCHAR(100) NOT NULL,
    carrera VARCHAR(100) NOT NULL,
    id_semestre_ingreso INTEGER REFERENCES semestres(id_semestre)
);

-- Tabla: secciones
CREATE TABLE secciones (
    id_seccion SERIAL PRIMARY KEY,
    id_asignatura INTEGER NOT NULL REFERENCES asignaturas(id_asignatura),
    id_profesor INTEGER NOT NULL REFERENCES profesores(id_profesor),
    semestre VARCHAR(10) NOT NULL,
    capacidad INTEGER,
    inscritos INTEGER,
    seccion CHAR(1)
);

-- Tabla: rendimiento_academico (tabla de hechos)
CREATE TABLE rendimiento_academico (
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id_estudiante),
    id_asignatura INTEGER NOT NULL REFERENCES asignaturas(id_asignatura),
    id_profesor INTEGER REFERENCES profesores(id_profesor),
    id_seccion INTEGER REFERENCES secciones(id_seccion),
    semestre VARCHAR(10) NOT NULL,
    ano_academico INTEGER NOT NULL,
    facultad VARCHAR(100),
    carrera VARCHAR(100),
    creditos INTEGER,
    calificacion DECIMAL(5,2),
    aprobado BOOLEAN,
    deserto BOOLEAN,
    PRIMARY KEY (id_estudiante, id_asignatura, semestre)
);

-- Tabla: evaluaciones
CREATE TABLE evaluaciones (
    id_evaluacion SERIAL PRIMARY KEY,
    id_estudiante INTEGER NOT NULL REFERENCES estudiantes(id_estudiante),
    id_asignatura INTEGER NOT NULL REFERENCES asignaturas(id_asignatura),
    semestre VARCHAR(10) NOT NULL,
    tipo_evaluacion VARCHAR(50) NOT NULL,
    nota DECIMAL(5,2) NOT NULL,
    peso DECIMAL(3,2),
    fecha DATE
);

-- Tabla: egresados
CREATE TABLE egresados (
    id_egresado SERIAL PRIMARY KEY,
    id_estudiante INTEGER NOT NULL UNIQUE REFERENCES estudiantes(id_estudiante),
    carrera VARCHAR(100),
    facultad VARCHAR(100),
    ano_ingreso INTEGER,
    ano_egreso INTEGER,
    duracion_anos INTEGER,
    promedio_final DECIMAL(5,2),
    titulo_obtenido BOOLEAN,
    trabaja_en_area BOOLEAN,
    satisfaccion_laboral INTEGER
);

-- ============================================================================
-- ÍNDICES RECOMENDADOS
-- ============================================================================
CREATE INDEX idx_estudiantes_facultad ON estudiantes(facultad);
CREATE INDEX idx_estudiantes_carrera ON estudiantes(carrera);
CREATE INDEX idx_rendimiento_semestre ON rendimiento_academico(semestre);
CREATE INDEX idx_rendimiento_carrera ON rendimiento_academico(carrera);
CREATE INDEX idx_evaluaciones_estudiante ON evaluaciones(id_estudiante);
CREATE INDEX idx_egresados_carrera ON egresados(carrera);
CREATE INDEX idx_profesores_especialidad ON profesores(especialidad);
CREATE INDEX idx_secciones_semestre ON secciones(semestre);

-- ============================================================================
-- COMENTARIOS EN TABLAS
-- ============================================================================
COMMENT ON TABLE semestres IS 'Períodos académicos de la universidad';
COMMENT ON TABLE profesores IS 'Docentes de todas las facultades';
COMMENT ON TABLE asignaturas IS 'Catálogo de materias por carrera y facultad';
COMMENT ON TABLE estudiantes IS 'Estudiantes registrados en la universidad';
COMMENT ON TABLE secciones IS 'Grupos/clases por semestre y asignatura';
COMMENT ON TABLE rendimiento_academico IS 'Calificaciones finales por materia y semestre';
COMMENT ON TABLE evaluaciones IS 'Notas parciales, proyectos y evaluaciones';
COMMENT ON TABLE egresados IS 'Seguimiento a graduados de la universidad';

-- ============================================================================
-- RELACIONES
-- ============================================================================
-- estudiantes.id_semestre_ingreso -> semestres.id_semestre
-- secciones.id_asignatura -> asignaturas.id_asignatura
-- secciones.id_profesor -> profesores.id_profesor
-- rendimiento_academico.id_estudiante -> estudiantes.id_estudiante
-- rendimiento_academico.id_asignatura -> asignaturas.id_asignatura
-- rendimiento_academico.id_profesor -> profesores.id_profesor
-- rendimiento_academico.id_seccion -> secciones.id_seccion
-- evaluaciones.id_estudiante -> estudiantes.id_estudiante
-- evaluaciones.id_asignatura -> asignaturas.id_asignatura
-- egresados.id_estudiante -> estudiantes.id_estudiante
