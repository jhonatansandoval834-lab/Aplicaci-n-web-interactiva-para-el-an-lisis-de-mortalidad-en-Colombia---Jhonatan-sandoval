from dash import html, dcc, dash_table
from src.processing.transformations import prepare
from src.visualizations.charts import map_departments, monthly_line, violent_cities, lowest_cities_pie, causes_table_data, stacked_sex, age_distribution

def build_layout(data):
    df = prepare(data["mortality"])
    departments = sorted(df["DEPARTAMENTO"].dropna().unique().tolist())
    sexes = sorted(df["SEXO_LABEL"].dropna().unique().tolist())
    ages = sorted(df["GRUPO_EDAD_LABEL"].dropna().unique().tolist())
    months = [{"label": f"{i:02d} — {name}", "value": i} for i, name in enumerate(
        ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"],1)]
    cards = [
        html.Div([html.Div("Registros analizados", className="kpi-label"), html.Div(f"{len(df):,}".replace(",", "."), id="kpi-total", className="kpi-value")], className="kpi"),
        html.Div([html.Div("Departamentos", className="kpi-label"), html.Div(str(df["DEPARTAMENTO"].nunique()), className="kpi-value")], className="kpi"),
        html.Div([html.Div("Municipios con registros", className="kpi-label"), html.Div(str(df["COD_DANE_KEY"].nunique()), className="kpi-value")], className="kpi"),
    ]
    return html.Div([
        html.Header([html.H1("Dashboard de Mortalidad en Colombia — 2019"),
                     html.P("Exploración geográfica, temporal, demográfica y epidemiológica de defunciones no fetales.")], className="hero"),
        html.Div(cards, className="kpi-grid"),
        html.Section([
            html.H2("Filtros"),
            html.Div([
                html.Div([html.Label("Departamento"), dcc.Dropdown(id="filter-department", options=[{"label":"Todos","value":"Todos"}]+[{"label":x,"value":x} for x in departments], value="Todos", clearable=False)]),
                html.Div([html.Label("Sexo"), dcc.Dropdown(id="filter-sex", options=[{"label":"Todos","value":"Todos"}]+[{"label":x,"value":x} for x in sexes], value="Todos", clearable=False)]),
                html.Div([html.Label("Grupo de edad"), dcc.Dropdown(id="filter-age", options=[{"label":"Todos","value":"Todos"}]+[{"label":x,"value":x} for x in ages], value="Todos", clearable=False)]),
                html.Div([html.Label("Mes"), dcc.Dropdown(id="filter-month", options=[{"label":"Todos","value":"Todos"}]+months, value="Todos", clearable=False)]),
            ], className="filters")
        ], className="panel"),
        html.Div([
            dcc.Graph(id="graph-map", figure=map_departments(df)),
            dcc.Graph(id="graph-month", figure=monthly_line(df)),
            dcc.Graph(id="graph-violent", figure=violent_cities(df)),
            dcc.Graph(id="graph-lowest", figure=lowest_cities_pie(df)),
            html.Div([html.H3("Diez principales causas de muerte"),
                      dash_table.DataTable(id="table-causes", columns=[{"name":"Código","id":"Código"},{"name":"Causa","id":"Causa"},{"name":"Fallecimientos","id":"Fallecimientos"}],
                                           data=causes_table_data(df), page_size=10, style_table={"overflowX":"auto"},
                                           style_cell={"textAlign":"left","padding":"9px","whiteSpace":"normal","height":"auto"},
                                           style_header={"fontWeight":"bold","backgroundColor":"#eaf0f6"})], className="panel"),
            dcc.Graph(id="graph-sex", figure=stacked_sex(df)),
            dcc.Graph(id="graph-age", figure=age_distribution(df)),
        ], className="charts-grid"),
        html.Footer([
            html.P("Fuente de datos: archivos suministrados para la actividad (mortalidad 2019, catálogo CIE-10 y DIVIPOLA)."),
            html.P("Nota metodológica: el ranking de municipios con menor mortalidad considera únicamente municipios con al menos un registro en el archivo; no equivale a municipios con cero defunciones.")
        ])
    ], className="container")
