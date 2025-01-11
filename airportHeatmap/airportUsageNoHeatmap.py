import polars as pl
import pandas as pd
from geopy.distance import geodesic
from scipy.spatial import cKDTree

flights_file_path = "../filtered_flights.csv"
airports_file_path = "../iata-icao.csv"

flights_data = pl.read_csv(flights_file_path)
airports_data = pd.read_csv(airports_file_path)

# need to convert to pandas for processing
filtered_flights = flights_data.to_pandas()

if "timestamp" not in filtered_flights.columns:
    filtered_flights["timestamp"] = range(len(filtered_flights))

# with KDtree data structure time complexity is reduced to O(logm) instead of O(num_flights x num_airports)
def find_nearest_airports(latitudes, longitudes):
    airport_coords = airports_data[["latitude", "longitude"]].values
    kdtree = cKDTree(airport_coords)

    nearest_airports = []
    for lat, lon in zip(latitudes, longitudes):
        dist, idx = kdtree.query([lat, lon])
        nearest_airport = airports_data.iloc[idx]["iata"]
        nearest_airports.append(nearest_airport)
    return nearest_airports

filtered_flights["nearest_airport"] = find_nearest_airports(
    filtered_flights["lat"].values, filtered_flights["lon"].values
)

# find descending flights
def filter_descending_flights(flights, altitude_threshold=500):
    flights = flights.sort_values(["flight", "timestamp"])
    descending_mask = flights["alt_geom"].diff(periods=-1) > altitude_threshold
    return flights[descending_mask]

def analyze_flights(num_flights=None):
    if num_flights is not None:
        filtered_flights_subset = filtered_flights.head(num_flights)  # Limit the number of flights to analyze
    else:
        filtered_flights_subset = filtered_flights

    descending_flights = filter_descending_flights(filtered_flights_subset)

    airport_counts = descending_flights["nearest_airport"].value_counts().reset_index()
    airport_counts.columns = ["Airport", "Descending Flights Count"]

    most_descending_airport = airport_counts.iloc[0]
    print("Airport with the most descending flights:")
    with open("most_descending_airport.txt", "w") as f:
        f.write("Airport with the most descending flights:\n")
        f.write(str(most_descending_airport))
    print(most_descending_airport)

num_flights_to_analyze = int(input("Enter the number of flights to analyze (or 0 for all): "))
if num_flights_to_analyze == 0:
    analyze_flights()
else:
    analyze_flights(num_flights=num_flights_to_analyze)
