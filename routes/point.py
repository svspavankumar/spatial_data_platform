import json
import logging
from fastapi import APIRouter, HTTPException
from models import Point, CreatePoint, UpdatePoint
from connection import get_db_connection
from helper import wkt_to_geojson


point_router = APIRouter(prefix="/points")

@point_router.post("/")
def create_point(point: CreatePoint):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                wkt_location = f"SRID=4326;POINT({point.location.coordinates[0]} {point.location.coordinates[1]})"
                cur.execute(
                    """
                    INSERT INTO points (name, location, description)
                    VALUES (%s, ST_GeomFromText(%s), %s)
                    RETURNING id, name, ST_AsGeoJSON(location) AS location, description;
                    """,
                    (point.name, wkt_location, point.description)
                )
                result = cur.fetchone()
                conn.commit()

                location_geojson = json.loads(result["location"])
                return {
                    "id": result["id"],
                    "name": result["name"],
                    "location": location_geojson,
                    "description": result["description"]
                }
    except Exception as e:
        logging.error(f"Error creating point: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@point_router.put("/{point_id}")
def update_point(point_id: int, point: UpdatePoint):
    try:
        if not any([point.name, point.location, point.description is not None]):
            raise HTTPException(status_code=400, detail="At least one field must be provided for update")
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                updates = []
                params = []
                if point.name:
                    updates.append("name = %s")
                    params.append(point.name)
                if point.location:
                    wkt_location = f"SRID=4326;POINT({point.location.coordinates[0]} {point.location.coordinates[1]})"
                    updates.append("location = ST_GeomFromText(%s)")
                    params.append(wkt_location)
                if point.description is not None:
                    updates.append("description = %s")
                    params.append(point.description)

                params.append(point_id)
                query = f"UPDATE points SET {', '.join(updates)} WHERE id = %s RETURNING id, name, ST_AsGeoJSON(location) AS location, description;"
                cur.execute(query, params)
                result = cur.fetchone()
                if not result:
                    raise HTTPException(status_code=404, detail="Point not found")
                conn.commit()
                return {
                    "id": result["id"],
                    "name": result["name"],
                    "location": (wkt_to_geojson(result["location"])),
                    "description": result["description"]
                }
    except Exception as e:
        logging.error(f"Error updating point: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    

@point_router.get("/{point_id}", response_model=Point)
def get_point(point_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, ST_AsGeoJSON(location) AS location, description FROM points WHERE id = %s;",
                    (point_id,)
                )
                result = cur.fetchone()
                if not result:
                    raise HTTPException(status_code=404, detail="Point not found")
                return {
                    "id": result["id"],
                    "name": result["name"],
                    "location": json.loads(result["location"]),
                    "description": result["description"]
                }
    except Exception as e:
        logging.error(f"Error retrieving point: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@point_router.delete("/{point_id}")
def delete_point(point_id: int):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM points WHERE id = %s;", (point_id,))
                conn.commit()
                return {"message": "Point deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting point: {e}", exc_info=True)
        raise HTTPException(status_code=404, detail="Point not found")
    
@point_router.get("/")
def get_all_points():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, ST_AsGeoJSON(location) AS location, description FROM points;")
                results = cur.fetchall()
                points = []
                for result in results:
                    points.append({
                        "id": result["id"],
                        "name": result["name"],
                        "location": json.loads(result["location"]),
                        "description": result["description"]
                    })
                return points
    except Exception as e:
        logging.error(f"Error retrieving all points: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")