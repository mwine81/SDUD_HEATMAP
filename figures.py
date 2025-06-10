import polars as pl
import plotly.express as px
from polars import col as c
from dash import html

# 46Brooklyn Research Brand Colors
BROOKLYN_PRIMARY = "#1a365d"     # Deep navy blue
BROOKLYN_SECONDARY = "#2c5282"   # Medium blue
BROOKLYN_ACCENT = "#ed8936"      # Orange accent
BROOKLYN_TEXT = "#1a202c"        # Dark gray text
BROOKLYN_MUTED = "#718096"       # Light gray text
BROOKLYN_BACKGROUND = "#f7fafc"  # Light background
BROOKLYN_WHITE = "#ffffff"       # Pure white

def create_choropleth(data: pl.LazyFrame, metric: str):
    """
    Create a professional choropleth map optimized for Mantine cards.

    Args:
        data (pl.LazyFrame): Polars LazyFrame containing the data.
        metric (str): The metric to visualize on the map.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object for the choropleth map.
    """
    # Currency fields for proper formatting
    currency_fields = {'total', 'medicaid_reimbursed', 'nadac', 'markup_per_unit', 'payment_per_unit', 'nadac_per_unit'}
    
    # Collect the data
    df = data.collect()
    
    # Determine if the metric is a currency field
    is_currency = metric in currency_fields
    
    # 46Brooklyn Research color scale - professional navy/orange theme
    if is_currency:
        # Custom color scale for 46Brooklyn - navy to orange gradient
        color_scale = [[0.0, "#f7fafc"], [0.25, "#90cdf4"], [0.5, "#2c5282"], [0.75, "#1a365d"], [1.0, "#ed8936"]]
    else:
        # Blue gradient for non-currency metrics
        color_scale = [[0.0, "#f7fafc"], [0.25, "#bee3f8"], [0.5, "#63b3ed"], [0.75, "#2c5282"], [1.0, "#1a365d"]]
    
    # Create the choropleth map
    fig = px.choropleth(
        df, 
        locations='state', 
        locationmode="USA-states", 
        color=metric, 
        scope="usa",
        color_continuous_scale=color_scale,
        custom_data=['state'],
    )
    
    # Calculate min/max for colorbar ticks with null safety
    min_val_raw = df[metric].min() 
    max_val_raw = df[metric].max()
    nticks = 4  # Limit to 4 ticks to avoid overlap
    
    if min_val_raw is None or max_val_raw is None:
        tickvals = [0]
    else:
        min_val = float(min_val_raw)
        max_val = float(max_val_raw)
        if min_val == max_val:
            tickvals = [min_val]
        else:
            tickvals = [round(min_val + i * (max_val - min_val) / (nticks - 1), 2) for i in range(nticks)]
    
    # Enhanced styling for 46Brooklyn Research professional appearance
    fig.update_layout(
        title=None,
        showlegend=False,
        width=None,
        height=500,
        margin=dict(l=5, r=5, t=10, b=70),
        font=dict(
            family="Source Sans Pro, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            size=12,
            color=BROOKLYN_TEXT
        ),
        coloraxis_colorbar={
            'title': {
                'text': metric.replace('_', ' ').title(),
                'font': {'size': 14, 'color': BROOKLYN_TEXT, 'family': 'Source Sans Pro, Inter, sans-serif'},
                'side': 'bottom'
            },
            'tickfont': {'size': 16, 'color': BROOKLYN_MUTED},
            'orientation': 'h',
            'x': 0.5,
            'y': -0.15,
            'xanchor': 'center',
            'lenmode': 'fraction',
            'len': 0.75,
            'thickness': 18,
            'bgcolor': 'rgba(247, 250, 252, 0.95)',
            'bordercolor': BROOKLYN_SECONDARY,
            'borderwidth': 1,
            'tickformat': '$,.2f' if is_currency else ',.1f',
            'tickmode': 'array',
            'tickvals': tickvals,
            'nticks': nticks
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor=BROOKLYN_MUTED,
            coastlinewidth=0.8,
            projection_type='albers usa',
            bgcolor='rgba(0,0,0,0)',
            showlakes=True,
            lakecolor='#e0f2fe',
            showrivers=False,
            showland=True,
            landcolor=BROOKLYN_BACKGROUND,
            showsubunits=True,
            subunitcolor=BROOKLYN_SECONDARY,
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        autosize=True,
    )
    
    fig.update_traces(
        hovertemplate='<b>%{location}</b><br>' +
                     f'<span style="color: {BROOKLYN_MUTED};">{metric.replace("_", " ").title()}:</span> ' +
                     (f'<span style="color: {BROOKLYN_ACCENT}; font-weight: 600;">$%{{z:,.2f}}</span>' if is_currency else 
                      f'<span style="color: {BROOKLYN_ACCENT}; font-weight: 600;">%{{z:,.2f}}</span>') +
                     '<extra></extra>',
        marker_line_color='white',
        marker_line_width=1.5,
        zmid=None,
    )
    
    fig.add_annotation(
        text=f"<b>{metric.replace('_', ' ').title()}</b> by State",
        xref="paper", yref="paper",
        x=0.5, y=0.98,
        xanchor="center", yanchor="top",
        showarrow=False,
        font=dict(size=16, color=BROOKLYN_PRIMARY, family="Source Sans Pro, Inter, sans-serif"),
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor=BROOKLYN_SECONDARY,
        borderwidth=1,
        borderpad=8
    )
    
    fig.update_layout(
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor=BROOKLYN_SECONDARY,
            font_size=18,
            font_family="Source Sans Pro, Inter, sans-serif",
            font_color=BROOKLYN_TEXT,
            align="left"
        )
    )
    
    return fig



def plot_state_timeseries(state_df: pl.LazyFrame, state: str = "State"):
    """
    Plots an enhanced time series line chart for nadac_per_unit and payment_per_unit.

    Args:
        state_df (pl.LazyFrame): Polars LazyFrame with 'date', 'nadac_per_unit', and 'payment_per_unit' columns.
        state (str): State abbreviation for the chart title.

    Returns:
        plotly.graph_objects.Figure: The enhanced time series line chart.
    """
    # Optimize data processing with Polars
    df_long = (
        state_df
        .collect()
        .sort("date")
        .select([
            pl.col("date"),
            pl.col("nadac_per_unit").alias("NADAC Per Unit"),
            pl.col("payment_per_unit").alias("Payment Per Unit")
        ])
        .unpivot(
            index=["date"],
            on=["NADAC Per Unit", "Payment Per Unit"],
            variable_name="Metric",
            value_name="Value"
        )
        .to_pandas()
    )
  
    # 46Brooklyn Research color scheme
    color_map = {
        "NADAC Per Unit": BROOKLYN_PRIMARY,      # Deep navy blue
        "Payment Per Unit": BROOKLYN_ACCENT      # Orange accent
    }
    
    # Create the line plot
    fig = px.line(
        df_long,
        x="date",
        y="Value",
        color="Metric",
        markers=True,
        color_discrete_map=color_map,
        labels={
            "date": "Date",
            "Value": "Price per Unit ($)",
            "Metric": ""
        }
    )

    # Enhanced trace styling
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>" +
                     "Date: %{x|%b %Y}<br>" +
                     "Price: $%{y:,.2f}<extra></extra>",
        line=dict(width=4),
        marker=dict(size=8, line=dict(width=2, color="white")),
        connectgaps=True
    )

    # 46Brooklyn Research professional layout
    fig.update_layout(
        title={
            "text": f"<b>Drug Pricing Comparison: NADAC vs Payment per Unit</b><br><sup>State: {state}</sup>",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 24, "family": "Source Sans Pro, Inter, Arial, sans-serif", "color": BROOKLYN_PRIMARY}
        },
        xaxis=dict(
            title=dict(
                text="<b>Date</b>",
                font=dict(size=16, color=BROOKLYN_PRIMARY)
            ),
            tickformat="%b %Y",
            showgrid=True,
            gridcolor=BROOKLYN_BACKGROUND,
            gridwidth=1,
            tickfont=dict(size=13, color=BROOKLYN_MUTED),
            showline=True,
            linewidth=2,
            linecolor=BROOKLYN_SECONDARY,
            mirror=True,
            rangeslider=dict(
                visible=True,
                thickness=0.08,
                bgcolor=BROOKLYN_BACKGROUND,
                bordercolor=BROOKLYN_SECONDARY,
                borderwidth=2
            ),
            rangeselector=dict(
                buttons=[
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=2, label="2Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ],
                bgcolor=BROOKLYN_BACKGROUND,
                activecolor=BROOKLYN_ACCENT,
                bordercolor=BROOKLYN_SECONDARY,
                borderwidth=1,
                font=dict(size=12, color=BROOKLYN_TEXT),
                x=0.01,
                y=1.02
            )
        ),
        yaxis=dict(
            title=dict(
                text="<b>Price per Unit ($)</b>",
                font=dict(size=16, color=BROOKLYN_PRIMARY)
            ),
            tickprefix="$",
            tickformat=",.2f",
            showgrid=True,
            gridcolor=BROOKLYN_BACKGROUND,
            gridwidth=1,
            tickfont=dict(size=13, color=BROOKLYN_MUTED),
            showline=True,
            linewidth=2,
            linecolor=BROOKLYN_SECONDARY,
            mirror=True,
            zeroline=True,
            zerolinecolor=BROOKLYN_ACCENT,
            zerolinewidth=2
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.40,
            xanchor="center",
            x=0.5,
            font=dict(size=14, color=BROOKLYN_PRIMARY),
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor=BROOKLYN_SECONDARY,
            borderwidth=1,
            itemsizing="constant"
        ),
        font=dict(family="Source Sans Pro, Inter, Arial, sans-serif"),
        plot_bgcolor=BROOKLYN_WHITE,
        paper_bgcolor=BROOKLYN_BACKGROUND,
        # width=1000,
        height=600,
        margin=dict(l=80, r=40, t=120, b=120),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor=BROOKLYN_SECONDARY,
            font_size=13,
            font_family="Source Sans Pro, Inter, Arial, sans-serif"
        ),
        # 46Brooklyn Research annotation
        annotations=[
            dict(
                text="Data shows pricing trends over time | 46brooklyn Research",
                xref="paper", yref="paper",
                x=1, y=0,
                xanchor="right", yanchor="bottom",
                showarrow=False,
                font=dict(size=11, color=BROOKLYN_MUTED),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor=BROOKLYN_BACKGROUND,
                borderwidth=1
            )
        ]
    )

    # Professional styling touches with 46Brooklyn colors
    fig.update_xaxes(
        showspikes=True,
        spikecolor=BROOKLYN_MUTED,
        spikesnap="cursor",
        spikemode="across",
        spikethickness=1
    )
    
    fig.update_yaxes(
        showspikes=True,
        spikecolor=BROOKLYN_MUTED,
        spikesnap="cursor",
        spikemode="across",
        spikethickness=1
    )
    
    return fig

def state_place_holder():
    return html.Div(
            [
                html.Div(
                    [
                        html.I(
                            className="fas fa-chart-line",
                            style={
                                "fontSize": "3rem",
                                "color": BROOKLYN_MUTED,
                                "marginBottom": "1rem",
                            },
                        ),
                        html.H4(
                            "Select a State to View Time Series",
                            style={"color": BROOKLYN_PRIMARY, "marginBottom": "0.5rem"},
                        ),
                        html.P(
                            "Click on any state in the map above to see pricing trends over time",
                            style={"color": BROOKLYN_MUTED, "fontSize": "1.1rem"},
                        ),
                    ],
                    style={
                        "textAlign": "center",
                        "padding": "3rem 2rem",
                        "backgroundColor": BROOKLYN_WHITE,
                        "borderRadius": "8px",
                        "border": f"2px dashed {BROOKLYN_SECONDARY}",
                        "margin": "2rem 0",
                    },
                )
            ]
        )


def empty_map_placeholder():
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_annotation(
        text=f"<b>No Data Available</b><br><span style='font-size:1.1em;color:{BROOKLYN_MUTED};'>No data found for the selected filters.<br>Please adjust your selections and try again.</span>",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        xanchor="center", yanchor="middle",
        showarrow=False,
        font=dict(size=20, color=BROOKLYN_PRIMARY, family="Source Sans Pro, Inter, Arial, sans-serif"),
        bgcolor="rgba(255,255,255,0.95)",
        bordercolor=BROOKLYN_SECONDARY,
        borderwidth=2,
        borderpad=12
    )

    fig.update_layout(
        geo=dict(
            scope="usa",
            showland=True,
            landcolor=BROOKLYN_BACKGROUND,
            showframe=False,
            showcoastlines=False,
            bgcolor="rgba(0,0,0,0)"
        ),
        plot_bgcolor=BROOKLYN_WHITE,
        paper_bgcolor=BROOKLYN_BACKGROUND,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

    return fig