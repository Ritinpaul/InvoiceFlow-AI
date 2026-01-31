"""Async invoice processing tasks"""
from celery_config import celery_app
from orchestrator.orchestrator import InvoiceOrchestrator
from cache.redis_cache import cache
import asyncio
from typing import Dict, Any, List

@celery_app.task(name='tasks.invoice_tasks.process_invoice_async', bind=True, max_retries=3)
def process_invoice_async(self, file_path: str, session_id: str = None) -> Dict[str, Any]:
    """Process invoice in background"""
    try:
        self.update_state(state='PROCESSING', meta={'stage': 'initializing'})
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        orchestrator = InvoiceOrchestrator()
        result = loop.run_until_complete(orchestrator.process_invoice(file_path, session_id))
        
        loop.close()
        
        if result.get("extraction", {}).get("invoice_number"):
            invoice_num = result["extraction"]["invoice_number"]
            cache.cache_invoice(invoice_num, result, ttl=2592000)
        
        cache.invalidate_stats()
        
        return {
            "status": "completed",
            "result": result,
            "task_id": self.request.id
        }
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise self.retry(exc=e, countdown=60)


@celery_app.task(name='tasks.invoice_tasks.batch_process')
def batch_process(file_paths: List[str]) -> Dict[str, Any]:
    """Batch process multiple invoices"""
    results = []
    successful = 0
    failed = 0
    
    for file_path in file_paths:
        try:
            task_result = process_invoice_async.apply_async(args=[file_path], priority=3)
            results.append({
                "file": file_path,
                "task_id": task_result.id,
                "status": "queued"
            })
            successful += 1
        except Exception as e:
            results.append({
                "file": file_path,
                "status": "failed",
                "error": str(e)
            })
            failed += 1
    
    return {
        "total": len(file_paths),
        "successful": successful,
        "failed": failed,
        "results": results
    }
