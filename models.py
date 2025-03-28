from pydantic import BaseModel
from pydantic_geojson import PointModel as PydanticPoint, PolygonModel as PydanticPolygon
from typing import Optional



class CreatePoint(BaseModel):
    name: str
    location: PydanticPoint
    description: Optional[str] = None

class UpdatePoint(BaseModel):
    name: Optional[str] = None
    location: Optional[PydanticPoint] = None
    description: Optional[str] = None

class Point(BaseModel):
    id: int
    name: str
    location: PydanticPoint
    description: Optional[str] = None

class CreatePolygon(BaseModel):
    name: str
    shape: PydanticPolygon
    population_density: Optional[float] = None

class UpdatePolygon(BaseModel):
    name: Optional[str] = None
    shape: Optional[PydanticPolygon] = None
    population_density: Optional[float] = None

class Polygon(BaseModel):
    id: int
    name: str
    shape: PydanticPolygon
    population_density: Optional[float] = None

class QueryPolygon(BaseModel):
    shape: PydanticPolygon