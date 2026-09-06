import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# Импорт логики генерации
from backend.app.solver_engine import solve_layout

app = FastAPI(title="AI House Planner API", version="2.0")

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class RoomRequirement(BaseModel):
    min_area: float
    max_area: Optional[float] = None
    adjacent_to: Optional[List[str]] = []

class LayoutRequest(BaseModel):
    building_width: float
    building_length: float
    floors: int = 1
    rooms: Dict[str, RoomRequirement]

# Определение путей к фронтенду
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Путь к папке frontend из структуры проекта
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../frontend"))

# Подключение статических файлов (JS, CSS)
js_path = os.path.join(FRONTEND_DIR, "js")
if os.path.exists(js_path):
    app.mount("/js", StaticFiles(directory=js_path), name="js")

css_path = os.path.join(FRONTEND_DIR, "css")
if os.path.exists(css_path):
    app.mount("/css", StaticFiles(directory=css_path), name="css")

# Эндпоинт генерации планировки
@app.post("/api/v1/generate")
def generate_layout(req: LayoutRequest):
    try:
        result = solve_layout(
            width=req.building_width,
            length=req.building_length,
            rooms=req.rooms
        )
        return {"status": "success", "layout": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Главная страница - отдача index.html
@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "ok", "message": "API running, index.html not found"}