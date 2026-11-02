import os
from dash import Dash
from src.data.loader import load_all_data
from src.layout.dashboard import build_layout
from src.utils.helpers import register_callbacks

DATA = load_all_data()
app = Dash(__name__, title="Dashboard de Mortalidad en Colombia — 2019")
server = app.server
app.layout = build_layout(DATA)
register_callbacks(app, DATA)

if __name__ == "__main__":
    app.run(debug=os.getenv("DASH_DEBUG", "false").lower() == "true",
            host="0.0.0.0", port=int(os.getenv("PORT", "8050")))
