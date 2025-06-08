def create_state_placeholder():
    """Create a professional placeholder for state selection."""
    return dmc.Card([
        dmc.CardSection([
            dmc.Stack([
                dmc.Group([
                    dmc.ThemeIcon(
                        dmc.Text("📈", size="xl"),
                        size=60,
                        radius="xl",
                        variant="light",
                        color="blue",
                        style={"fontSize": "24px"}
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
                            c="gray.6"
                        )
                    ], gap="xs")
                ], gap="lg", align="center"),
                
                dmc.Divider(color="blue.2"),
                
                dmc.Stack([
                    dmc.Text("📊 What you'll see:", size="sm", fw="bold", c="dark"),
                    dmc.List([
                        dmc.ListItem([
                            dmc.Text("Historical pricing trends for ", span=True, size="sm", c="gray.7"),
                            dmc.Text("NADAC vs Payment per Unit", span=True, size="sm", fw="bold", c="blue"),
                        ]),
                        dmc.ListItem([
                            dmc.Text("Interactive time series with ", span=True, size="sm", c="gray.7"),
                            dmc.Text("zoom controls", span=True, size="sm", fw="bold", c="blue"),
                        ]),
                        dmc.ListItem([
                            dmc.Text("Professional data visualization with ", span=True, size="sm", c="gray.7"),
                            dmc.Text("detailed tooltips", span=True, size="sm", fw="bold", c="blue"),
                        ]),
                    ], size="sm", c="gray.7", withPadding=True, icon=dmc.Text("•", c="blue"))
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

@app.callback(
    [Output('state-chart-card', 'children'),
     Output('state-chart-card', 'style')],
    [Input('heatmap-graph', 'clickData'),
     Input('product-dropdown', 'value')]
)
def display_state_timeseries(clickData, product_value):
    """
    Display time series chart for the selected state with professional Mantine styling.
    """
    if clickData is None:
        return create_state_placeholder(), {"display": "none"}
    
    try:
        # Get product ID
        product_id = product.filter(c.product == product_value).select(c.product_id).collect().item()
        
        # Extract state from click data
        state = clickData['points'][0]['customdata'][0]
        
        # Get state data
        data = state_data(state, product_id)
        
        # Check if data is available
        if data.collect().is_empty():
            no_data_content = dmc.Card([
                dmc.CardSection([
                    dmc.Stack([
                        dmc.Group([
                            dmc.ThemeIcon(
                                dmc.Text("📊", size="xl"),
                                size=60,
                                radius="xl",
                                variant="light",
                                color="orange"
                            ),
                            dmc.Stack([
                                dmc.Text(
                                    f"No Data Available for {state}",
                                    size="xl",
                                    fw="bold",
                                    c="orange"
                                ),
                                dmc.Text(
                                    "No historical pricing data found for this state and product combination",
                                    size="md",
                                    c="gray.6"
                                )
                            ], gap="xs")
                        ], gap="lg", align="center"),
                        
                        dmc.Divider(color="orange.3"),
                        
                        dmc.Text(
                            "Try selecting a different state or product to view time series data.",
                            size="sm",
                            c="gray.7",
                            ta="center"
                        )
                    ], gap="md")
                ], inheritPadding=True, py="xl")
            ],
            withBorder=True,
            shadow="sm",
            radius="lg",
            style={"backgroundColor": "#fff7ed"}
            )
            return no_data_content, {"display": "block"}
        
        # Create time series plot
        fig = plot_state_timeseries(data, state)
        
        # Create professional card content
        card_content = [
            dmc.CardSection([
                dmc.Stack([
                    dmc.Group([
                        dmc.Badge(
                            state,
                            size="lg",
                            variant="light",
                            color="blue",
                            radius="md"
                        ),
                        dmc.Group([
                            dmc.Text("Time Series Analysis", size="lg", fw="bold", c="dark"),
                            dmc.ActionIcon(
                                dmc.Text("📊", size="lg"),
                                variant="light",
                                color="blue",
                                size="lg",
                                radius="md"
                            )
                        ], gap="xs")
                    ], justify="space-between", align="center"),
                    
                    dmc.Text(
                        f"Historical pricing trends for {product_value} in {state}",
                        size="sm",
                        c="gray.6",
                        style={"lineHeight": 1.4}
                    )
                ], gap="xs")
            ], withBorder=True, inheritPadding=True, py="sm"),
            
            dmc.CardSection([
                dcc.Graph(
                    figure=fig,
                    id='state-timeseries-graph',
                    style={'height': '600px'},
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
            ], p=0),
            
            dmc.CardSection([
                dmc.Group([
                    dmc.Badge("NADAC", color="blue", variant="light"),
                    dmc.Text("vs", size="sm", c="gray"),
                    dmc.Badge("Payment per Unit", color="pink", variant="light"),
                    dmc.Divider(orientation="vertical"),
                    dmc.Text(
                        "Interactive chart with zoom and pan controls",
                        size="xs",
                        c="gray.6"
                    )
                ], gap="sm", align="center")
            ], withBorder=True, inheritPadding=True, py="xs", style={"backgroundColor": "#f8fafc"})
        ]
        
        return card_content, {"display": "block"}
        
    except Exception as e:
        error_content = dmc.Card([
            dmc.CardSection([
                dmc.Alert(
                    f"Error loading time series data: {str(e)}",
                    title="Data Error",
                    color="red",
                    variant="light"
                )
            ], inheritPadding=True, py="md")
        ])
        return error_content, {"display": "block"}