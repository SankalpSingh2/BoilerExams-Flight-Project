import polars as pl
import folium

file_path = "filtered_flights.csv" 
data = pl.read_csv(file_path)

flight_number = "SWA4155"

filtered_data = data.filter(pl.col("flight").str.strip().eq(flight_number))

filtered_data_pd = filtered_data.to_pandas()

if not filtered_data_pd.empty:
    print(f"\nFound the following records for flight number {flight_number}:")
    print(filtered_data_pd)

    first_lat = filtered_data_pd.iloc[0]["lat"]
    first_lon = filtered_data_pd.iloc[0]["lon"]

    flight_map = folium.Map(location=[first_lat, first_lon], zoom_start=6)

    for _, row in filtered_data_pd.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=(
            f"Flight: {row['flight']}<br>"
            f"Altitude: {row['alt_geom']}<br>"
            f"Operator: {row['ownOp']}<br>"
            f"Latitude: {row['lat']}<br>"
            f"Longitude: {row['lon']}"),
            icon=folium.Icon(color="blue", icon="plane", prefix="fa"),
        ).add_to(flight_map)

    flight_map.save("filtered_flight_map.html")

    print(f"Map saved to filtered_flight_map.html. Open it in your browser to view the flight {flight_number}.")
else:
    print(f"No data found for flight number {flight_number}. Please check the flight number.")
