"""
Basic Appshell with header and navbar that collapses on mobile.
"""

import dash_mantine_components as dmc

from dash import Dash, Input, Output, State, callback, dcc
from helper import MantineUI, dates, product, map_df, state_data
from figures import create_choropleth, plot_state_timeseries
from polars import col as c
from dash import html

app = Dash(external_stylesheets=dmc.styles.ALL)


layout = dmc.AppShell(
    children=[
        dmc.AppShellHeader(
            dmc.Group(
                [
                    dmc.Burger(id="burger", size="sm", hiddenFrom="sm", opened=False),
                    # dmc.Image(src=logo, h=40),
                    dmc.Title("Demo App", c="blue"),
                ],
                h="100%",
                px="md",
            )
        ),
        dmc.AppShellNavbar(
            id="navbar",
            children=[
                "Navbar",
                MantineUI.product_dropdown(),
                MantineUI.date_dropdown(),
                MantineUI.ffsu_dropdown(),
                MantineUI.metric_dropdown(),
            ],
            p="md",
        ),
        dmc.AppShellMain(
            [
                dmc.Container(
                    [
                        dmc.Title("Drug Pricing Analytics", order=2, mb="md", c="blue"),
                        dmc.Card(
                            children=[
                                dmc.CardSection(
                                    [
                                        dmc.Group(
                                            [
                                                dmc.Text(
                                                    "State-by-State Analysis",
                                                    size="lg",
                                                    fw="bold",
                                                ),
                                                dmc.Text(
                                                    "Click on a state to view detailed trends",
                                                    size="sm",
                                                    c="gray",
                                                ),
                                            ],
                                            justify="space-between",
                                            align="flex-start",
                                        )
                                    ],
                                    withBorder=True,
                                    inheritPadding=True,
                                    py="xs",
                                ),
                                dmc.CardSection(
                                    dcc.Graph(
                                        id="heatmap-graph",
                                        style={"height": "500px"},
                                        config={
                                            "displayModeBar": True,
                                            "displaylogo": False,
                                            "modeBarButtonsToRemove": [
                                                "pan2d",
                                                "lasso2d",
                                                "select2d",
                                            ],
                                        },
                                    )
                                ),
                            ],
                            withBorder=True,
                            shadow="sm",
                            radius="md",
                            id="map-card",
                        ),
                        dmc.Card(id="state-chart"),
                    ],
                    size="xl",
                    px=0,
                )
            ]
        ),
    ],
    header={"height": 60},
    padding="md",
    navbar={
        "width": 300,
        "breakpoint": "sm",
        "collapsed": {"mobile": True},
    },
    id="appshell",
)

app.layout = dmc.MantineProvider(layout)


@callback(
    Output("appshell", "navbar"),
    Input("burger", "opened"),
    State("appshell", "navbar"),
)
def navbar_is_open(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened}
    return navbar


@app.callback(
    Output("heatmap-graph", "figure"),
    [
        Input("product-dropdown", "value"),
        Input("date-dropdown", "value"),
        Input("ffsu-checklist", "value"),
        Input("metric-dropdown", "value"),
    ],
)
def update_heatmap(product_value, date_value, ffsu_value, metric_value):
    product_id = (
        product.filter(c.product == product_value).select(c.product_id).collect().item()
    )
    date_id = (
        dates.filter(c.formatted_date == date_value).select(c.date_id).collect().item()
    )

    if len(ffsu_value) == 2:
        ffsu_value = [True, False]
    elif ffsu_value == ["FFSU"]:
        ffsu_value = [True]
    elif ffsu_value == ["Non-FFSU"]:
        ffsu_value = [False]
    else:
        ffsu_value = []
    df = map_df(date_id, product_id, ffsu_value)
    fig = create_choropleth(df, metric_value)

    return fig


@app.callback(
    Output("state-chart", "children"),
    Input("heatmap-graph", "clickData"),
    Input("product-dropdown", "value"),
)
def display_hover_data(clickData, product_value):
    if clickData is None:
        return html.Div(
            [
                html.Div(
                    [
                        html.I(
                            className="fas fa-chart-line",
                            style={
                                "fontSize": "3rem",
                                "color": "#64748b",
                                "marginBottom": "1rem",
                            },
                        ),
                        html.H4(
                            "Select a State to View Time Series",
                            style={"color": "#64748b", "marginBottom": "0.5rem"},
                        ),
                        html.P(
                            "Click on any state in the map above to see pricing trends over time",
                            style={"color": "#94a3b8", "fontSize": "1.1rem"},
                        ),
                    ],
                    style={
                        "textAlign": "center",
                        "padding": "3rem 2rem",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "8px",
                        "border": "2px dashed #e2e8f0",
                        "margin": "2rem 0",
                    },
                )
            ]
        )

    product_id = (
        product.filter(c.product == product_value).select(c.product_id).collect().item()
    )
    state = clickData["points"][0]["customdata"][0]
    data = state_data(state, product_id)

    return html.Div(
        [
            html.Div(
                [
                    html.H3(f"Time Series Analysis - {state}", className="chart-title"),
                    html.P(
                        "Historical pricing trends for the selected product and state",
                        className="chart-subtitle",
                    ),
                    dcc.Graph(
                        figure=plot_state_timeseries(data, state),
                        id="state-timeseries-graph",
                        className="detail-chart",
                    ),
                ],
                className="graph-container",
            )
        ]
    )


if __name__ == "__main__":
    app.run(debug=True, port=8052)
