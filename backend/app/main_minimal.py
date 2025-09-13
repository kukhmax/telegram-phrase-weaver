#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Минимальная версия main.py для диагностики проблем запуска
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

# Создаем приложение FastAPI
app = FastAPI(
    title="Phrase Weaver API (Minimal)",
    description="Минимальная версия для диагностики",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Базовые роуты
@app.get("/")
async def root():
    return {"message": "Phrase Weaver API работает (минимальная версия)"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "minimal"}

@app.get("/api/test")
async def api_test():
    return {"api": "working", "message": "API эндпоинт работает"}

# Статические файлы
static_path = Path("/app/frontend")
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = static_path / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(str(favicon_path))
        return {"error": "favicon not found"}
    
    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        # Обслуживание frontend файлов
        if not path or path == "/":
            index_path = static_path / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
        
        file_path = static_path / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # Fallback на index.html для SPA
        index_path = static_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        
        return {"error": "File not found", "path": path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)