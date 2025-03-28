import logging
import json
from fastapi import APIRouter, HTTPException
from models import Polygon, CreatePolygon, UpdatePolygon, QueryPolygon
from connection import get_db_connection
from helper import wkt_to_geojson
from typing import List


polygon_router = APIRouter(prefix="/polygon")
@polygon_router.post("/", response_model=Polygon)
def create_polygon(polygon: CreatePolygon):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                check_duplicate_query = "SELECT id FROM polygons WHERE name = %s;"
                cur.execute(check_duplicate_query, (polygon.name,))
                existing_polygon = cur.fetchone()
                if existing_polygon:
                    raise HTTPException(status_code=400, detail="Polygon with this name already exists")
                
                wkt_shape = f"SRID=4326;POLYGON(({', '.join([f'{x} {y}' for x, y in polygon.shape.coordinates[0]])}))"
                cur.execute(
                    """
                    INSERT INTO polygons (name, shape, population_density)
                    VALUES (%s, ST_GeomFromText(%s), %s)
                    RETURNING id, name, ST_AsText(shape) AS shape, population_density;
                    """,
                    (polygon.name, wkt_shape, polygon.population_density)
                )
                result = cur.fetchone()
                conn.commit()
                return {
                    "id": result["id"],
                    "name": result["name"],
                    "shape": (wkt_to_geojson(result["shape"])),
                    "population_density": result["population_density"]
                }
    except Exception as e:
        logging.error(f"Error creating polygon: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@polygon_router.put("/{polygon_id}", response_model=Polygon)
def update_polygon(polygon_id: int, polygon: UpdatePolygon):
    try:
        if not any([polygon.name, polygon.shape, polygon.population_density is not None]):
            raise HTTPException(status_code=400, detail="At least one field must be provided for update")
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                updates = []
                params = []
                if polygon.name:
                    updates.append("name = %s")
                    params.append(polygon.name)
                if polygon.shape:
                    wkt_shape = f"SRID=4326;POLYGON(({', '.join([f'{x} {y}' for x, y in polygon.shape.coordinates[0]])}))"
                    updates.append("shape = ST_GeomFromText(%s)")
                    params.append(wkt_shape)
                if polygon.population_density is not None:
                    updates.append("population_density = %s")
                    params.append(polygon.population_density)

                params.append(polygon_id)
                query = f"UPDATE polygons SET {', '.join(updates)} WHERE id = %s RETURNING id, name, ST_AsText(shape) AS shape, population_density;"
                cur.execute(query, params)
                result = cur.fetchone()
                if not result:
                    raise HTTPException(status_code=404, detail="Polygon not found")
                conn.commit()
                return {
                    "id": result["id"],
                    "name": result["name"],
                    "shape": wkt_to_geojson(result["shape"]),
                    "population_density": result["population_density"]
                }
    except Exception as e:
        logging.error(f"Error updating polygon: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@polygon_router.get("/{polygon_id}", response_model=Polygon)
def get_polygon(polygon_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, ST_AsText(shape) AS shape, population_density FROM polygons WHERE id = %s;",
                (polygon_id,)
            )
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Polygon not found")
            return {
                "id": result["id"],
                "name": result["name"],
                "shape": wkt_to_geojson(result["shape"]),
                "population_density": result["population_density"]
            }

@polygon_router.delete("/{polygon_id}")
def delete_polygon(polygon_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                check_query = "SELECT id FROM polygons WHERE id = %s;"
                cur.execute(check_query, (polygon_id,))
                result = cur.fetchone()
                if not result:
                    return {"message": f"Polygon with id {polygon_id} not found"}
                cur.execute("DELETE FROM polygons WHERE id = %s;", (polygon_id,))
                conn.commit()
                return {"message": "Polygon deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting polygon: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@polygon_router.get("/", response_model=List[Polygon])
def get_all_polygons():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, ST_AsText(shape) AS shape, population_density FROM polygons;")
                results = cur.fetchall()
                polygons = []
                for result in results:
                    polygons.append({
                        "id": result["id"],
                        "name": result["name"],
                        "shape": wkt_to_geojson(result["shape"]),
                        "population_density": result["population_density"]
                    })
                return polygons
    except Exception as e:
        logging.error(f"Error retrieving all polygons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")