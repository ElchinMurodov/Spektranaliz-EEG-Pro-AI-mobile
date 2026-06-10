"""
main.py — Spektranaliz EEG Pro AI mobil backend (FastAPI).

Bu server ish stoli dasturidagi BIR XIL `eeg_engine` tahlil yadrosini REST API
ko'rinishida taqdim etadi. Android/iOS ilovasi EEG faylni yuklaydi, server uni
tahlil qilib, JSON natija (holat, ballar, ritmlar, PSD, hisobot) qaytaradi.

Ishga tushirish (mahalliy):
    pip install -r requirements.txt
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Endpointlar:
    GET  /                 — server haqida qisqa ma'lumot
    GET  /health           — holat tekshiruvi (mobil ilova ulanishni tekshiradi)
    GET  /api/states       — aniqlanadigan funksional holatlar ro'yxati
    POST /api/analyze      — EEG fayl yuklash -> JSON tahlil natijasi
    POST /api/report/html  — EEG fayl yuklash -> HTML vizual hisobot
"""

from __future__ import annotations

import os
import tempfile
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from eeg_engine import config, pipeline, visualize
from app.analysis import analyze

# Qabul qilinadigan fayl kengaytmalari
ALLOWED_EXT = {".edf", ".bdf", ".csv"}
# Maksimal yuklash hajmi (xavfsizlik uchun) — 64 MB
MAX_UPLOAD_BYTES = 64 * 1024 * 1024

app = FastAPI(
    title="Spektranaliz EEG Pro AI — Mobile API",
    description="Sportchining EEG signallarini spektral tahlil qilish (mobil backend).",
    version=config.APP_VERSION,
)

# Mobil ilova istalgan tarmoqdan ulanishi uchun CORS ochiq. Ishlab chiqarishda
# (production) bu ro'yxatni faqat kerakli domenlar bilan cheklang.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _save_upload(file: UploadFile) -> str:
    """Yuklangan faylni vaqtinchalik diskka saqlaydi va yo'lini qaytaradi."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            status_code=400,
            detail="Qo'llab-quvvatlanmaydigan format: '%s'. Ruxsat etilgan: %s"
            % (ext or "(yo'q)", ", ".join(sorted(ALLOWED_EXT))),
        )
    data = file.file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Bo'sh fayl yuklandi.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Fayl hajmi juda katta (maks. %d MB)." % (MAX_UPLOAD_BYTES // (1024 * 1024)),
        )
    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)
    return tmp_path


@app.get("/")
def root():
    return {
        "name": config.APP_NAME,
        "version": config.APP_VERSION,
        "author": config.AUTHOR,
        "description": "Sportchining EEG signallarini spektral tahlil qilish — mobil backend.",
        "endpoints": ["/health", "/api/states", "/api/analyze", "/api/report/html", "/docs"],
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": config.APP_VERSION}


@app.get("/api/states")
def states():
    """Aniqlanadigan 8 funksional holat va ritm diapazonlari."""
    return {
        "states": config.STATES,
        "bands": {k: list(v) for k, v in config.BANDS.items()},
        "band_labels": config.BAND_LABELS,
    }


@app.post("/api/analyze")
async def api_analyze(
    file: UploadFile = File(..., description="EEG fayl (EDF/EDF+/BDF/BDF+/CSV)"),
    fs: Optional[float] = Form(None, description="Namuna chastotasi (CSV uchun), Hz"),
    target_fs: Optional[float] = Form(None, description="Harmonizatsiya chastotasi, Hz"),
    notch: bool = Form(True, description="50/60 Hz tarmoq filtri"),
    reader: str = Form("auto", description="O'qish usuli: auto|pyedflib|mne|pure"),
):
    """EEG faylni tahlil qilib, mobil ilova uchun JSON natija qaytaradi."""
    tmp_path = _save_upload(file)
    try:
        result = analyze(tmp_path, fs=fs, target_fs=target_fs,
                         notch=notch, prefer=reader)
        # Yuklangan asl fayl nomini ko'rsatamiz (vaqtinchalik yo'l emas)
        result["summary"]["source_file"] = file.filename
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as exc:  # tahlil xatosi -> tushunarli xabar
        raise HTTPException(status_code=422, detail="Tahlil xatosi: %s" % exc)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


@app.post("/api/report/html", response_class=HTMLResponse)
async def api_report_html(
    file: UploadFile = File(...),
    fs: Optional[float] = Form(None),
    target_fs: Optional[float] = Form(None),
    notch: bool = Form(True),
    reader: str = Form("auto"),
    topo_band: str = Form("alpha"),
):
    """EEG faylni tahlil qilib, to'liq HTML vizual hisobotni qaytaradi."""
    tmp_path = _save_upload(file)
    try:
        objs = pipeline.analyze_objects(
            tmp_path, fs=fs, target_fs=target_fs, notch=notch, prefer=reader)
        html = visualize.build_html(
            objs["rec"], objs["spec"], objs["features"],
            objs["classification"], topo_band=topo_band)
        return HTMLResponse(content=html)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Hisobot xatosi: %s" % exc)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
