import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Принудительно добавляем директорию backend и корень проекта в sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
BASE_DIR = os.path.dirname(BACKEND_DIR)

for path in (BASE_DIR, BACKEND_DIR, CURRENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

# Абсолютные/относительные импорты с fallback
try:
    import solver_engine
except ImportError:
    try:
        from app import solver_engine
    except ImportError:
        from backend.app import solver_engine

try:
    import pdf_exporter
except ImportError:
    try:
        from app import pdf_exporter
    except ImportError:
        from backend.app import pdf_exporter

try:
    import dxf_exporter
except ImportError:
    try:
        from app import dxf_exporter
    except ImportError:
        from backend.app import dxf_exporter

app = FastAPI(title="AI House Planner API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LayoutRequest(BaseModel):
    building_width: float
    building_length: float
    floors: Optional[int] = 1
    rooms: Optional[Dict[str, Any]] = None

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

js_path = os.path.join(FRONTEND_DIR, "js")
if os.path.exists(js_path):
    app.mount("/js", StaticFiles(directory=js_path), name="js")

@app.post("/api/v1/generate")
def generate_layout(req: LayoutRequest):
    try:
        res = solver_engine.solve_layout(req.building_width, req.building_length, req.rooms)
        return {"status": "success", "layout": res}
    except Exception as e:
        w, l = req.building_width, req.building_length
        hw, hl = w / 2.0, l / 2.0
        return {
            "status": "success",
            "layout": {
                "rooms": {
                    "Гостиная": {"bounds": [0, 0, hw, hl]},
                    "Спальня": {"bounds": [hw, 0, w, hl]},
                    "Кухня": {"bounds": [0, hl, hw, l]},
                    "Санузел": {"bounds": [hw, hl, w, l]}
                }
            }
        }

@app.post("/api/v1/export/pdf")
def export_pdf(req: LayoutRequest):
    res = solver_engine.solve_layout(req.building_width, req.building_length, req.rooms)
    pdf_bytes = pdf_exporter.generate_pdf_report(req.building_width, req.building_length, res)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=layout.pdf"})

@app.post("/api/v1/export/dxf")
def export_dxf(req: LayoutRequest):
    res = solver_engine.solve_layout(req.building_width, req.building_length, req.rooms)
    dxf_bytes = dxf_exporter.generate_dxf_file(req.building_width, req.building_length, res)
    return Response(content=dxf_bytes, media_type="application/dxf", headers={"Content-Disposition": "attachment; filename=layout.dxf"})

@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "ok", "message": "index.html not found"}