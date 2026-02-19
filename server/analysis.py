import geopandas as gpd
from sqlalchemy import create_engine

# Database connection parameters
host = "localhost"
port = "5432"
dbname = "gme221"
user = "postgres"
password = "zeroeyteen018"

# Create connection string
conn_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

# Create AQLAlchemy engine
engine = create_engine(conn_str)

# Minimal SQL queries (no spatial operations)
sql_parcel = "SELECT parcel_pin, geom FROM public.parcel"
sql_landuse = "SELECT name, geom FROM public.landuse"

# Load data into GeoDataFrames
parcels = gpd.read_postgis(sql_parcel, engine, geom_col="geom")
landuse = gpd.read_postgis(sql_landuse, engine, geom_col="geom")

print(parcels.head())
print(landuse.head())

# print(parcels.head())
# print(landuse.head())

print(parcels.crs)
print(landuse.crs)
print(parcels.geometry.type.unique())
print(landuse.geometry.type.unique())

# Reproject to EPSG:3395 for area calculations
parcels = parcels.to_crs(epsg=3395)
landuse = landuse.to_crs(epsg=3395)
print(parcels.head())

print(parcels.geometry)

parcels["total_area"] = parcels.geometry.area
print(parcels["total_area"])

overlay = gpd.overlay(parcels, landuse, how="intersection")
overlay["landuse_area"] = overlay.geometry.area
print(overlay.head())

overlay["percentage"] = (
    overlay["landuse_area"] / overlay["total_area"]
) * 100

overlay["percentage"] = overlay["percentage"].round(2)

print(overlay.head())

dominant_res = overlay[
    ((overlay["name"] == "Residential Zone - Low Density") |
     (overlay["name"] == "Residential Zone - Medium Density")) &
     (overlay["percentage"] >= 60)
].copy()

print(dominant_res.head())


dominant_res = dominant_res.to_crs(epsg=4326)

dominant_res.to_file("dominant_residential.geojson", driver="GeoJSON")
print("GeoJSON saved successfully.")


dominant_res = overlay[
    ((overlay["name"] == "Residential Zone - Low Density") |
     (overlay["name"] == "Residential Zone - Medium Density")) &
     (overlay["percentage"] >= 50)
].copy()

print(dominant_res.head())


dominant_res = dominant_res.to_crs(epsg=4326)

dominant_res.to_file("dominant_residential.geojson", driver="GeoJSON")
print("GeoJSON saved successfully.")

# 1. Calculate the maximum percentage found in each parcel
# This creates a Series where the index is 'parcel_id' and the value is the highest % found
max_pct_per_parcel = overlay.groupby('parcel_id')['percentage'].max()

# 2. Identify IDs where the 'peak' land use is less than 60%
mixed_ids = max_pct_per_parcel[max_pct_per_parcel < 60].index

# 3. Filter the original overlay to keep only these parcels
mixed_use_df = overlay[overlay['parcel_id'].isin(mixed_ids)].copy()

# 4. Export the result
mixed_use_df = mixed_use_df.to_crs(epsg=4326)
mixed_use_df.to_file("mixed_use_parcels.geojson", driver="GeoJSON")

print(f"Success! Identified {mixed_use_df['parcel_id'].nunique()} mixed-use parcels.")