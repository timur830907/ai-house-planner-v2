import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import networkx as nx

from app.solver_engine import solve_layout_variants
from app.dxf_exporter import export_to_dxf
from app.pdf_exporter import export_to_pdf

app = FastAPI(title="AI House Plan Generator API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RoomRequirement(BaseModel):
    name: str
    min_area: float
    preferred_adjacent: Optional[List[str]] = []

class HousePlanRequest(BaseModel):
    total_area: float
    floors: int = 1
    rooms: List[RoomRequirement]

class ExportRequest(BaseModel):
    layout: Dict[str, Any]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/", response_class=HTMLResponse)
async def read_index():
    html_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(status_code=404, detail="index.html не найден")

@app.post("/api/v1/generate-plan")
def generate_plan(request: HousePlanRequest):
    try:
        G = nx.Graph()
        for room in request.rooms:
            G.add_node(room.name, min_area=room.min_area)
            for adj in room.preferred_adjacent:
                G.add_edge(room.name, adj)

        variants = solve_layout_variants(G, request.total_area, num_variants=10)
        return {"variants": variants}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/export-dxf")
def export_dxf_endpoint(req: ExportRequest):
    try:
        file_path = export_to_dxf(req.layout, file_path="house_plan.dxf")
        return FileResponse(path=file_path, media_type="application/dxf", filename="house_plan.dxf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/export-pdf")
def export_pdf_endpoint(req: ExportRequest):
    try:
        file_path = export_to_pdf(req.layout, file_path="house_plan.pdf")
        return FileResponse(path=file_path, media_type="application/pdf", filename="house_plan.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))