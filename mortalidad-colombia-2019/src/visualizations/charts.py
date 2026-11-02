import json
from pathlib import Path
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.processing.transformations import MONTHS, AGE_ORDER, top_causes, top_homicide_municipalities, lowest_mortality_municipalities

GEOJSON_URL = "https://raw.githubusercontent.com/ytolosa/mapas-colombia/main/output/geojson/col_departamentos_inset_nacional.geojson"
GEOJSON_CACHE = Path(__file__).resolve().parents[2] / "data" / "departamentos.geojson"

def load_geojson():
    if GEOJSON_CACHE.exists():
        try:
            return json.loads(GEOJSON_CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    try:
        r = requests.get(GEOJSON_URL, timeout=8)
        r.raise_for_status()
        geo = r.json()
        GEOJSON_CACHE.write_text(json.dumps(geo, ensure_ascii=False), encoding="utf-8")
        return geo
    except Exception:
        return None

def _empty(title, msg="No hay datos para los filtros seleccionados."):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, showarrow=False)
    fig.update_layout(title=title, template="plotly_white")
    return fig

def map_departments(df):
    title = "Mortalidad por departamento"
    if df.empty:
        return _empty(title)
    grouped = df.groupby(["COD_DEP_KEY", "DEPARTAMENTO"]).size().reset_index(name="Muertes")
    geo = load_geojson()
    if geo:
        # Determine property name for department code and normalize codes.
        props = geo.get("features", [{}])[0].get("properties", {})
        candidate = next((k for k in props if "codigo" in k.lower() or "dpto" in k.lower()), None)
        if candidate:
            for feature in geo["features"]:
                val = feature.get("properties", {}).get(candidate)
                if val is not None:
                    feature.setdefault("properties", {})["COD_DEP_KEY"] = str(val).zfill(2)
            grouped["COD_DEP_KEY"] = grouped["COD_DEP_KEY"].astype(str).str.zfill(2)
            fig = px.choropleth(grouped, geojson=geo, locations="COD_DEP_KEY",
                                featureidkey="properties.COD_DEP_KEY", color="Muertes",
                                hover_name="DEPARTAMENTO", hover_data={"COD_DEP_KEY": False, "Muertes": ":,"},
                                color_continuous_scale="YlOrRd", title=title)
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(template="plotly_white")
            return fig
    # Explicit fallback: no fake polygons or geographic coordinates.
    fig = px.bar(grouped.sort_values("Muertes", ascending=False), x="DEPARTAMENTO", y="Muertes",
                 title=title + " (vista alternativa: ranking)", color="Muertes",
                 color_continuous_scale="YlOrRd")
    fig.update_layout(template="plotly_white", xaxis_tickangle=-45)
    fig.add_annotation(text="GeoJSON no disponible: se muestra ranking departamental.", xref="paper", yref="paper",
                       x=0, y=1.08, showarrow=False, font=dict(size=11))
    return fig

def monthly_line(df):
    g = df.groupby("MES").size().reindex(range(1,13), fill_value=0).reset_index(name="Muertes")
    g["Mes"] = g["MES"].map(lambda x: MONTHS[x-1])
    return px.line(g, x="Mes", y="Muertes", markers=True, title="Mortalidad mensual",
                   category_orders={"Mes": MONTHS}, hover_data={"MES": False})

def violent_cities(df):
    g = top_homicide_municipalities(df)
    if g.empty: return _empty("Cinco municipios con más homicidios por código X95")
    g["Lugar"] = g["MUNICIPIO"] + " — " + g["DEPARTAMENTO"]
    return px.bar(g, x="Lugar", y="Casos", color="Casos", title="Top 5 municipios: homicidios con código X95",
                  hover_data=["COD_DANE_KEY"], color_continuous_scale="Reds")

def lowest_cities_pie(df):
    g = lowest_mortality_municipalities(df)
    if g.empty: return _empty("10 municipios con menor mortalidad registrada")
    g["Lugar"] = g["MUNICIPIO"] + " — " + g["DEPARTAMENTO"]
    return px.pie(g, names="Lugar", values="Muertes", title="10 municipios con menor mortalidad registrada",
                  hover_data=["COD_DANE_KEY"], hole=0.15)

def causes_table_data(df):
    g = top_causes(df).copy()
    g = g.rename(columns={"COD_MUERTE":"Código", "DESC_CAUSA":"Causa", "Total":"Fallecimientos"})
    g["Fallecimientos"] = g["Fallecimientos"].map(lambda x: f"{x:,}".replace(",", "."))
    return g.to_dict("records")

def stacked_sex(df):
    g = df.groupby(["DEPARTAMENTO", "SEXO_LABEL"]).size().reset_index(name="Muertes")
    return px.bar(g, x="DEPARTAMENTO", y="Muertes", color="SEXO_LABEL", barmode="stack",
                  title="Mortalidad por sexo y departamento",
                  labels={"SEXO_LABEL":"Sexo", "Muertes":"Fallecimientos"},
                  color_discrete_sequence=px.colors.qualitative.Set2)

def age_distribution(df):
    g = df.groupby("GRUPO_EDAD_LABEL").size().reindex(AGE_ORDER, fill_value=0).reset_index(name="Muertes")
    g = g.rename(columns={"GRUPO_EDAD_LABEL":"Grupo de edad"})
    return px.bar(g, x="Grupo de edad", y="Muertes", title="Distribución de fallecimientos por grupo de edad",
                  category_orders={"Grupo de edad": AGE_ORDER}, color="Muertes",
                  color_continuous_scale="Blues")
