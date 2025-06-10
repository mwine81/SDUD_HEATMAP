"""
Enhanced Appshell with professional header, navbar, and improved functionality.
Features: State selection, time series analysis, professional Mantine UI components,
error handling, and responsive design.
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import Dash, Input, Output, State, callback, dcc, no_update
from helper import MantineUI, dates, product, map_df, state_data, check_ffsu_value
from figures import create_choropleth, plot_state_timeseries, state_place_holder, empty_map_placeholder
from polars import col as c
from dash import html
import traceback

app = Dash(
    external_stylesheets=dmc.styles.ALL,
    assets_folder='assets',
    title="Drug Pricing Analytics"
)


layout = dmc.AppShell(
    children=[
        dmc.AppShellHeader(
            dmc.Group(
                [
                    dmc.Burger(id="burger", size="sm", hiddenFrom="sm", opened=False),
                    dmc.Group(
                        [
                            dmc.ThemeIcon(
                                DashIconify(icon="tabler:pill", width=28),
                                size="xl",
                                variant="light",
                                color="blue",
                                radius="md",
                            ),
                            dmc.Stack(
                                [
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
                                            "lineHeight": 1.2,
                                        },
                                    ),
                                    dmc.Text(
                                        "SDUD NADAC Analysis Dashboard",
                                        size="xs",
                                        c="gray",
                                        style={"marginTop": "-4px", "fontWeight": 500},
                                    ),
                                ],
                                gap="xs",
                            ),
                        ],
                        gap="md",
                        align="center",
                    ),
                ],
                h="100%",
                px="xl",
                align="center",
                justify="space-between",
            ),
            style={
                "background": "linear-gradient(135deg, #e0e7ff 0%, #f8fafc 100%)",
                "borderBottom": "2px solid #e2e8f0",
                "boxShadow": "0 4px 12px rgba(30, 64, 175, 0.06)",
                "height": "60px",
            },
        ),
        # ...existing navbar content...
        dmc.AppShellNavbar(
            id="navbar",
            children=[
                dmc.Stack(
                    [
                        # Header Section
                        dmc.Paper(
                            [
                                dmc.Group(
                                    [
                                        dmc.ThemeIcon(
                                            DashIconify(icon="tabler:dashboard", width=20),
                                            variant="light",
                                            color="blue",
                                            size="lg",
                                        ),
                                        dmc.Stack(
                                            [
                                                dmc.Text("Control Panel", fw="bold", size="md", c="blue"),
                                                dmc.Text("Configure analysis parameters", size="xs", c="gray"),
                                            ],
                                            gap="xs"
                                        ),
                                    ],
                                    gap="sm",
                                ),
                            ],
                            p="sm",
                            radius="md",
                            withBorder=True,
                            style={"backgroundColor": "#f8fafc"},
                        ),
                        
                        # Product Selection Section
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        DashIconify(icon="tabler:pill", width=16, color="#3b82f6"),
                                        dmc.Text("Product Selection", size="sm", fw="bold", c="dark"),
                                    ],
                                    gap="xs",
                                ),
                                MantineUI.product_dropdown(),
                                dmc.Text("Choose the pharmaceutical product to analyze", size="xs", c="gray"),
                            ],
                            gap="xs",
                        ),
                        
                        dmc.Divider(variant="dashed"),
                        
                        # Date Selection Section
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        DashIconify(icon="tabler:calendar", width=16, color="#3b82f6"),
                                        dmc.Text("Date Selection", size="sm", fw="bold", c="dark"),
                                    ],
                                    gap="xs",
                                ),
                                MantineUI.date_dropdown(),
                                dmc.Text("Select the time period for analysis", size="xs", c="gray"),
                            ],
                            gap="xs",
                        ),
                        
                        dmc.Divider(variant="dashed"),
                        
                        # Facility Type Section
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        DashIconify(icon="tabler:building-hospital", width=16, color="#3b82f6"),
                                        dmc.Text("Facility Type", size="sm", fw="bold", c="dark"),
                                    ],
                                    gap="xs",
                                ),
                                MantineUI.ffsu_dropdown(),
                                dmc.Text("Filter by Federal facility status", size="xs", c="gray"),
                            ],
                            gap="xs",
                        ),
                        
                        dmc.Divider(variant="dashed"),
                        
                        # Metric Selection Section
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        DashIconify(icon="tabler:chart-line", width=16, color="#3b82f6"),
                                        dmc.Text("Metric Selection", size="sm", fw="bold", c="dark"),
                                    ],
                                    gap="xs",
                                ),
                                MantineUI.metric_dropdown(),
                                dmc.Text("Choose the pricing metric to visualize", size="xs", c="gray"),
                            ],
                            gap="xs",
                        ),
                        
                        dmc.Space(h="md"),
                        
                        # Quick Tips Section
                        dmc.Paper(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Group(
                                            [
                                                DashIconify(icon="tabler:lightbulb", width=16, color="#f59e0b"),
                                                dmc.Text("Quick Tips", size="sm", fw="bold", c="orange"),
                                            ],
                                            gap="xs",
                                        ),
                                        dmc.List(
                                            [
                                                dmc.ListItem(
                                                    dmc.Text("Click states for time series", size="xs", c="dark")
                                                ),
                                                dmc.ListItem(
                                                    dmc.Text("Use zoom controls on charts", size="xs", c="dark")
                                                ),
                                                dmc.ListItem(
                                                    dmc.Text("Hover for detailed data", size="xs", c="dark")
                                                ),
                                            ],
                                            size="xs",
                                            withPadding=True,
                                        ),
                                    ],
                                    gap="xs",
                                ),
                            ],
                            p="sm",
                            radius="md",
                            style={"backgroundColor": "#fef3c7", "border": "1px solid #f59e0b"},
                        ),
                        
                        dmc.Space(h="xl"),
                        
                        # Footer
                        dmc.Text(
                            "Powered by 46Brooklyn",
                            size="xs",
                            c="gray",
                            ta="center",
                        ),
                    ],
                    gap="md",
                )
            ],
            p="md",
            style={
                "backgroundColor": "#f8fafc",
                "borderRight": "1px solid #e2e8f0",
                "minHeight": "100vh",
                "overflowY": "auto",
            },
        ),
        dmc.AppShellMain(
            [
                dcc.Loading(
                    id="loading-main",
                    children=[
                        dmc.Container(
                            [
                                # Page Header
                                dmc.Group(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Title("Drug Pricing Analytics", order=2, c="blue", fw="bold"),
                                                dmc.Text(
                                                    "Comprehensive analysis of NADAC vs payment pricing across states and time",
                                                    size="md",
                                                    c="gray",
                                                ),
                                            ],
                                            gap="xs",
                                        ),
                                        dmc.Group(
                                            [
                                                dmc.Badge("Live Data", color="green", variant="light"),
                                                dmc.Badge("SDUD Source", color="blue", variant="light"),
                                            ],
                                            gap="xs",
                                        ),
                                    ],
                                    justify="space-between",
                                    align="flex-start",
                                    mb="lg",
                                ),
                                
                                # Main Choropleth Card
                                dmc.Card(
                                    children=[
                                        dmc.CardSection(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Group(
                                                            [
                                                                DashIconify(icon="tabler:map", width=20, color="#3b82f6"),
                                                                dmc.Text(
                                                                    "State-by-State Analysis",
                                                                    size="lg",
                                                                    fw="bold",
                                                                ),
                                                            ],
                                                            gap="xs",
                                                        ),
                                                        dmc.Group(
                                                            [
                                                                dmc.Tooltip(
                                                                    dmc.ActionIcon(
                                                                        DashIconify(icon="tabler:info-circle", width=16),
                                                                        variant="subtle",
                                                                        color="gray",
                                                                        size="sm",
                                                                    ),
                                                                    label="Click on any state to view detailed time series analysis",
                                                                    position="left",
                                                                ),
                                                                dmc.Text(
                                                                    "Click on a state to view detailed trends",
                                                                    size="sm",
                                                                    c="gray",
                                                                ),
                                                            ],
                                                            gap="xs",
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                    align="center",
                                                )
                                            ],
                                            withBorder=True,
                                            inheritPadding=True,
                                            py="sm",
                                            style={"backgroundColor": "#f8fafc"},
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
                                                    "toImageButtonOptions": {
                                                        "format": "png",
                                                        "filename": "drug_pricing_choropleth",
                                                        "height": 500,
                                                        "width": 1000,
                                                        "scale": 2,
                                                    },
                                                },
                                            )
                                        ),
                                    ],
                                    withBorder=True,
                                    shadow="md",
                                    radius="md",
                                    id="map-card",
                                    style={"marginBottom": "1.5rem"},
                                ),
                                
                                # State Details Section
                                html.Div(id="state-chart"),
                                
                                # Hidden components for additional functionality
                                html.Div(id="notifications-container", style={"display": "none"}),
                                dcc.Interval(id="interval-component", interval=60000, n_intervals=0),
                                html.Div(id="dummy-output", style={"display": "none"}),
                                html.Div(id="viewport-size", style={"display": "none"}),
                            ],
                            size="xl",
                            px="md",
                        )
                    ],
                    type="default",
                    color="#3b82f6",
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
    prevent_initial_call=False,
)
def update_heatmap(product_value, date_value, ffsu_value, metric_value):
    """
    Update the choropleth heatmap based on user selections with comprehensive error handling.
    """
    try:
        # Validate inputs
        if not all([product_value, date_value, ffsu_value, metric_value]):
            return empty_map_placeholder()
        
        # Get product and date IDs with error handling
        try:
            product_id = (
                product.filter(c.product == product_value).select(c.product_id).collect().item()
            )
        except Exception as e:
            print(f"Error getting product_id for {product_value}: {e}")
            return empty_map_placeholder()
            
        try:
            date_id = (
                dates.filter(c.formatted_date == date_value).select(c.date_id).collect().item()
            )
        except Exception as e:
            print(f"Error getting date_id for {date_value}: {e}")
            return empty_map_placeholder()

        # Process FFSU value
        ffsu_value = check_ffsu_value(ffsu_value)
        if not ffsu_value:
            return empty_map_placeholder()

        # Get map data
        df = map_df(date_id, product_id, ffsu_value)
        
        # Check if data is available
        if df.collect().is_empty():
            return empty_map_placeholder()
            
        # Create choropleth
        fig = create_choropleth(df, metric_value)
        return fig
        
    except Exception as e:
        print(f"Error in update_heatmap: {e}")
        print(traceback.format_exc())
        return empty_map_placeholder()




@app.callback(
    Output("state-chart", "children"),
    [
        Input("heatmap-graph", "clickData"),
        Input("product-dropdown", "value"),
        Input("ffsu-checklist", "value"),
        Input("date-dropdown", "value"),
    ],
    prevent_initial_call=False,
)
def display_state_timeseries(clickData, product_value, ffsu_value, date_value):
    """
    Display comprehensive state timeseries analysis with professional Mantine styling.
    """
    try:
        # Show placeholder if no state is selected
        if clickData is None or "points" not in clickData or not clickData["points"]:
            return create_state_placeholder()
        
        # Validate inputs
        if not all([product_value, ffsu_value, date_value]):
            return create_error_card("Missing required parameters")
        
        # Get required data with error handling
        try:
            product_id = (
                product.filter(c.product == product_value).select(c.product_id).collect().item()
            )
        except Exception as e:
            return create_error_card(f"Error retrieving product data: {str(e)}")
            
        try:
            state = clickData["points"][0]["customdata"][0]
        except (KeyError, IndexError) as e:
            return create_error_card("Invalid state selection data")
            
        ffsu_value = check_ffsu_value(ffsu_value)
        if not ffsu_value:
            return create_error_card("Invalid FFSU selection")
        
        # Get state data
        data = state_data(state, product_id, ffsu_value)
        
        if data.collect().is_empty():
            return create_no_data_card(state)

        # Get summary data for the selected date
        try:
            summary_data = (
                data
                .filter(c.formatted_date == date_value)
                .collect()
                .to_dict(as_series=False)
            )
            
            if not summary_data or not summary_data.get('rx_count'):
                return create_no_data_card(state, date_value)
                
            # Extract metrics with safe defaults
            total_claims = int(summary_data.get('rx_count', [0])[0])
            pre_rebate_spend = float(summary_data.get('total', [0])[0])
            payment_per_unit = float(summary_data.get('payment_per_unit', [0])[0])
            nadac_per_unit = float(summary_data.get('nadac_per_unit', [0])[0])
            markup_per_unit = payment_per_unit - nadac_per_unit
            
        except Exception as e:
            print(f"Error processing summary data: {e}")
            # Use default values if summary data fails
            total_claims = 0
            pre_rebate_spend = 0
            payment_per_unit = 0
            nadac_per_unit = 0
            markup_per_unit = 0

        # Create professional time series card
        return create_timeseries_card(
            state, data, date_value, total_claims, pre_rebate_spend,
            payment_per_unit, nadac_per_unit, markup_per_unit, product_value
        )
        
    except Exception as e:
        print(f"Error in display_state_timeseries: {e}")
        print(traceback.format_exc())
        return create_error_card(f"Unexpected error: {str(e)}")


def create_state_placeholder():
    """Create a professional placeholder for state selection."""
    return dmc.Card([
        dmc.CardSection([
            dmc.Stack([
                dmc.Group([
                    dmc.ThemeIcon(
                        DashIconify(icon="tabler:chart-line", width=32),
                        size=60,
                        radius="xl",
                        variant="light",
                        color="blue",
                    ),
                    dmc.Stack([
                        dmc.Text(
                            "Select a State to View Time Series",
                            size="xl",
                            fw="bold",
                            c="blue"
                        ),
                        dmc.Text(
                            "Click on any state in the map above to see pricing trends over time",
                            size="md",
                            c="gray"
                        )
                    ], gap="xs")
                ], gap="lg", align="center"),
                
                dmc.Divider(color="blue"),
                
                dmc.Stack([
                    dmc.Text("📊 What you'll see:", size="sm", fw="bold", c="dark"),
                    dmc.List([
                        dmc.ListItem([
                            dmc.Text("Historical pricing trends for ", span=True, size="sm", c="gray"),
                            dmc.Text("NADAC vs Payment per Unit", span=True, size="sm", fw="bold", c="blue"),
                        ]),
                        dmc.ListItem([
                            dmc.Text("Interactive time series with ", span=True, size="sm", c="gray"),
                            dmc.Text("zoom controls", span=True, size="sm", fw="bold", c="blue"),
                        ]),
                        dmc.ListItem([
                            dmc.Text("Professional data visualization with ", span=True, size="sm", c="gray"),
                            dmc.Text("detailed tooltips", span=True, size="sm", fw="bold", c="blue"),
                        ]),
                    ], size="sm", c="gray", withPadding=True)
                ], gap="xs")
                
            ], gap="md")
        ], inheritPadding=True, py="xl")
    ],
    withBorder=True,
    shadow="md",
    radius="lg",
    style={
        "backgroundColor": "#f8fafc",
        "border": "2px dashed #cbd5e1"
    }
    )


def create_error_card(error_message):
    """Create a professional error display card."""
    return dmc.Card([
        dmc.CardSection([
            dmc.Alert(
                error_message,
                title="Error Loading Data",
                color="red",
                variant="light",
                icon=DashIconify(icon="tabler:alert-circle"),
            )
        ], inheritPadding=True, py="md")
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    mt="md"
    )


def create_no_data_card(state, date_value=None):
    """Create a professional no data display card."""
    message = f"No data available for {state}"
    if date_value:
        message += f" on {date_value}"
    
    return dmc.Card([
        dmc.CardSection([
            dmc.Stack([
                dmc.Group([
                    dmc.ThemeIcon(
                        DashIconify(icon="tabler:database-off", width=24),
                        size=50,
                        radius="xl",
                        variant="light",
                        color="orange"
                    ),
                    dmc.Stack([
                        dmc.Text(
                            f"No Data Available for {state}",
                            size="lg",
                            fw="bold",
                            c="orange"
                        ),
                        dmc.Text(
                            message,
                            size="md",
                            c="gray"
                        )
                    ], gap="xs")
                ], gap="lg", align="center"),
                
                dmc.Text(
                    "Try selecting a different state, date, or product combination.",
                    size="sm",
                    c="gray",
                    ta="center"
                )
            ], gap="md")
        ], inheritPadding=True, py="xl")
    ],
    withBorder=True,
    shadow="sm",
    radius="md",
    mt="md",
    style={"backgroundColor": "#fff7ed"}
    )


def create_timeseries_card(state, data, date_value, total_claims, pre_rebate_spend,
                          payment_per_unit, nadac_per_unit, markup_per_unit, product_value):
    """Create a comprehensive time series analysis card."""
    return dmc.Card(
        [
            # Header Section
            dmc.CardSection(
                [
                    dmc.Group(
                        [
                            dmc.Group([
                                dmc.Badge(
                                    state,
                                    size="lg",
                                    variant="light",
                                    color="blue",
                                    radius="md"
                                ),
                                dmc.Text(
                                    "Time Series Analysis",
                                    size="lg",
                                    fw="bold",
                                    c="blue"
                                ),
                            ], gap="sm"),
                            dmc.ActionIcon(
                                DashIconify(icon="tabler:chart-line", width=20),
                                variant="light",
                                color="blue",
                                size="lg",
                                radius="md"
                            )
                        ],
                        justify="space-between",
                        align="center",
                    ),
                    dmc.Text(
                        f"Historical pricing trends for {product_value} in {state}",
                        size="sm",
                        c="gray",
                        style={"lineHeight": 1.4}
                    )
                ],
                withBorder=True,
                inheritPadding=True,
                py="sm",
            ),
            
            # Summary Metrics Section
            dmc.CardSection(
                [
                    dmc.Group([
                        DashIconify(icon="tabler:calendar", width=16, color="#3b82f6"),
                        dmc.Text(f"Summary for {date_value}", size="md", fw="bold", c="blue"),
                    ], gap="xs", mb="sm"),
                    
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
                                            justify="center",
                                            align="center",
                                            h="100%",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#f0f9ff", "height": "80px"},
                                ),
                                span="auto",
                            ),
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Pre-Rebate Spend", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"${pre_rebate_spend:,.0f}", size="xl", fw="bold", c="blue", ta="center"),
                                            ],
                                            gap="xs",
                                            justify="center",
                                            align="center",
                                            h="100%",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#f0f9ff", "height": "80px"},
                                ),
                                span="auto",
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
                                            justify="center",
                                            align="center",
                                            h="100%",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#f0f9ff", "height": "80px"},
                                ),
                                span="auto",
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
                                            justify="center",
                                            align="center",
                                            h="100%",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#f0f9ff", "height": "80px"},
                                ),
                                span="auto",
                            ),
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Markup/Unit", size="xs", c="gray", ta="center"),
                                                dmc.Text(
                                                    f"${markup_per_unit:.2f}", 
                                                    size="xl", 
                                                    fw="bold", 
                                                    c="teal" if markup_per_unit > 0 else "red", 
                                                    ta="center"
                                                ),
                                            ],
                                            gap="xs",
                                            justify="center",
                                            align="center",
                                            h="100%",
                                        )
                                    ],
                                    withBorder=True,
                                    shadow="xs",
                                    radius="md",
                                    p="md",
                                    style={"background": "#ecfdf5" if markup_per_unit > 0 else "#fef2f2", "height": "80px"},
                                ),
                                span="auto",
                            ),
                        ],
                        gutter="md",
                    ),
                ],
                inheritPadding=True,
                py="md",
            ),
            
            # Chart Section
            dmc.CardSection(
                [
                    dcc.Graph(
                        figure=plot_state_timeseries(data, state),
                        id="state-timeseries-graph",
                        style={"height": "600px"},
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                            'toImageButtonOptions': {
                                'format': 'png',
                                'filename': f'timeseries_{state}_{product_value}',
                                'height': 600,
                                'width': 1000,
                                'scale': 2
                            }
                        }
                    )
                ],
                p=0,
            ),
            
            # Footer Section
            dmc.CardSection(
                [
                    dmc.Group(
                        [
                            dmc.Badge("NADAC", color="blue", variant="light"),
                            dmc.Text("vs", size="sm", c="gray"),
                            dmc.Badge("Payment per Unit", color="pink", variant="light"),
                            dmc.Divider(orientation="vertical"),
                            dmc.Text(
                                "Interactive chart with zoom and pan controls",
                                size="xs",
                                c="gray"
                            )
                        ],
                        gap="sm",
                        align="center"
                    )
                ],
                withBorder=True,
                inheritPadding=True,
                py="xs",
                style={"backgroundColor": "#f8fafc"}
            )
        ],
        withBorder=True,
        shadow="md",
        radius="md",
        mt="md",
    )


# Simplified notification system using console logging
def log_user_action(action, details=None):
    """Log user actions for debugging and analytics."""
    timestamp = html.Div(style={"display": "none"})  # Placeholder for timestamp
    message = f"User Action: {action}"
    if details:
        message += f" - {details}"
    print(message)


# Enhanced error handling wrapper
def safe_callback(func):
    """Decorator to add comprehensive error handling to callbacks."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in callback {func.__name__}: {e}")
            print(traceback.format_exc())
            return create_error_card(f"Error in {func.__name__}: {str(e)}")
    return wrapper


if __name__ == "__main__":
    app.run(debug=True, port=8052)
