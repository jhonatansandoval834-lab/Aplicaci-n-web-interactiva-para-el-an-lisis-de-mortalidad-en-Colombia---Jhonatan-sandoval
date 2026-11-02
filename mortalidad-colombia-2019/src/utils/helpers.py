from dash import Input, Output
from src.processing.transformations import prepare, filter_data
from src.visualizations.charts import map_departments, monthly_line, violent_cities, lowest_cities_pie, causes_table_data, stacked_sex, age_distribution

def register_callbacks(app, data):
    df = prepare(data["mortality"])
    @app.callback(
        Output("graph-map","figure"), Output("graph-month","figure"),
        Output("graph-violent","figure"), Output("graph-lowest","figure"),
        Output("table-causes","data"), Output("graph-sex","figure"),
        Output("graph-age","figure"), Output("kpi-total","children"),
        Input("filter-department","value"), Input("filter-sex","value"),
        Input("filter-age","value"), Input("filter-month","value")
    )
    def update(department, sex, age, month):
        filtered = filter_data(df, department, sex, age, month)
        return (map_departments(filtered), monthly_line(filtered), violent_cities(filtered),
                lowest_cities_pie(filtered), causes_table_data(filtered), stacked_sex(filtered),
                age_distribution(filtered), f"{len(filtered):,}".replace(",", "."))
