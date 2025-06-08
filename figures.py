import polars as pl
import plotly.express as px
from polars import col as c

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
    
    # Professional color scale - better than Viridis for business presentations
    color_scale = "RdYlBu_r" if is_currency else "Blues"
    
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
    
    # Calculate min/max for colorbar ticks
    min_val = float(df[metric].min())
    max_val = float(df[metric].max())
    nticks = 4  # Limit to 4 ticks to avoid overlap
    if min_val == max_val:
        tickvals = [min_val]
    else:
        tickvals = [round(min_val + i * (max_val - min_val) / (nticks - 1), 2) for i in range(nticks)]
    
    # Enhanced styling for professional appearance optimized for Mantine cards
    fig.update_layout(
        title=None,
        showlegend=False,
        width=None,
        height=500,
        margin=dict(l=5, r=5, t=10, b=70),
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
            size=12,
            color="#1e293b"
        ),
        coloraxis_colorbar={
            'title': {
                'text': metric.replace('_', ' ').title(),
                'font': {'size': 14, 'color': '#212529', 'family': 'Inter, sans-serif'},
                'side': 'bottom'
            },
            'tickfont': {'size': 12, 'color': '#495057'},
            'orientation': 'h',
            'x': 0.5,
            'y': -0.15,
            'xanchor': 'center',
            'lenmode': 'fraction',
            'len': 0.75,
            'thickness': 18,
            'bgcolor': 'rgba(248, 249, 250, 0.95)',
            'bordercolor': '#dee2e6',
            'borderwidth': 1,
            'tickformat': '$,.0f' if is_currency else ',.1f',
            'tickmode': 'array',
            'tickvals': tickvals,
            'nticks': nticks
        },
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#94a3b8",
            coastlinewidth=0.8,
            projection_type='albers usa',
            bgcolor='rgba(0,0,0,0)',
            showlakes=True,
            lakecolor='#e0f2fe',
            showrivers=False,
            showland=True,
            landcolor='#f8fafc',
            showsubunits=True,
            subunitcolor="#222323",
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        autosize=True,
    )
    
    fig.update_traces(
        hovertemplate='<b>%{location}</b><br>' +
                     f'<span style="color: #374151;">{metric.replace("_", " ").title()}:</span> ' +
                     ('<span style="color: #059669; font-weight: 600;">$%{z:,.2f}</span>' if is_currency else 
                      '<span style="color: #059669; font-weight: 600;">%{z:,.2f}</span>') +
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
        font=dict(size=16, color="#1f2937", family="Inter, sans-serif"),
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="#e5e7eb",
        borderwidth=1,
        borderpad=8
    )
    
    fig.update_layout(
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#e5e7eb",
            font_size=12,
            font_family="Inter, sans-serif",
            font_color="#374151",
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
            pl.col("nadac_per_unit"),
            pl.col("payment_per_unit")
        ])
        .unpivot(
            index=["date"],
            on=["nadac_per_unit", "payment_per_unit"],
            variable_name="Metric",
            value_name="Value"
        )
        .with_columns([
            pl.col("Metric").str.replace("_per_unit", "").str.replace("_", " ").str.to_titlecase().alias("Metric_Label")
        ])
        .to_pandas()
    )

    # Enhanced color scheme with better contrast
    color_map = {
        "nadac_per_unit": "#2E86AB",      # Professional blue
        "payment_per_unit": "#A23B72"     # Complementary magenta
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

    # Professional layout with enhanced styling
    fig.update_layout(
        title={
            "text": f"<b>Drug Pricing Comparison: NADAC vs Payment per Unit</b><br><sup>State: {state}</sup>",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 24, "family": "Inter, Arial, sans-serif", "color": "#2c3e50"}
        },
        xaxis=dict(
            title=dict(
                text="<b>Date</b>",
                font=dict(size=16, color="#34495e")
            ),
            tickformat="%b %Y",
            showgrid=True,
            gridcolor="#ecf0f1",
            gridwidth=1,
            tickfont=dict(size=13, color="#7f8c8d"),
            showline=True,
            linewidth=2,
            linecolor="#bdc3c7",
            mirror=True,
            rangeslider=dict(
                visible=True,
                thickness=0.08,
                bgcolor="#f8f9fa",
                bordercolor="#dee2e6",
                borderwidth=2
            ),
            rangeselector=dict(
                buttons=[
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(count=2, label="2Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ],
                bgcolor="#f8f9fa",
                activecolor="#3498db",
                bordercolor="#dee2e6",
                borderwidth=1,
                font=dict(size=12, color="#495057"),
                x=0.01,
                y=1.02
            )
        ),
        yaxis=dict(
            title=dict(
                text="<b>Price per Unit ($)</b>",
                font=dict(size=16, color="#34495e")
            ),
            tickprefix="$",
            tickformat=",.2f",
            showgrid=True,
            gridcolor="#ecf0f1",
            gridwidth=1,
            tickfont=dict(size=13, color="#7f8c8d"),
            showline=True,
            linewidth=2,
            linecolor="#bdc3c7",
            mirror=True,
            zeroline=True,
            zerolinecolor="#e74c3c",
            zerolinewidth=2
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.40,
            xanchor="center",
            x=0.5,
            font=dict(size=14, color="#2c3e50"),
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#bdc3c7",
            borderwidth=1,
            itemsizing="constant"
        ),
        font=dict(family="Inter, Arial, sans-serif"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#fafbfc",
        # width=1000,
        height=600,
        margin=dict(l=80, r=40, t=120, b=120),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#bdc3c7",
            font_size=13,
            font_family="Inter, Arial, sans-serif"
        ),
        # Add subtle shadow effect
        annotations=[
            dict(
                text="Data shows pricing trends over time",
                xref="paper", yref="paper",
                x=1, y=0,
                xanchor="right", yanchor="bottom",
                showarrow=False,
                font=dict(size=11, color="#95a5a6"),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="#ecf0f1",
                borderwidth=1
            )
        ]
    )

    # Add professional styling touches
    fig.update_xaxes(
        showspikes=True,
        spikecolor="#95a5a6",
        spikesnap="cursor",
        spikemode="across",
        spikethickness=1
    )
    
    fig.update_yaxes(
        showspikes=True,
        spikecolor="#95a5a6",
        spikesnap="cursor",
        spikemode="across",
        spikethickness=1
    )
    
    return fig
