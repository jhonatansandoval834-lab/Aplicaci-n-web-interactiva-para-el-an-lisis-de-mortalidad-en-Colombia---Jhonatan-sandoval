from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

MORTALITY_FILE = DATA_DIR / "mortalidad_2019.xlsx"
CAUSES_FILE = DATA_DIR / "codigos_muerte.xlsx"
DIVIPOLA_FILE = DATA_DIR / "divipola.xlsx"

def _clean_code(value, width=None):
    if pd.isna(value):
        return None
    s = str(value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    if width and s.isdigit():
        s = s.zfill(width)
    return s

def load_all_data():
    missing = [str(p) for p in [MORTALITY_FILE, CAUSES_FILE, DIVIPOLA_FILE] if not p.exists()]
    if missing:
        raise FileNotFoundError("Faltan archivos requeridos: " + ", ".join(missing))

    mortality = pd.read_excel(MORTALITY_FILE, sheet_name="No_Fetales_2019")
    causes = pd.read_excel(CAUSES_FILE, sheet_name="Final", header=8)
    divipola = pd.read_excel(DIVIPOLA_FILE, sheet_name="Hoja1")

    required = ["COD_DANE", "COD_DEPARTAMENTO", "COD_MUNICIPIO", "AÑO", "MES",
                "SEXO", "GRUPO_EDAD1", "MANERA_MUERTE", "COD_MUERTE"]
    missing_cols = [c for c in required if c not in mortality.columns]
    if missing_cols:
        raise ValueError(f"Columnas faltantes en mortalidad: {missing_cols}")

    mortality = mortality.copy()
    mortality["COD_DANE_KEY"] = mortality["COD_DANE"].map(lambda x: _clean_code(x, 5))
    mortality["COD_DEP_KEY"] = mortality["COD_DEPARTAMENTO"].map(lambda x: _clean_code(x, 2))
    mortality["COD_MUERTE"] = mortality["COD_MUERTE"].astype(str).str.strip().str.upper()
    mortality["MES"] = pd.to_numeric(mortality["MES"], errors="coerce")
    mortality["SEXO"] = pd.to_numeric(mortality["SEXO"], errors="coerce")
    mortality["GRUPO_EDAD1"] = pd.to_numeric(mortality["GRUPO_EDAD1"], errors="coerce")

    divipola = divipola.copy()
    divipola["COD_DANE_KEY"] = divipola["COD_DANE"].map(lambda x: _clean_code(x, 5))
    divipola["COD_DEP_KEY"] = divipola["COD_DEPARTAMENTO"].map(lambda x: _clean_code(x, 2))
    divipola["COD_MUNICIPIO_KEY"] = divipola["COD_MUNICIPIO"].map(lambda x: _clean_code(x, 3))

    dept_lookup = divipola[["COD_DEP_KEY", "DEPARTAMENTO"]].drop_duplicates()
    muni_lookup = divipola[["COD_DANE_KEY", "MUNICIPIO", "DEPARTAMENTO"]].drop_duplicates("COD_DANE_KEY")
    mortality = mortality.merge(muni_lookup, on="COD_DANE_KEY", how="left", validate="many_to_one")
    # Prefer DIVIPOLA department labels, with original code fallback.
    mortality["DEPARTAMENTO"] = mortality["DEPARTAMENTO"].fillna(
        mortality["COD_DEP_KEY"].map(dict(zip(dept_lookup["COD_DEP_KEY"], dept_lookup["DEPARTAMENTO"])))
    )
    mortality["MUNICIPIO"] = mortality["MUNICIPIO"].fillna("Municipio sin etiqueta DIVIPOLA")

    causes = causes.rename(columns={
        "Código de la CIE-10 cuatro caracteres": "COD_CIE4",
        "Descripcion  de códigos mortalidad a cuatro caracteres": "DESC_CIE4",
        "Código de la CIE-10 tres caracteres": "COD_CIE3",
        "Descripción  de códigos mortalidad a tres caracteres": "DESC_CIE3"
    })
    causes["COD_CIE4"] = causes["COD_CIE4"].astype(str).str.strip().str.upper()
    causes["COD_CIE3"] = causes["COD_CIE3"].astype(str).str.strip().str.upper()
    causes["DESC_CIE4"] = causes["DESC_CIE4"].astype(str).str.strip()
    causes["DESC_CIE3"] = causes["DESC_CIE3"].astype(str).str.strip()
    causes = causes.dropna(subset=["COD_CIE4"])
    causes = causes[~causes["COD_CIE4"].isin(["NAN", ""])]

    # Resolve description with exact 4-char code first, then 3-char fallback.
    lookup4 = causes.drop_duplicates("COD_CIE4").set_index("COD_CIE4")["DESC_CIE4"].to_dict()
    lookup3 = causes.drop_duplicates("COD_CIE3").set_index("COD_CIE3")["DESC_CIE3"].to_dict()
    mortality["DESC_CAUSA"] = mortality["COD_MUERTE"].map(lookup4)
    mask = mortality["DESC_CAUSA"].isna()
    mortality.loc[mask, "DESC_CAUSA"] = mortality.loc[mask, "COD_MUERTE"].str[:3].map(lookup3)
    mortality["DESC_CAUSA"] = mortality["DESC_CAUSA"].replace({"nan": None, "": None}).fillna("Descripción no disponible")

    sex_labels = {1: "Masculino", 2: "Femenino", 3: "Sexo no especificado"}
    mortality["SEXO_LABEL"] = mortality["SEXO"].map(sex_labels).fillna("Sexo desconocido")
    return {"mortality": mortality, "causes": causes, "divipola": divipola}
