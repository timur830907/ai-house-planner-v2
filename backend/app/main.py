import os
import io
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Импорты ваших локальных модулей генерации и экспорта
from app.solver_engine import generate_layouts  # Предполагаемая функция решения/генерации
from app.pdf_exporter import export_to_pdf
from app.dxf_exporter import export_to_dxf

app = FastAPI(title="AI House Planner API", version="2.0")

# --- Настройка CORS ---
# Позволяет фронтенду (на Vercel, Netlify, Render или локально) делать запросы к бэкенду
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic-схемы запросов и ответов ---
class HouseRequest(BaseModel):
    area: float
    rooms: List[str]

class LayoutVariant(BaseModel):
    id: int
    rooms_data: dict
    score: Optional[float] = None


# --- Эндпоинты ---

@app.get("/")
def root():
    return {"status": "ok", "service": "AI House Planner API v2.0"}


@app.post("/generate")
def generate_house_plans(request: HouseRequest):
    """
    Генерирует варианты планировок на основе площади и списка комнат.
    """
    try:
        # Вызов вашего алгоритма генерации
        variants = generate_layouts(area=request.area, rooms=request.rooms)
        
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
    Генерирует PDF-чертёж выбранного варианта с помощью reportlab.
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
    try:
        dxf_bytes = export_to_dxf(plan_data)
        return Response(
            content=dxf_bytes,
            media_type="application/dxf",
            headers={"Content-Disposition": "attachment; filename=house_plan.dxf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта в DXF: {str(e)}")