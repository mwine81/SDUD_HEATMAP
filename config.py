from pathlib import Path

DATA = Path('/Users/matthewwine/3 Axis Advisors Dropbox/Matthew matt@3axisadvisors.com/datalake/projects/JUNE_2025/SDUD_HEATMAP')
#DATA = Path(r"C:\Users\mwine\3 Axis Advisors Dropbox\Matthew matt@3axisadvisors.com\datalake\projects\JUNE_2025\SDUD_HEATMAP")
sdud_path = DATA / 'sdud.parquet'
product_path = DATA / 'product_id.parquet'
dates_path = DATA / 'date_id_filtered.parquet'
