import os
import io
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Подставьте ТЕ имена функций, которые фактически объявлены в ваших файлах:
from app.solver_engine import generate_plans  # Замените generate_layouts на реальное имя
from app.pdf_exporter import export_to_pdf
from app.dxf_exporter import export_to_dxf

app = FastAPI(title="AI House Planner API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HouseRequest(BaseModel):
    area: float
    rooms: List[str]

@app.get("/")
def root():
    return {"status": "ok", "service": "AI House Planner API v2.0"}

@app.post("/generate")
def generate_house_plans(request: HouseRequest):
    try:
        # Используем правильное имя функции
        variants = generate_plans(area=request.area, rooms=request.rooms)
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
    try:
        dxf_bytes = export_to_dxf(plan_data)
        return Response(
            content=dxf_bytes,
            media_type="application/dxf",
            headers={"Content-Disposition": "attachment; filename=house_plan.dxf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта в DXF: {str(e)}")