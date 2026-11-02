# Aplicaci-n-web-interactiva-para-el-an-lisis-de-mortalidad-en-Colombia---Jhonatan-sandoval
Aplicación analítica web desarrollada con Python, Dash, Plotly y Pandas para explorar los registros de mortalidad no fetal de Colombia correspondientes a 2019.

## Objetivo
Examinar los registros desde perspectivas geográfica, temporal, demográfica y epidemiológica, usando los archivos suministrados para la actividad.

## Archivos fuente
- `data/mortalidad_2019.xlsx`: base de mortalidad.
- `data/codigos_muerte.xlsx`: catálogo CIE-10.
- `data/divipola.xlsx`: referencia de códigos y nombres territoriales.

## Estructura
mortalidad-colombia-2019/
├── app.py
├── requirements.txt
├── Procfile
├── README.md
├── data/
├── assets/styles.css
├── screenshots/
└── src/
    ├── data/loader.py
    ├── processing/transformations.py
    ├── visualizations/charts.py
    ├── layout/dashboard.py
    └── utils/helpers.py
```

## Requisitos
- Python 3.10 o 3.11 recomendado.
- pip.
- Conexión a internet necesaria para descargar GeoJSON departamental en la primera carga del mapa. Si falla, la aplicación muestra un ranking departamental alternativo.
- Dependencias listadas en `requirements.txt`.

## Instalación y ejecución local
Desde la carpeta raíz:

```bash
python -m venv .venv
```

Windows:
```bash
.venv\\Scripts\\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Instalar:
```bash
pip install -r requirements.txt
```

Ejecutar:
```bash
python app.py
```
Abrir `http://127.0.0.1:8050`.

## Visualizaciones e interpretación
1. **Mapa/ranking departamental:** muestra conteos por departamento. El mapa coroplético requiere GeoJSON; sin conectividad, se usa ranking de barras como fallback.
2. **Línea mensual:** total de registros por mes. Los meses se presentan en orden calendario.
3. **Top 5 homicidios X95:** se limita a registros con `MANERA_MUERTE = Homicidio` y código que comienza por `X95`, conforme a la base y catálogo.
4. **Diez municipios con menor mortalidad registrada:** ordena municipios con registros presentes. No incluye municipios ausentes como cero.
5. **Top 10 causas:** frecuencia por código de causa con descripción asociada al catálogo CIE-10.
6. **Barras apiladas sexo/departamento:** conserva los códigos de sexo 1, 2 y 3 como categorías rotuladas.
7. **Grupos de edad:** agrupa `GRUPO_EDAD1` según los intervalos/códigos proporcionados en la actividad. Es una distribución categórica de frecuencias, no un histograma de edades continuas.

Los valores exactos y rankings son calculados dinámicamente desde la base. No se incluyen interpretaciones de resultados precalculados o inventados.
