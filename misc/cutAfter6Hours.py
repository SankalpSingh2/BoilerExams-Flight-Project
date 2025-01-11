import polars as pl
from datetime import timedelta

df = pl.read_csv("adsb.csv")

df = df.with_columns(
    pl.col("epoch").str.strptime(pl.Datetime).cast(pl.Datetime)
)

first_flight_time = df[0, "epoch"]

six_hours_later = first_flight_time + timedelta(hours=6)

filtered_df = df.filter(pl.col("epoch") <= six_hours_later)

filtered_df.write_csv("filtered_flights.csv")
