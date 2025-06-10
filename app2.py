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
                                DashIconify(icon="tabler:chart-line", width=32),
                                size="xl",
                                variant="light",
                                color="orange",
                                radius="md",
                                style={"backgroundColor": "white"},
                            ),
                            dmc.Stack(
                                [
                                    dmc.Title(
                                        "46brooklyn Research",
                                        order=3,
                                        className="brooklyn-title",
                                        style={
                                            "fontSize": "1.75rem",
                                            "marginBottom": "0",
                                            "lineHeight": 1.2,
                                            "color": "white",
                                            "fontFamily": "Source Sans Pro, sans-serif",
                                            "fontWeight": 700,
                                        },
                                    ),
                                    dmc.Text(
                                        "Drug Pricing Analytics Dashboard",
                                        size="sm",
                                        className="brooklyn-subtitle",
                                        style={
                                            "marginTop": "-2px",
                                            "color": "rgba(255, 255, 255, 0.8)",
                                        },
                                    ),
                                ],
                                gap="xs",
                            ),
                        ],
                        gap="md",
                        align="center",
                    ),
                    dmc.Group(
                        [
                            dmc.Badge("NADAC Data", color="orange", variant="light", size="md"),
                            dmc.Badge("Live Dashboard", color="gray", variant="outline", size="md", style={"color": "white", "borderColor": "white"}),
                        ],
                        gap="sm",
                    ),
                ],
                h="100%",
                px="xl",
                align="center",
                justify="space-between",
                wrap="nowrap",
            ),
            className="brooklyn-header",
            style={
                "height": "70px",
                "background": "linear-gradient(135deg, #1a365d 0%, #2c5282 100%)",
                "borderBottom": "3px solid #ed8936",
            },
        ),
        dmc.AppShellNavbar(
            id="navbar",
            children=[
                dmc.Stack(
                    [
                        # 46Brooklyn Style Header Section
                        dmc.Paper(
                            [
                                dmc.Group(
                                    [
                                        dmc.ThemeIcon(
                                            DashIconify(icon="tabler:adjustments-horizontal", width=20),
                                            variant="light",
                                            color="orange",
                                            size="lg",
                                        ),
                                        dmc.Stack(
                                            [
                                                dmc.Text("Dashboard Controls", fw="bold", size="md", className="brooklyn-brand"),
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
                            className="brooklyn-viz-container",
                        ),
                        
                        # Product Selection Section - 46Brooklyn Style
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        DashIconify(icon="tabler:pill", width=16, color="#1a365d"),
                                        dmc.Text("Product Selection", size="sm", fw="bold", className="brooklyn-brand"),
                                    ],
                                    gap="xs",
                                ),
                                MantineUI.product_dropdown(),
                                dmc.Text("Choose pharmaceutical product for analysis", size="xs", c="gray"),
                            ],
                            gap="xs",
                        ),
                        
                        dmc.Divider(color="gray", variant="dashed"),
                        
                        # Date Selection Section
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        DashIconify(icon="tabler:calendar-stats", width=16, color="#1a365d"),
                                        dmc.Text("Time Period", size="sm", fw="bold", className="brooklyn-brand"),
                                    ],
                                    gap="xs",
                                ),
                                MantineUI.date_dropdown(),
                                dmc.Text("Select reporting quarter", size="xs", c="gray"),
                            ],
                            gap="xs",
                        ),
                        
                        dmc.Divider(color="gray", variant="dashed"),
                        
                        # Facility Type Section
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        DashIconify(icon="tabler:building-hospital", width=16, color="#1a365d"),
                                        dmc.Text("Facility Status", size="sm", fw="bold", className="brooklyn-brand"),
                                    ],
                                    gap="xs",
                                ),
                                MantineUI.ffsu_dropdown(),
                                dmc.Text("Federal vs Non-Federal facilities", size="xs", c="gray"),
                            ],
                            gap="xs",
                        ),
                        
                        dmc.Divider(color="gray", variant="dashed"),
                        
                        # Metric Selection Section
                        dmc.Stack(
                            [
                                dmc.Group(
                                    [
                                        DashIconify(icon="tabler:chart-bar", width=16, color="#1a365d"),
                                        dmc.Text("Pricing Metric", size="sm", fw="bold", className="brooklyn-brand"),
                                    ],
                                    gap="xs",
                                ),
                                MantineUI.metric_dropdown(),
                                dmc.Text("Choose visualization metric", size="xs", c="gray"),
                            ],
                            gap="xs",
                        ),
                        
                        dmc.Space(h="md"),
                        
                        # 46Brooklyn Research Info Section
                        dmc.Paper(
                            [
                                dmc.Stack(
                                    [
                                        dmc.Group(
                                            [
                                                DashIconify(icon="tabler:info-circle", width=16, color="#ed8936"),
                                                dmc.Text("About This Dashboard", size="sm", fw="bold", className="brooklyn-accent"),
                                            ],
                                            gap="xs",
                                        ),
                                        dmc.List(
                                            [
                                                dmc.ListItem(
                                                    dmc.Text("NADAC pricing data from CMS", size="xs", c="dark")
                                                ),
                                                dmc.ListItem(
                                                    dmc.Text("State utilization comparisons", size="xs", c="dark")
                                                ),
                                                dmc.ListItem(
                                                    dmc.Text("Interactive time series analysis", size="xs", c="dark")
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
                            style={"backgroundColor": "#fef5e7", "border": "1px solid #ed8936"},
                        ),
                        
                        dmc.Space(h="lg"),
                        
                        # 46Brooklyn Footer
                        dmc.Stack(
                            [
                                dmc.Text(
                                    "46brooklyn Research",
                                    size="sm",
                                    fw="bold",
                                    ta="center",
                                    className="brooklyn-brand",
                                ),
                                dmc.Text(
                                    "Ohio 501(c)(3) Public Charity",
                                    size="xs",
                                    c="gray",
                                    ta="center",
                                ),
                            ],
                            gap="xs",
                        ),
                    ],
                    gap="md",
                )
            ],
            p="md",
            className="brooklyn-navbar",
            style={
                "backgroundColor": "#f7fafc",
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
                                # 46Brooklyn Style Page Header
                                dmc.Stack(
                                    [
                                        dmc.Group(
                                            [
                                                dmc.Stack(
                                                    [
                                                        dmc.Title("NADAC Drug Pricing Dashboard", order=2, className="brooklyn-brand", fw="bold"),
                                                        dmc.Text(
                                                            "Explore state-by-state Medicaid drug pricing using CMS NADAC data",
                                                            size="md",
                                                            c="gray",
                                                            style={"maxWidth": "600px"},
                                                        ),
                                                    ],
                                                    gap="xs",
                                                ),
                                                dmc.Group(
                                                    [
                                                        dmc.Badge("46brooklyn Research", color="orange", variant="filled", size="lg"),
                                                        dmc.Badge("CMS NADAC", variant="outline", size="md", style={"borderColor": "#1a365d", "color": "#1a365d"}),
                                                    ],
                                                    gap="sm",
                                                ),
                                            ],
                                            justify="space-between",
                                            align="flex-start",
                                            mb="xl",
                                        ),
                                        
                                        # 46Brooklyn Style Instructions
                                        dmc.Paper(
                                            [
                                                dmc.Group(
                                                    [
                                                        DashIconify(icon="tabler:info-circle", width=20, color="#ed8936"),
                                                        dmc.Text("How to Use This Dashboard", fw="bold", className="brooklyn-accent"),
                                                    ],
                                                    gap="xs",
                                                    mb="sm",
                                                ),
                                                dmc.Text(
                                                    "Select filters from the left panel, then click on any state in the map below to view detailed pricing trends over time. Compare NADAC reference prices with actual Medicaid payments.",
                                                    size="sm",
                                                    c="dark",
                                                ),
                                            ],
                                            p="md",
                                            radius="md",
                                            withBorder=True,
                                            style={"backgroundColor": "#fef5e7", "borderColor": "#ed8936"},
                                            mb="lg",
                                        ),
                                    ],
                                    gap="md",
                                ),
                                
                                # Main Choropleth Card - 46Brooklyn Style
                                dmc.Card(
                                    children=[
                                        dmc.CardSection(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Group(
                                                            [
                                                                DashIconify(icon="tabler:map-2", width=24, color="white"),
                                                                dmc.Text(
                                                                    "State-by-State Drug Pricing Analysis",
                                                                    size="lg",
                                                                    fw="bold",
                                                                    style={"color": "white"},
                                                                ),
                                                            ],
                                                            gap="sm",
                                                        ),
                                                        dmc.Group(
                                                            [
                                                                dmc.Tooltip(
                                                                    dmc.ActionIcon(
                                                                        DashIconify(icon="tabler:help", width=16),
                                                                        variant="subtle",
                                                                        size="sm",
                                                                        style={"color": "white"},
                                                                    ),
                                                                    label="Click any state to view detailed time series analysis",
                                                                    position="left",
                                                                ),
                                                                dmc.Text(
                                                                    "Interactive Map",
                                                                    size="sm",
                                                                    style={"color": "rgba(255, 255, 255, 0.8)"},
                                                                ),
                                                            ],
                                                            gap="xs",
                                                        ),
                                                    ],
                                                    justify="space-between",
                                                    align="center",
                                                )
                                            ],
                                            className="brooklyn-card-header",
                                            withBorder=True,
                                            inheritPadding=True,
                                            py="md",
                                        ),
                                        dmc.CardSection(
                                            dcc.Graph(
                                                id="heatmap-graph",
                                                style={"height": "520px"},
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
                                                        "filename": "46brooklyn_drug_pricing_analysis",
                                                        "height": 520,
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
                                    style={"marginBottom": "2rem"},
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
    header={"height": 70},
    padding="md",
    navbar={
        "width": 320,
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
    """Create a 46Brooklyn-themed placeholder for state selection."""
    return dmc.Card([
        dmc.CardSection([
            dmc.Stack([
                dmc.Group([
                    dmc.ThemeIcon(
                        DashIconify(icon="tabler:chart-line", width=32),
                        size=60,
                        radius="xl",
                        variant="light",
                        color="orange",
                    ),
                    dmc.Stack([
                        dmc.Text(
                            "Select a State for Detailed Analysis",
                            size="xl",
                            fw="bold",
                            className="brooklyn-brand"
                        ),
                        dmc.Text(
                            "Click on any state in the map above to explore NADAC vs payment pricing trends",
                            size="md",
                            c="gray"
                        )
                    ], gap="xs")
                ], gap="lg", align="center"),
                
                dmc.Divider(color="orange"),
                
                dmc.Stack([
                    dmc.Text("📊 46brooklyn Analysis Features:", size="sm", fw="bold", className="brooklyn-accent"),
                    dmc.List([
                        dmc.ListItem([
                            dmc.Text("Historical pricing trends comparing ", span=True, size="sm", c="gray"),
                            dmc.Text("NADAC reference prices", span=True, size="sm", fw="bold", className="brooklyn-brand"),
                            dmc.Text(" with actual payments", span=True, size="sm", c="gray"),
                        ]),
                        dmc.ListItem([
                            dmc.Text("Interactive time series with ", span=True, size="sm", c="gray"),
                            dmc.Text("quarterly data points", span=True, size="sm", fw="bold", className="brooklyn-brand"),
                        ]),
                        dmc.ListItem([
                            dmc.Text("Medicaid spending insights from ", span=True, size="sm", c="gray"),
                            dmc.Text("CMS utilization data", span=True, size="sm", fw="bold", className="brooklyn-brand"),
                        ]),
                    ], size="sm", c="gray", withPadding=True)
                ], gap="xs")
                
            ], gap="md")
        ], inheritPadding=True, py="xl")
    ],
    withBorder=True,
    shadow="md",
    radius="md",
    style={
        "backgroundColor": "#fef5e7",
        "border": "2px dashed #ed8936"
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
    """Create a comprehensive 46Brooklyn-styled time series analysis card."""
    return dmc.Card(
        [
            # 46Brooklyn Header Section
            dmc.CardSection(
                [
                    dmc.Group(
                        [
                            dmc.Group([
                                dmc.Badge(
                                    state,
                                    size="lg",
                                    variant="filled",
                                    color="orange",
                                    radius="md"
                                ),
                                dmc.Text(
                                    "46brooklyn Drug Pricing Analysis",
                                    size="lg",
                                    fw="bold",
                                    style={"color": "white"}
                                ),
                            ], gap="sm"),
                            dmc.ActionIcon(
                                DashIconify(icon="tabler:chart-dots", width=20),
                                variant="subtle",
                                size="lg",
                                radius="md",
                                style={"color": "white"}
                            )
                        ],
                        justify="space-between",
                        align="center",
                    ),
                    dmc.Text(
                        f"NADAC vs Payment Analysis: {product_value} in {state}",
                        size="sm",
                        style={"color": "rgba(255, 255, 255, 0.8)", "lineHeight": 1.4}
                    )
                ],
                className="brooklyn-card-header",
                withBorder=True,
                inheritPadding=True,
                py="md",
            ),
            
            # 46Brooklyn Summary Metrics Section
            dmc.CardSection(
                [
                    dmc.Group([
                        DashIconify(icon="tabler:calendar-stats", width=16, color="#ed8936"),
                        dmc.Text(f"Quarterly Summary: {date_value}", size="md", fw="bold", className="brooklyn-accent"),
                    ], gap="xs", mb="md"),
                    
                    dmc.Grid(
                        [
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Total Claims", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"{total_claims:,.0f}", size="xl", fw="bold", className="brooklyn-brand", ta="center"),
                                            ],
                                            gap="xs",
                                            justify="center",
                                            align="center",
                                            h="100%",
                                        )
                                    ],
                                    className="brooklyn-metric-card",
                                    style={"height": "90px"},
                                ),
                                span="auto",
                            ),
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Total Spend", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"${pre_rebate_spend:,.0f}", size="xl", fw="bold", className="brooklyn-brand", ta="center"),
                                            ],
                                            gap="xs",
                                            justify="center",
                                            align="center",
                                            h="100%",
                                        )
                                    ],
                                    className="brooklyn-metric-card",
                                    style={"height": "90px"},
                                ),
                                span="auto",
                            ),
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Payment/Unit", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"${payment_per_unit:.2f}", size="xl", fw="bold", className="brooklyn-brand", ta="center"),
                                            ],
                                            gap="xs",
                                            justify="center",
                                            align="center",
                                            h="100%",
                                        )
                                    ],
                                    className="brooklyn-metric-card",
                                    style={"height": "90px"},
                                ),
                                span="auto",
                            ),
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("NADAC/Unit", size="xs", c="gray", ta="center"),
                                                dmc.Text(f"${nadac_per_unit:.2f}", size="xl", fw="bold", className="brooklyn-brand", ta="center"),
                                            ],
                                            gap="xs",
                                            justify="center",
                                            align="center",
                                            h="100%",
                                        )
                                    ],
                                    className="brooklyn-metric-card",
                                    style={"height": "90px"},
                                ),
                                span="auto",
                            ),
                            dmc.GridCol(
                                dmc.Paper(
                                    [
                                        dmc.Stack(
                                            [
                                                dmc.Text("Pricing Differential", size="xs", c="gray", ta="center"),
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
                                    style={
                                        **{"height": "90px"},
                                        "background": "#e6fffa" if markup_per_unit > 0 else "#fef2f2",
                                        "border": f"1px solid {'#38b2ac' if markup_per_unit > 0 else '#f56565'}",
                                        "borderLeft": f"4px solid {'#38b2ac' if markup_per_unit > 0 else '#f56565'}",
                                        "borderRadius": "6px",
                                        "padding": "1rem",
                                        "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
                                    },
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
            
            # Chart Section with 46Brooklyn Styling
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
                                'filename': f'46brooklyn_timeseries_{state}_{product_value}',
                                'height': 600,
                                'width': 1000,
                                'scale': 2
                            }
                        }
                    )
                ],
                p=0,
            ),
            
            # 46Brooklyn Footer Section
            dmc.CardSection(
                [
                    dmc.Group(
                        [
                            dmc.Badge("NADAC Reference", color="orange", variant="light"),
                            dmc.Text("vs", size="sm", c="gray"),
                            dmc.Badge("Medicaid Payment", variant="outline", style={"borderColor": "#1a365d", "color": "#1a365d"}),
                            dmc.Divider(orientation="vertical"),
                            dmc.Text(
                                "46brooklyn Research • Data-driven drug pricing insights",
                                size="xs",
                                className="brooklyn-brand"
                            )
                        ],
                        gap="sm",
                        align="center"
                    )
                ],
                withBorder=True,
                inheritPadding=True,
                py="sm",
                style={"backgroundColor": "#f7fafc"}
            )
        ],
        withBorder=True,
        shadow="lg",
        radius="md",
        mt="lg",
        style={"border": "1px solid #e2e8f0"}
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
    app.run(debug=True, port=8053)
