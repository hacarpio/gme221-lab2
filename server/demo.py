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

