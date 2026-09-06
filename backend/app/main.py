import os
import io
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.solver_engine import solve_layout_variants
from app.graph_builder import build_graph_from_rooms
from app.pdf_exporter import export_to_pdf
from app.dxf_exporter import export_to_dxf

app = FastAPI(title="AI House Planner API", version="2.0")

# --- Настройка CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic-схема запроса ---
class HouseRequest(BaseModel):
    area: float
    rooms: List[str]

# --- Эндпоинты ---
@app.get("/")
def root():
    return {"status": "ok", "service": "AI House Planner API v2.0"}

@app.post("/generate")
def generate_house_plans(request: HouseRequest):
    """
    Строит граф помещений и вызывает solve_layout_variants для генерации 10 вариантов.
    """
    try:
        graph = build_graph_from_rooms(request.rooms)
        variants = solve_layout_variants(graph=graph, total_area=request.area, num_variants=10)
        
        return {
            "status": "success",
            "area": request.area,
            "requested_rooms": request.rooms,
            "count": len(variants),
            "plans": variants
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")

@app.post("/export/pdf")
def export_pdf(plan_data: dict):
    """
    Генерирует PDF-чертёж выбранного варианта.
    """
    try:
        pdf_bytes = export_to_pdf(plan_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=house_plan.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта в PDF: {str(e)}")

@app.post("/export/dxf")
def export_dxf(plan_data: dict):
    """
    Генерирует CAD-чертёж (.dxf) выбранного варианта.
    """
    try:
        dxf_bytes = export_to_dxf(plan_data)
        return Response(
            content=dxf_bytes,
            media_type="application/dxf",
            headers={"Content-Disposition": "attachment; filename=house_plan.dxf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта в DXF: {str(e)}")