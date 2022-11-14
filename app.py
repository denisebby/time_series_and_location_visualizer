import dash
from dash import dcc, html, dash_table, ctx
from dash.dependencies import Output, Input, State
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import pandas as pd


external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;1,100&display=swap',
    'https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;1,100&family=Roboto+Mono&display=swap'
]



######## Utility ##############

form = html.Center(dbc.Form([
    dbc.Row(
        [
            dbc.Label("Store", width="auto"),
            dbc.Col(
                dbc.Input(id = "store-input",type="text", placeholder="Enter store"),
                className="me-3",
            ),
        ],
        className="g-2", style={"margin-bottom": "1em"}
    ),
    dbc.Row(
        [
            dbc.Label("Grain", width="auto"),
            dbc.Col(
                dbc.Input(id="grain-input",type="text", placeholder="Enter grain"),
                className="me-3",
            ),
            
        ],
        className="g-2", style={"margin-bottom": "1em"}
    ),
    dbc.Row([
        dbc.Col([dbc.Button(id="submit-button",children = "Submit", color="primary")],),

    ], className="g-2",style={"textAlign":"center", "margin-bottom": "1em"})



], style = {"width":"50%", "margin-top": "2em"}))





###############################
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}])
app.title = "Time Series Visualizer"
server = app.server


def data_in():
    df = pd.read_csv("data/dunkin_stores.csv")
    df.rename(columns={"row_id": "store"}, inplace=True)
    return df

def app_layout():
   
    navbar = dbc.NavbarSimple(
        brand="Time Series Visualizer",
        brand_style = {"font-family": "Lato, -apple-system, sans-serif" , "font-size": "2rem", "padding": "0.1rem 0.1rem"},
        brand_href="#",
        color="black",
        dark=True,
        id="my-navbar",
        style={"height": "3rem", "padding": "0.1rem 0.1rem"},
        expand = True,
     
    )

    return html.Div(children=[
        navbar,
        dcc.Store(id = "selected-grain",data={}),
        dbc.Container([

            form,
            dcc.Graph(id="time-series-1"),
            dcc.Graph(id="choropleth")
        

        ],)
        
    ])

source_df = pd.DataFrame(data = {"store": [1,2], "grain": ["AB", "BC"], "val": [2,10]})

seasonality_df = pd.DataFrame(data = \
                              {
                                "store": [1]*12 + [2]*12,
                               "state": ["AL"]*12 + ["NJ"]*12,
                               "month": list(range(1,13))*2,
                               "value": list(range(1,13,)) + list(range(12,0, -1))
                              }
                             )

location_df = data_in()

app.layout = app_layout

####### Callbacks #######################
@app.callback(
    Output("selected-grain","data"),
    Input("submit-button", "n_clicks"),
    [State("store-input", "value"), State("grain-input", "value")]
)
def get_input(n_clicks, store_input, grain_input):
    # print(u'''
    #     The Button has been pressed {} times,
    #     Input 1 is "{}",
    #     and Input 2 is "{}"
    # '''.format(n_clicks, store_input, grain_input))

    if store_input is None or grain_input is None:
        raise PreventUpdate


    return {"store": int(store_input), "grain": grain_input}

@app.callback(
    [Output("time-series-1", "figure"),Output("choropleth", "figure")],
    Input("selected-grain", "data")
)
def get_graphs(grain_dict):
    print(grain_dict)

    if grain_dict == "" or grain_dict is None or None in list(grain_dict.values()):
        return 


    fig = px.line(data_frame=seasonality_df.query(f"store=={grain_dict['store']}"),x="month", y = "value", template = "plotly_white")
    fig.update_xaxes(linecolor="rgb(0, 58, 174)",mirror = True, linewidth = 1)
    fig.update_yaxes(linecolor="rgb(0, 58, 174)",mirror = True, linewidth = 1)

    state_us = location_df.query(f"store=={grain_dict['store']}").state.iloc[0]

    loc_df_plot = location_df.query(f"state=='{state_us}'")

    fig_map = go.Figure(data=go.Scattergeo(
        lon = loc_df_plot['loc_long'],
        lat = loc_df_plot['loc_lat'],
        text = loc_df_plot['store'],
        mode = 'markers',
        ))

    fig_map.update_layout(
            title = f'{state_us}',
            geo_scope='usa',
        )
    
    fig_map.update_xaxes(linecolor="rgb(0, 58, 174)",mirror = True, linewidth = 1)
    fig_map.update_yaxes(linecolor="rgb(0, 58, 174)",mirror = True, linewidth = 1)


    return fig, fig_map


if __name__=='__main__':
    app.run_server(debug=True, port=8005)
    # host = "0.0.0.0"
    # app.run_server(debug=True, host = "127.0.0.1", port=int(os.environ.get("PORT", 8081)))