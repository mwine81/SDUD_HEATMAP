import polars as pl
from polars import col as c 
import polars.selectors as cs
from config import sdud_path, product_path, dates_path
from dash import dcc
import plotly.express as px
import dash_mantine_components as dmc
from dash import Dash, html, Input, Output, State, callback

# Lazy load dataframes
sdud = pl.scan_parquet(sdud_path)
product = pl.scan_parquet(product_path)
dates = pl.scan_parquet(dates_path)

def product_dropdown():
    """
    Create a dropdown component for product selection.
    """
    options = product.select(c.product).collect().to_series().to_list()
    return dcc.Dropdown(
        id="product-dropdown",
        options=options,
        value='metFORMIN HCl ER Oral Tablet Extended Release 24 Hour 500 MG',  # Default to the first product
        searchable=True,
        clearable=True,
        style={"width": "100%"},
    )

def date_dropdown():
    """
    Create a dropdown component for date selection.
    """
    options = dates.select(c.formatted_date).collect().to_series().to_list()
    return dcc.Dropdown(
        id="date-dropdown",
        options=options,
        value=options[-1],  # Default to the last date
        searchable=True,
        clearable=True,
        style={"width": "100%"},
    )

def ffsu_dropdown():
    """
    Create a dropdown component for FFSU selection.
    """
    return dcc.Checklist(
        id="ffsu-checklist",
        options=[
            {'label': 'FFSU', 'value': True},
            {'label': 'Non-FFSU', 'value': False}
        ],
        value=[True, False],  # Default to both options selected
        labelStyle={'display': 'block'},
    )

# metric dropdown
def metric_dropdown():
    """
    Create a dropdown component for metric selection.
    """
    return dcc.Dropdown(
        id="metric-dropdown",
        options=[
         'markup_per_unit', 'payment_per_unit'
        ],
        value='markup_per_unit',  # Default to markup_per_unit
        searchable=True,
        style={"width": "100%"},
    )

def markup_per_unit() -> pl.Expr:
    return ((c.total - c.nadac) / c.units).round(2).alias('markup_per_unit')

def payment_per_unit() -> pl.Expr:
    return (c.total / c.units).round(2).alias('payment_per_unit')

def nadac_per_unit():
    return (c.nadac / c.units).round(2).alias('nadac_per_unit')

def map_df(date_id, product_id, ffsu):
        return (
        sdud
        .filter(c.date_id == date_id)
        #  filter by brand or generic based on brand_generic value
        .filter(
        c.product_id == product_id)
        .filter(c.is_ffsu.is_in(ffsu))
        .group_by('state')
        .agg(pl.col(pl.Float64).sum())
        .with_columns(markup_per_unit(),payment_per_unit(), nadac_per_unit())
        )

def state_data(state, product_id):
    return (
        sdud
        .filter(c.product_id == product_id)
        .filter(c.state == state)
        .group_by(c.date_id)
        .agg(pl.col(pl.Float64).sum().round(4))
        .join(dates, on='date_id')
        .with_columns(
            pl.date(
                c.year,
                c.quarter.cast(pl.String).replace({'1': 1, '2': 4, '3': 7, '4': 10}).cast(pl.Int8),
                1
            ).alias("date")
        )
        .sort('date')
        .with_columns(
            # calculate total_per_unit
            total_per_unit=(c.total / c.units).round(4),
            # calculate nadac_per_unit
            nadac_per_unit=(c.nadac / c.units).round(4),
            # calculate payment_per_unit
            payment_per_unit=(c.total / c.units).round(4)
        )
    )

class MantineUI:
    """
    A class to encapsulate Mantine UI components for Dash applications.
    """

    @staticmethod
    def product_dropdown():
        """
        Create a Mantine dropdown component for product selection.
        """
        options = product.select(c.product).collect().to_series().to_list()
        return dmc.Select(
            id="product-dropdown",
            data=options,
            value='metFORMIN HCl ER Oral Tablet Extended Release 24 Hour 500 MG',  # Default to the first product
            searchable=True,
        )
    
    @staticmethod
    def date_dropdown():
        """
        Create a Mantine dropdown component for date selection.
        """
        options = dates.select(c.formatted_date).collect().to_series().to_list()
        return dmc.Select(
            id="date-dropdown",
            data=options,
            value=options[-1],  # Default to the last date
            searchable=True,
        )
    
    @staticmethod
    def ffsu_dropdown():
        """
        Create a Mantine checklist component for FFSU selection.
        """
        return dmc.MultiSelect(
            id="ffsu-checklist",
            data= ['FFSU', 'Non-FFSU'],
              # Default to both options selected
            value=['FFSU', 'Non-FFSU'],
        )
    @staticmethod
    def metric_dropdown():
        """
        Create a Mantine dropdown component for metric selection.
        """
        return dmc.Select(
            id="metric-dropdown",
            data=[
                'markup_per_unit', 'payment_per_unit'
            ],
            value='markup_per_unit',  # Default to markup_per_unit
            searchable=True,
        )