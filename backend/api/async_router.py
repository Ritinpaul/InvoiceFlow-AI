"""Async processing endpoints"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import shutil
import uuid

try:
    from tasks.invoice_tasks import process_invoice_async, batch_process
    from celery.result import AsyncResult
    from celery_config import celery_app
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

from cache.redis_cache import cache

router = APIRouter(prefix="/async", tags=["Async Processing"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_async(file: UploadFile = File(...)):
    """Upload invoice for async processing"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Async processing not available")
    
    allowed = ['jpg', 'jpeg', 'png', 'pdf']
    ext = file.filename.split(".")[-1].lower()
    
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Use: {allowed}")
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    task = process_invoice_async.apply_async(args=[file_path], priority=7)
    
    return {
        "status": "queued",
        "task_id": task.id,
        "message": "Invoice queued for processing"
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get task status"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Async processing not available")
    
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {"task_id": task_id, "status": task_result.state}
    
    if task_result.state == 'SUCCESS':
        response["result"] = task_result.result
    elif task_result.state == 'FAILURE':
        response["error"] = str(task_result.info)
    
    return response


@router.post("/batch")
async def batch_upload(files: List[UploadFile] = File(...)):
    """Batch upload invoices"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Async processing not available")
    
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Max 50 files per batch")
    
    file_paths = []
    for file in files:
        ext = file.filename.split(".")[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'pdf']:
            continue
        
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_paths.append(file_path)
    
    task = batch_process.apply_async(args=[file_paths], priority=5)
    
    return {
        "status": "queued",
        "task_id": task.id,
        "files_queued": len(file_paths)
    }


@router.get("/queue/stats")
async def get_queue_stats():
    """Get queue statistics"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Async processing not available")
    
    inspect = celery_app.control.inspect()
    active = inspect.active() or {}
    scheduled = inspect.scheduled() or {}
    
    return {
        "active_tasks": sum(len(tasks) for tasks in active.values()),
        "scheduled_tasks": sum(len(tasks) for tasks in scheduled.values()),
        "workers": len(active)
    }


@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    try:
        stats = cache.get_cache_stats()
        total = stats['hits'] + stats['misses']
        hit_rate = (stats['hits'] / total * 100) if total > 0 else 0
        
        return {**stats, "hit_rate": round(hit_rate, 2)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cache unavailable: {str(e)}")
