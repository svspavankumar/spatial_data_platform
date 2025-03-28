import uvicorn
from fastapi import FastAPI
from routes.polygon import polygon_router
from routes.point import point_router


app = FastAPI(title="Spatial Data API")

app.include_router(polygon_router, tags=["polygons"])
app.include_router(point_router, tags=["points"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Spatial Data API"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)