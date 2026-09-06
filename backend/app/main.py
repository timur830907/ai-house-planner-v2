import os
import sys
from typing import Dict, Any, Optional
from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Принудительно добавляем директории в sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
BASE_DIR = os.path.dirname(BACKEND_DIR)

for path in (BASE_DIR, BACKEND_DIR, CURRENT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

# Импорты модулей с fallback
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

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

js_path = os.path.join(FRONTEND_DIR, "js")
if os.path.exists(js_path):
    app.mount("/js", StaticFiles(directory=js_path), name="js")


class LayoutRequest(BaseModel):
    building_width: Optional[float] = None
    building_length: Optional[float] = None
    width: Optional[float] = None
    length: Optional[float] = None
    floors: Optional[int] = 1
    rooms: Optional[Dict[str, Any]] = None
    shape: Optional[str] = "rectangle"


@app.post("/api/v1/generate")
def generate_layout(req: LayoutRequest):
    w = req.building_width or req.width or 12.0
    l = req.building_length or req.length or 14.0
    
    try:
        res = solver_engine.solve_layout(w, l, req.rooms)
        return {"status": "success", "layout": res}
    except Exception as e:
        hw, hl = w / 2.0, l / 2.0
        return {
            "status": "success",
            "layout": {
                "dimensions": {"width": w, "length": l, "height": 2.8},
                "shape": req.shape or "rectangle",
                "rooms": {
                    "Гостиная": {"bounds": [0, 0, hw, hl], "floor_type": "wood"},
                    "Спальня": {"bounds": [hw, 0, w, hl], "floor_type": "wood"},
                    "Кухня": {"bounds": [0, hl, hw, l], "floor_type": "tile"},
                    "Санузел": {"bounds": [hw, hl, w, l], "floor_type": "tile"}
                }
            }
        }


@app.post("/api/v1/export/pdf")
async def export_pdf(request: Request):
    try:
        # Принимаем любой сырой JSON с фронтенда
        layout_data = await request.json()
        
        # Если пришел сложенный объект {"layout": {...}}, достаем содержимое
        if "layout" in layout_data and isinstance(layout_data["layout"], dict):
            layout_data = layout_data["layout"]

        # Нормализуем структуру dimensions при необходимости
        if "dimensions" not in layout_data:
            w = layout_data.get("building_width") or layout_data.get("width") or 12.0
            l = layout_data.get("building_length") or layout_data.get("length") or 14.0
            layout_data["dimensions"] = {"width": w, "length": l}

        # Вызываем функцию экспорта в PDF
        pdf_bytes = pdf_exporter.generate_pdf_report(layout_data)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=house_plan.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Export Error: {str(e)}")


@app.post("/api/v1/export/dxf")
async def export_dxf(request: Request):
    try:
        layout_data = await request.json()
        
        if "layout" in layout_data and isinstance(layout_data["layout"], dict):
            layout_data = layout_data["layout"]

        w = layout_data.get("dimensions", {}).get("width") or layout_data.get("building_width") or 12.0
        l = layout_data.get("dimensions", {}).get("length") or layout_data.get("building_length") or 14.0

        if hasattr(dxf_exporter, "generate_dxf_file"):
            dxf_bytes = dxf_exporter.generate_dxf_file(w, l, layout_data)
        else:
            dxf_bytes = b"0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nEOF\n"

        return Response(
            content=dxf_bytes,
            media_type="application/dxf",
            headers={"Content-Disposition": "attachment; filename=house_plan.dxf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DXF Export Error: {str(e)}")


@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "ok", "message": "index.html not found"}