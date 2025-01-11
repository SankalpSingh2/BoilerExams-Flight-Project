import polars as pl
import matplotlib.pyplot as plt

def analyze_flight_data(input_csv, output_txt):
    df = pl.read_csv(input_csv)

    findings = []

    findings.append(f"Total number of records: {df.shape[0]}")
    findings.append(f"Unique flights: {df['flight'].n_unique()}")
    findings.append(f"Unique operators: {df['ownOp'].n_unique()}")

    #altitude
    max_altitude = df['alt_geom'].max()
    min_altitude = df['alt_geom'].min()
    avg_altitude = df['alt_geom'].mean()
    findings.append(f"Highest altitude: {max_altitude} ft")
    findings.append(f"Lowest altitude: {min_altitude} ft")
    findings.append(f"Average altitude: {avg_altitude:.2f} ft")

    #geographic insights
    unique_locations = df.select(['lat', 'lon']).unique().shape[0]
    findings.append(f"Unique geographic locations (lat/lon pairs): {unique_locations}")
    ground_flights = df.filter(df['alt_geom'] <= 0)
    findings.append(f"Number of flights at ground level or below: {ground_flights.shape[0]}")

    #top operators
    top_operators = (
        df.group_by('ownOp')
        .agg(pl.count().alias('flight_count'))
        .sort('flight_count', descending=True)
        .head(5)
    )
    findings.append("\nTop 5 operators by flight count:")
    findings.extend(
        [f"  {row[0]}: {row[1]} flights" for row in top_operators.iter_rows()]
    )

    with open(output_txt, 'w') as file:
        file.write("\n".join(findings))
    print(f"Analysis complete. Findings written to {output_txt}")

    # removing none
    filtered_data = [
        (operator, count)
        for operator, count in zip(top_operators['ownOp'], top_operators['flight_count'])
        if count is not None and operator is not None
    ]

    operators = [operator for operator, _ in filtered_data]
    flight_counts = [count for _, count in filtered_data]

    plt.figure(figsize=(10, 6))
    plt.bar(operators, flight_counts, color='skyblue')
    plt.title('Top Operators by Flight Count')
    plt.xlabel('Operator')
    plt.ylabel('Number of Flights')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    plt.savefig("basicStatistics/flightsPerLiner")
    print(f"Plot saved to basicStatistics/flightsPerLiner")

    plt.figure(figsize=(10, 6))
    plt.hist(df['alt_geom'].to_list(), bins=50, color='skyblue', edgecolor='black')
    plt.title('Altitude Distribution')
    plt.xlabel('Altitude (ft)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig("basicStatistics/altitude_distribution_plot.png")
    print("Altitude distribution plot saved.")

    plt.figure(figsize=(10, 6))
    plt.scatter(df['lon'].to_list(), df['lat'].to_list(), color='skyblue', alpha=0.5)
    plt.title('Geographic Distribution of Flights')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.tight_layout()
    plt.savefig("basicStatistics/geographic_distribution_plot.png")
    print("Geographic distribution plot saved.")

input_csv = "adsb.csv"
output_txt = "basicStatistics/interestingStats.txt"
analyze_flight_data(input_csv, output_txt)
