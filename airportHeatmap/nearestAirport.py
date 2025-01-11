import polars as pl
import folium
from geopy.distance import geodesic


flight_file_path = "filtered_flights.csv"
flight_data = pl.read_csv(flight_file_path)


airport_file_path = "iata-icao.csv" 
airport_data = pl.read_csv(airport_file_path).to_pandas()


flight_data_pd = flight_data.to_pandas()


flight_number = "SWA1081" 

selected_flight_data = flight_data_pd[flight_data_pd["flight"].str.strip() == flight_number]

if not selected_flight_data.empty:
    first_lat = selected_flight_data.iloc[0]["lat"]
    first_lon = selected_flight_data.iloc[0]["lon"]

    flight_map = folium.Map(location=[first_lat, first_lon], zoom_start=6)

    for _, row in selected_flight_data.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=(
                f"Flight: {row['flight']}<br>"
                f"Altitude: {row['alt_geom']}<br>"
                f"Operator: {row['ownOp']}<br>"
                f"Latitude: {row['lat']}<br>"
                f"Longitude: {row['lon']}"
            ),
            icon=folium.Icon(color="blue", icon="plane", prefix="fa"),
        ).add_to(flight_map)

    nearest_airport = None
    shortest_distance = float("inf")
    nearest_airport_coords = (0, 0)

    for _, airport in airport_data.iterrows():
        airport_coords = (airport["latitude"], airport["longitude"])
        for _, point in selected_flight_data.iterrows():
            flight_coords = (point["lat"], point["lon"])
            distance = geodesic(flight_coords, airport_coords).kilometers
            if distance < shortest_distance:
                shortest_distance = distance
                nearest_airport = airport["airport"]
                nearest_airport_coords = airport_coords

    folium.Marker(
        location=nearest_airport_coords,
        popup=(
            f"Nearest Airport: {nearest_airport}<br>"
            f"Distance: {shortest_distance:.2f} km"
        ),
        icon=folium.Icon(color="green", icon="flag", prefix="fa"),
    ).add_to(flight_map)

    flight_map.save("single_flight_map_with_nearest_airport.html")
    print(f"Map saved to single_flight_map_with_nearest_airport.html for flight {flight_number}.")
else:
    print(f"No data found for flight number {flight_number}. Please check the flight number.")
