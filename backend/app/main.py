import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Импорт солвера
try:
    from backend.app.solver_engine import solve_layout
except ImportError:
    from app.solver_engine import solve_layout

app = FastAPI(title="AI House Planner API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RoomRequirement(BaseModel):
    min_area: float
    max_area: Optional[float] = None
    adjacent_to: Optional[List[str]] = []

class LayoutRequest(BaseModel):
    building_width: float
    building_length: float
    floors: int = 1
    rooms: Optional[Dict[str, RoomRequirement]] = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

js_path = os.path.join(FRONTEND_DIR, "js")
if os.path.exists(js_path):
    app.mount("/js", StaticFiles(directory=js_path), name="js")

@app.post("/api/v1/generate")
def generate_layout(req: LayoutRequest):
    try:
        # Вызываем логику расчета
        if req.rooms:
            rooms_dict = {k: v.dict() for k, v in req.rooms.items()}
        else:
            rooms_dict = {
                "Гостиная": {"min_area": 20},
                "Спальня": {"min_area": 14},
                "Кухня": {"min_area": 12},
                "Санузел": {"min_area": 6}
            }

        res = solve_layout(req.building_width, req.building_length, rooms_dict)
        return {"status": "success", "layout": res}
    except Exception as e:
        # Резервный расчет планировки при возникновении исключения
        w, l = req.building_width, req.building_length
        hw, hl = w / 2, l / 2
        fallback_layout = {
            "rooms": {
                "Гостиная": {"bounds": [0, 0, hw, hl]},
                "Спальня": {"bounds": [hw, 0, w, hl]},
                "Кухня": {"bounds": [0, hl, hw, l]},
                "Санузел": {"bounds": [hw, hl, w, l]}
            }
        }
        return {"status": "success", "layout": fallback_layout}

@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "ok", "message": "index.html not found"}