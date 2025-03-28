from shapely import wkt

def wkt_to_geojson(wkt_str: str):

    if wkt_str.startswith("SRID=4326;"):
        wkt_str = wkt_str[10:]
    geom = wkt.loads(wkt_str) 
    print(geom) 
    return geojson