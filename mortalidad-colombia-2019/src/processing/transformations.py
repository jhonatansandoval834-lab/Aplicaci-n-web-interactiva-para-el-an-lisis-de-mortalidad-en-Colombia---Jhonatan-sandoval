import pandas as pd

MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
AGE_GROUPS = [
    ("Mortalidad neonatal", range(0, 5)),
    ("Mortalidad infantil", range(5, 7)),
    ("Primera infancia", range(7, 9)),
    ("Niñez", range(9, 11)),
    ("Adolescencia", range(11, 12)),
    ("Juventud", range(12, 14)),
    ("Adultez temprana", range(14, 17)),
    ("Adultez intermedia", range(17, 20)),
    ("Vejez", range(20, 25)),
    ("Longevidad / centenarios", range(25, 29)),
    ("Edad desconocida", range(29, 30)),
]
AGE_MAP = {code: label for label, codes in AGE_GROUPS for code in codes}
AGE_ORDER = [label for label, _ in AGE_GROUPS]

def filter_data(df, department=None, sex=None, age=None, month=None):
    out = df
    if department not in (None, "Todos"):
        out = out[out["DEPARTAMENTO"] == department]
    if sex not in (None, "Todos"):
        out = out[out["SEXO_LABEL"] == sex]
    if age not in (None, "Todos"):
        out = out[out["GRUPO_EDAD_LABEL"] == age]
    if month not in (None, "Todos"):
        out = out[out["MES"] == int(month)]
    return out

def prepare(df):
    out = df.copy()
    out["MES_LABEL"] = out["MES"].map(lambda x: MONTHS[int(x)-1] if pd.notna(x) and 1 <= int(x) <= 12 else "Mes no válido")
    out["GRUPO_EDAD_LABEL"] = out["GRUPO_EDAD1"].map(AGE_MAP).fillna("Código de edad fuera de clasificación")
    return out

def top_causes(df):
    return (df.groupby(["COD_MUERTE", "DESC_CAUSA"], dropna=False).size()
            .reset_index(name="Total").sort_values("Total", ascending=False).head(10))

def top_homicide_municipalities(df):
    subset = df[(df["MANERA_MUERTE"].astype(str).str.strip().str.lower() == "homicidio") &
                (df["COD_MUERTE"].astype(str).str.upper().str.startswith("X95"))]
    return (subset.groupby(["COD_DANE_KEY", "MUNICIPIO", "DEPARTAMENTO"]).size()
            .reset_index(name="Casos").sort_values("Casos", ascending=False).head(5))

def lowest_mortality_municipalities(df):
    # Only municipalities that have at least one mortality record are ranked.
    return (df.groupby(["COD_DANE_KEY", "MUNICIPIO", "DEPARTAMENTO"]).size()
            .reset_index(name="Muertes").sort_values(["Muertes", "MUNICIPIO"])
            .head(10))
