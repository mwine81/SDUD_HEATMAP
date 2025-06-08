"""
Basic Appshell with header and  navbar that collapses on mobile.
"""

import dash_mantine_components as dmc

from dash import Dash, Input, Output, State, callback, dcc
from helper import MantineUI, dates, product, map_df
from figures import create_choropleth
from polars import col as c

app = Dash(external_stylesheets=dmc.styles.ALL)



layout = dmc.AppShell(
    children=[
        dmc.AppShellHeader(
            dmc.Group(
                [
                    dmc.Burger(id="burger", size="sm", hiddenFrom="sm", opened=False),
                    #dmc.Image(src=logo, h=40),
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
        dmc.AppShellMain([
            dmc.Container([
                dmc.Title("Drug Pricing Analytics", order=2, mb="md", c="blue"),
                dmc.Card(
                    children=[
                        dmc.CardSection([
                            dmc.Group([
                                dmc.Text("State-by-State Analysis", size="lg", fw="bold"),
                                dmc.Text("Click on a state to view detailed trends", size="sm", c="gray")
                            ], justify="space-between", align="flex-start")
                        ], withBorder=True, inheritPadding=True, py="xs"),
                        dmc.CardSection(
                            id='heatmap-container',
                            p=0
                        ),
                    ],
                    withBorder=True,
                    shadow="sm",
                    radius="md",
                    id='map-card'
                ),
            ], size="xl", px=0)
        ]),
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
    Output('heatmap-container', 'children'),
    [Input('product-dropdown', 'value'),
     Input('date-dropdown', 'value'),
     Input('ffsu-checklist', 'value'),
     Input('metric-dropdown', 'value')]
)
def update_heatmap(product_value, date_value, ffsu_value, metric_value):
    product_id = product.filter(c.product == product_value).select(c.product_id).collect().item()
    date_id = dates.filter(c.formatted_date == date_value).select(c.date_id).collect().item()
    
    if len(ffsu_value) == 2:
        ffsu_value = [True, False]
    elif ffsu_value == ['FFSU']:
        ffsu_value = [True]
    elif ffsu_value == ['Non-FFSU']:
        ffsu_value = [False]
    else:
        ffsu_value = []
    df = map_df(date_id, product_id, ffsu_value)

    if df.collect().is_empty():
        return dmc.Center(
            dmc.Card(
            [
                dmc.CardSection(
                    dmc.Group([
                        #dmc.IconAlertCircleFilled(size=32, color="red", radius="xl", size="lg", variant="light"),
                        dmc.Text(
                            "No data available for the selected parameters.",
                            size="lg",
                            fw="bold",
                            c="red"
                        ),
                    ], gap="md", align="center"),
                    withBorder=False,
                    inheritPadding=True,
                    py="md"
                ),
                dmc.Text(
                    "Please adjust your filters and try again.",
                    size="sm",
                    #c="dimmed",
                    ta="center",
                    mt="xs"
                ),
            ],
            withBorder=True,
            shadow="sm",
            radius="md",
            p="lg",
            style={"maxWidth": 400}
            ),
            style={"height": "400px"}
        )

    fig = create_choropleth(df, metric_value)
    div = dcc.Graph(
        id='heatmap-graph',
        style={'height': '500px'},
        figure=fig,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
        }
    )

    return div

if __name__ == "__main__":
    app.run(debug=True, port=8052)