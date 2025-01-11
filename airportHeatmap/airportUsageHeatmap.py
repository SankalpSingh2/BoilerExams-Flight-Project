import polars as pl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import folium

flights_file_path = "../filtered_flights.csv"
airports_file_path = "../iata-icao.csv" 

flights_data = pl.read_csv(flights_file_path)
airports_data = pd.read_csv(airports_file_path)

num_flights = 10  # anaylze certain number of flights

#get unique flight numbers and select the first `num_flights` unique flights
unique_flight_numbers = flights_data["flight"].unique().to_list()[:num_flights]

filtered_flights = flights_data.filter(pl.col("flight").is_in(unique_flight_numbers)).to_pandas()

# timestamp fix
if "timestamp" not in filtered_flights.columns:
    filtered_flights["timestamp"] = range(len(filtered_flights))

def find_nearest_airports(latitudes, longitudes):
    nearest_airports = []
    for lat, lon in zip(latitudes, longitudes):
        min_distance = float("inf")
        nearest_airport = None
        for _, airport in airports_data.iterrows():
            distance = geodesic((lat, lon), (airport["latitude"], airport["longitude"])).kilometers
            if distance < min_distance:
                min_distance = distance
                nearest_airport = airport["iata"]
        nearest_airports.append(nearest_airport)
    return nearest_airports

filtered_flights.loc[:, "nearest_airport"] = find_nearest_airports(
    filtered_flights["lat"].values, filtered_flights["lon"].values
)


def filter_descending_flights(flights, altitude_threshold=500):
    flights = flights.sort_values(["flight", "timestamp"])
    descending_mask = flights["alt_geom"].diff(periods=-1) > altitude_threshold
    return flights[descending_mask]

descending_flights = filter_descending_flights(filtered_flights)


airport_counts = descending_flights["nearest_airport"].value_counts().reset_index()
airport_counts.columns = ["Airport", "Descending Flights Count"]


airport_map = folium.Map(location=[filtered_flights["lat"].iloc[0], filtered_flights["lon"].iloc[0]], zoom_start=6)


for _, row in airport_counts.iterrows():
    airport = airports_data[airports_data["iata"] == row["Airport"]].iloc[0]
    

    descending_flights_at_airport = descending_flights[descending_flights["nearest_airport"] == row["Airport"]]
    flight_numbers = descending_flights_at_airport["flight"].unique().tolist()
    
 
    flight_numbers_label = ", ".join(flight_numbers[:5]) 
    
    folium.CircleMarker(
        location=[airport["latitude"], airport["longitude"]],
        radius=10,
        color="darkred",
        fill=True,
        fill_opacity=0.7 + 0.3 * (row["Descending Flights Count"] / airport_counts["Descending Flights Count"].max()),
        popup=f"{airport['airport']} ({row['Airport']}): {row['Descending Flights Count']} descending flights\nFlight Numbers: {flight_numbers_label}",
    ).add_to(airport_map)

airport_map.save("airport_utilization_heatmap_with_flight_numbers.html")
print("Airport utilization heatmap with flight numbers saved as 'airport_utilization_heatmap_with_flight_numbers.html'.")


top_10_airports = airport_counts.head(10)
print("Top 10 Airports with Most Descending Flights:")
print(top_10_airports)

plt.figure(figsize=(10, 6))
sns.barplot(x="Descending Flights Count", y="Airport", data=top_10_airports, palette="Blues_d")
plt.title("Top 10 Airports with Most Descending Flights Nearby")
plt.xlabel("Number of Descending Flights")
plt.ylabel("Airport")
plt.show()
