# HACIA UNA METAGENÓMICA FAIR: DESARROLLO DE UN MARCO PARA EL ANÁLISIS DE DATOS PÚBLICOS EN ENFERMEDADES MENTALES

Este repositorio contiene el material asociado al Trabajo de Fin de Máster titulado “Hacia una metagenómica FAIR: desarrollo de un marco para el análisis de datos públicos en enfermedades mentales”, desarrollado en la Universidad Europea dentro del Máster Universitario en Bioinformática.  

El proyecto se enmarca en las actividades de la Plataforma de Medicina Computacional de la Fundación Pública Andaluza Progreso y Salud / Grupo de Medicina de Sistemas del Instituto de Biomedicina de Sevilla, en el marco del doctorado de Álvaro Román Gómez (Universidad Europea de Madrid). 

## Descripción general

El objetivo del trabajo es evaluar el grado de adherencia a los principios FAIR (Findable, Accessible, Interoperable, Reusable) en conjuntos de datos metagenómicos públicos relacionados con salud mental, y aplicar un pipeline reproducible de análisis funcional sobre el proyecto PRJEB29127 para identificar alteraciones microbianas asociadas a la esquizofrenia.

El repositorio incluye:
- Scripts y notebooks de procesamiento, análisis diferencial y gestión de metadatos.
- Archivos de entorno y configuración para reproducibilidad.

## Estructura del repositirio

El repositorio contiene el código y la configuración necesaria para reproducir el análisis, pero no incluye los datos ni los resultados. Dichas carpetas se generan automáticamente siguiendo el pipeline.

La estructura esperada del proyecto es la siguiente:

- **data/**
  - `metadata/` – carpeta destinada a los metadatos de las muestras. Durante el análisis, el archivo `metadata.csv` se genera.
  - `raw/functional_annotations/` – carpeta donde deben ubicarse los archivos de anotación funcional (`.emapper.annotations`) descargados desde Zenodo. Estos archivos no se encuentran en el repositorio por motivos de tamaño, pero pueden obtenerse manualmente (ver más abajo).

- **notebooks/**
  - `01_metadata_read.R` – script en R para la lectura y depuración de metadatos.
  - `02_deseq_study.ipynb` – notebook en Python que realiza el análisis diferencial con PyDESeq2.

- **results/**
  - `02_deseq_study/csv/` – resultados tabulares generados automáticamente.
  - `02_deseq_study/plots/` – figuras y visualizaciones del análisis.

- **src/**
  - `py/deseq_utils.py` – funciones auxiliares en Python para procesar las anotaciones y ejecutar DESeq2.
  - `r/install_bioc.R` y `r/metadata_utils.R` – utilidades en R para dependencias y gestión de metadatos.

Archivos adicionales:
- `.env` – variables de entorno con las rutas principales.
- `environment.yml` – definición del entorno Conda (Python + R).
- `.gitignore` – exclusión de datos y resultados generados.

### Descarga de datos necesarios

Para reproducir los análisis, es necesario descargar los archivos de anotación funcional desde Zenodo y colocarlos manualmente en la carpeta `data/raw/`.

1. Acceder al siguiente enlace de Zenodo:  
[(https://doi.org/10.5281/zenodo.17458786)]

2. Descargar el archivo comprimido `functional_annotations.zip`.

3. Extraer su contenido dentro de la carpeta del proyecto, de modo que la ruta resultante sea:
      data/raw/functional_annotations/ERRxxxx.emapper.annotations

Una vez completado este paso, el entorno ya dispone de todos los archivos necesarios para ejecutar los notebooks de análisis.
