import os
from celery import Celery
from celery.utils.log import get_task_logger

# Configure Celery
celery_app = Celery(
    'friday',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=['src.render_engine']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Create celery instance for import
celery = celery_app

logger = get_task_logger(__name__)

@celery_app.task(bind=True)
def render_video_task(self, lead_data, template_config):
    """Render personalized video for a lead"""
    try:
        logger.info(f"Starting video render for lead: {lead_data.get('email', 'unknown')}")
        
        # Import here to avoid circular imports
        from src.render_engine import render_personalized_video
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Initializing render...'}
        )
        
        # Render the video
        result = render_personalized_video(lead_data, template_config, progress_callback=self.update_state)
        
        logger.info(f"Video render completed for lead: {lead_data.get('email', 'unknown')}")
        return {
            'status': 'success',
            'video_path': result.get('video_path'),
            'thumbnail_path': result.get('thumbnail_path')
        }
        
    except Exception as exc:
        logger.error(f"Video render failed for lead {lead_data.get('email', 'unknown')}: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task(bind=True)
def batch_render_task(self, leads_data, template_config):
    """Render videos for multiple leads in batch"""
    try:
        logger.info(f"Starting batch render for {len(leads_data)} leads")
        
        results = []
        total_leads = len(leads_data)
        
        for i, lead_data in enumerate(leads_data):
            # Update progress
            progress = int((i / total_leads) * 100)
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': total_leads,
                    'status': f'Rendering lead {i + 1}/{total_leads}'
                }
            )
            
            # Render individual video
            result = render_video_task.delay(lead_data, template_config)
            results.append({
                'lead_email': lead_data.get('email'),
                'task_id': result.id,
                'status': 'queued'
            })
        
        logger.info(f"Batch render queued for {len(leads_data)} leads")
        return {
            'status': 'success',
            'total_leads': total_leads,
            'tasks': results
        }
        
    except Exception as exc:
        logger.error(f"Batch render failed: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=2)

@celery_app.task
def cleanup_old_files_task():
    """Clean up old rendered files"""
    try:
        import os
        import time
        from datetime import datetime, timedelta
        
        data_dir = os.getenv('STATE_DIR', 'state')
        outputs_dir = os.path.join(data_dir, 'outputs', 'videos')
        thumbs_dir = os.path.join(data_dir, 'outputs', 'thumbs')
        
        # Cleanup files older than 7 days
        cutoff_time = time.time() - (7 * 24 * 60 * 60)
        cleaned_count = 0
        
        for directory in [outputs_dir, thumbs_dir]:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        cleaned_count += 1
        
        logger.info(f"Cleanup completed: removed {cleaned_count} old files")
        return {'status': 'success', 'cleaned_count': cleaned_count}
        
    except Exception as exc:
        logger.error(f"Cleanup task failed: {exc}")
        return {'status': 'error', 'error': str(exc)}

if __name__ == '__main__':
    celery_app.start()
