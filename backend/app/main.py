import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

try:
    from backend.app.solver_engine import solve_layout
    from backend.app.pdf_exporter import generate_pdf_report
    from backend.app.dxf_exporter import generate_dxf_file
except ImportError:
    from app.solver_engine import solve_layout
    from app.pdf_exporter import generate_pdf_report
    from app.dxf_exporter import generate_dxf_file

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
    res = solve_layout(req.building_width, req.building_length, req.rooms)
    return {"status": "success", "layout": res}

@app.post("/api/v1/export/pdf")
def export_pdf(req: LayoutRequest):
    res = solve_layout(req.building_width, req.building_length, req.rooms)
    pdf_bytes = generate_pdf_report(req.building_width, req.building_length, res)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=layout.pdf"})

@app.post("/api/v1/export/dxf")
def export_dxf(req: LayoutRequest):
    res = solve_layout(req.building_width, req.building_length, req.rooms)
    dxf_bytes = generate_dxf_file(req.building_width, req.building_length, res)
    return Response(content=dxf_bytes, media_type="application/dxf", headers={"Content-Disposition": "attachment; filename=layout.dxf"})

@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "ok", "message": "index.html not found"}