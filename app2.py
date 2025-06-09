"""
Basic Appshell with header and navbar that collapses on mobile.
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import Dash, Input, Output, State, callback, dcc
from helper import MantineUI, dates, product, map_df, state_data, check_ffsu_value
from figures import create_choropleth, plot_state_timeseries, state_place_holder, empty_map_placeholder
from polars import col as c
from dash import html

app = Dash(external_stylesheets=dmc.styles.ALL)


layout = dmc.AppShell(
    children=[
        dmc.AppShellHeader(
            dmc.Group(
                [
                    dmc.Burger(id="burger", size="sm", hiddenFrom="sm", opened=False),
                    html.Img(
                        src="/assets/logo.png",
                        style={
                            "height": "40px",
                            "marginRight": "16px",
                            "verticalAlign": "middle",
                            "borderRadius": "8px",
                            "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
                            "background": "#fff",
                            "padding": "4px",
                        },
                    ),
                    dmc.Title(
                        "Drug Pricing Analytics",
                        c="blue",
                        order=3,
                        style={
                            "fontWeight": 800,
                            "letterSpacing": "0.02em",
                            "fontFamily": "Inter, sans-serif",
                            "fontSize": "1.7rem",
                            "marginBottom": "0",
                        },
                    ),
                ],
                h="100%",
                px="md",
                align="center",
                gap="xs",
            ),
            style={
                "background": "linear-gradient(90deg, #e0e7ff 0%, #f8fafc 100%)",
                "borderBottom": "1px solid #e2e8f0",
                "boxShadow": "0 2px 8px rgba(30, 64, 175, 0.04)",
                "height": "60px",
                "padding": "0 2rem",
            },
        ),
        dmc.AppShellNavbar(
            id="navbar",
            children=[
                dmc.Stack(
                    [
                        dmc.Group(
                            [
                                dmc.ThemeIcon(
                                    DashIconify(icon="tabler:database", width=24),
                                    variant="light",
                                    color="blue",
                                    size=36,
                                ),
                                dmc.Text("Navigation", fw=700, size="lg", c="blue"),
                            ],
                            mb="md",
                        ),
                        dmc.Divider(),
                        dmc.Text("Select Product", size="sm", c="gray"),
                        MantineUI.product_dropdown(),
                        dmc.Text("Select Date", size="sm", c="gray", mt="sm"),
                        MantineUI.date_dropdown(),
                        dmc.Text("FFSU Filter", size="sm", c="gray", mt="sm"),
                        MantineUI.ffsu_dropdown(),
                        dmc.Text("Metric", size="sm", c="gray", mt="sm"),
                        MantineUI.metric_dropdown(),
                        dmc.Space(h=16),
                        dmc.Divider(),
                        dmc.Text(
                            "Powered by 46Brooklyn",
                            size="xs",
                            c="dimmed",
                            mt="md",
                        ),
                    ],
                    gap="xs",
                )
            ],
            p="md",
            style={
                "backgroundColor": "#f1f5f9",
                "borderRight": "1px solid #e2e8f0",
                "minHeight": "100vh",
            },
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

    ffsu_value = check_ffsu_value(ffsu_value)

    df = map_df(date_id, product_id, ffsu_value)
    if df.collect().is_empty():
        return empty_map_placeholder()
    fig = create_choropleth(df, metric_value)
    
    return fig




@app.callback(
    Output("state-chart", "children"),
    Input("heatmap-graph", "clickData"),
    Input("product-dropdown", "value"),
    Input("ffsu-checklist", "value"),
    Input("date-dropdown", "value"),
)
def display_hover_data(clickData, product_value, ffsu_value, date_value):
    # If the heatmap-graph is not present in the layout, this callback won't be triggered.
    # But to be extra safe, check for clickData structure.
    if clickData is None or "points" not in clickData or not clickData["points"]:
        return state_place_holder()
    print(date_value)
    product_id = (
        product.filter(c.product == product_value).select(c.product_id).collect().item()
    )
    state = clickData["points"][0]["customdata"][0]
    ffsu_value = check_ffsu_value(ffsu_value)
    data = state_data(state, product_id, ffsu_value)
    
    if data.collect().is_empty():
        return state_place_holder()
    data.collect().glimpse()
    summary_data = (
    data
    .filter(c.formatted_date == date_value)
    .collect()
    .to_dict(as_series=False)
    )
    
    # int
    total_claims = (summary_data['rx_count'][0])
    
    # money
    pre_rebate_spend = (summary_data['total'][0])
    payment_per_unit = (summary_data['payment_per_unit'][0])
    nadac_per_unit = (summary_data['nadac_per_unit'][0])
    markup_per_unit = payment_per_unit - nadac_per_unit    
    time_series_div = dmc.Card(
        [
            dmc.CardSection(
                [
                    dmc.Group(
                        [
                            dmc.Text(
                                f"Time Series Analysis - {state}",
                                size="lg",
                                fw="bold",
                                c="blue"
                            ),
                            dmc.Text(
                                "Historical pricing trends for the selected product and state",
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
                [
                    dmc.Text(f"Summary for {date_value}", size="md", fw="bold", c="blue", mb="sm"),
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Total Claims", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"{total_claims:,.0f}", size="xl", fw="bold", c="blue", ta="center"),
                                            ],
                                            gap="xs",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#f8fafc", "height": "80px", "display": "flex", "alignItems": "center"},
                                ),
                                span='auto',
                            ),
                                                        dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Pre Rebated Spend", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"${pre_rebate_spend:,.0f}", size="xl", fw="bold", c="blue", ta="center"),
                                            ],
                                            gap="xs",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#f8fafc", "height": "80px", "display": "flex", "alignItems": "center"},
                                ),
                                span='auto',
                            ),
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Payment/Unit", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"${payment_per_unit:.2f}", size="xl", fw="bold", c="blue", ta="center"),
                                            ],
                                            gap="xs",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#f8fafc", "height": "80px", "display": "flex", "alignItems": "center"},
                                ),
                                span='auto',
                            ),
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("NADAC/Unit", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"${nadac_per_unit:.2f}", size="xl", fw="bold", c="blue", ta="center"),
                                            ],
                                            gap="xs",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#f8fafc", "height": "80px", "display": "flex", "alignItems": "center"},
                                ),
                                span='auto',
                            ),
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Markup/Unit", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"${markup_per_unit:.2f}", size="xl", fw="bold", c="teal", ta="center"),
                                            ],
                                            gap="xs",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#e6fffa", "height": "80px", "display": "flex", "alignItems": "center"},
                                ),
                                span='auto',
                            ),
                        ],
                        gutter="md",
                    ),
                ],
                inheritPadding=True,
                py="md",
            ),
            dmc.CardSection(
                dcc.Graph(
                    figure=plot_state_timeseries(data, state),
                    id="state-timeseries-graph",
                    style={"height": "600px"},
                )
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        mt="md",
    )

    return time_series_div


if __name__ == "__main__":
    app.run(debug=True, port=8052)
