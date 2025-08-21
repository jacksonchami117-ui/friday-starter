"""
Render module for FRIDAY system.
Handles video rendering job queue with status tracking.
"""

import os
import json
import uuid
import time
import threading
import csv
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from src.auth import login_required

render_bp = Blueprint('render', __name__, url_prefix='/render')

class JobStore:
    """Simple in-memory job store with file persistence."""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.jobs_file = os.path.join(data_dir, 'render_jobs.json')
        self.jobs = {}
        self.lock = threading.Lock()
        self.load_jobs()
    
    def load_jobs(self):
        """Load jobs from file."""
        if os.path.exists(self.jobs_file):
            try:
                with open(self.jobs_file, 'r') as f:
                    self.jobs = json.load(f)
            except Exception as e:
                current_app.logger.error(f"Error loading jobs: {e}")
                self.jobs = {}
    
    def save_jobs(self):
        """Save jobs to file."""
        try:
            with open(self.jobs_file, 'w') as f:
                json.dump(self.jobs, f, default=str, indent=2)
        except Exception as e:
            current_app.logger.error(f"Error saving jobs: {e}")
    
    def create_job(self, job_data):
        """Create a new job."""
        with self.lock:
            job_id = str(uuid.uuid4())
            job = {
                'id': job_id,
                'status': 'queued',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'progress': 0,
                'message': 'Job queued for processing',
                **job_data
            }
            self.jobs[job_id] = job
            self.save_jobs()
            return job_id
    
    def update_job(self, job_id, updates):
        """Update job status and data."""
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].update(updates)
                self.jobs[job_id]['updated_at'] = datetime.now().isoformat()
                self.save_jobs()
                return True
        return False
    
    def get_job(self, job_id):
        """Get job by ID."""
        return self.jobs.get(job_id)
    
    def get_all_jobs(self):
        """Get all jobs sorted by created_at desc."""
        jobs_list = list(self.jobs.values())
        return sorted(jobs_list, key=lambda x: x['created_at'], reverse=True)

# Global job store instance
job_store = None

def get_job_store():
    """Get or create job store instance."""
    global job_store
    if job_store is None:
        data_dir = current_app.config.get('DATA_DIR', 'state')
        job_store = JobStore(data_dir)
    return job_store

def process_render_job(job_id, app):
    """Process a render job in background with application context."""
    with app.app_context():
        store = get_job_store()
        job = store.get_job(job_id)
        
        if not job:
            return
        
        try:
            # Update status to processing
            store.update_job(job_id, {
                'status': 'processing',
                'message': 'Processing render job...',
                'progress': 10
            })
            
            # Simulate processing time and create output files
            data_dir = current_app.config.get('DATA_DIR', 'state')
            outputs_dir = os.path.join(data_dir, 'outputs', 'videos')
            os.makedirs(outputs_dir, exist_ok=True)
            
            # Read leads data
            leads_file = os.path.join(data_dir, 'uploads', 'accepted_leads.csv')
            if not os.path.exists(leads_file):
                store.update_job(job_id, {
                    'status': 'failed',
                    'message': 'No leads file found',
                    'progress': 0
                })
                return
            
            # Process leads and create video files
            with open(leads_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                leads = list(reader)
            
            total_leads = len(leads)
            processed = 0
            output_files = []
            
            for i, lead in enumerate(leads):
                # Simulate processing time
                time.sleep(0.5)  # Quick for demo
                
                # Create dummy video file
                first_name = lead.get('first_name', lead.get('First Name', f'lead_{i+1}'))
                video_filename = f"video_{first_name.lower()}_{int(time.time())}_{i+1}.mp4"
                video_path = os.path.join(outputs_dir, video_filename)
                
                # Create a dummy video file (in real scenario this would be FFmpeg)
                with open(video_path, 'w') as f:
                    f.write(f"# Dummy video file for {first_name}\n")
                    f.write(f"# Created at: {datetime.now()}\n")
                    f.write(f"# Lead data: {json.dumps(lead)}\n")
                
                output_files.append({
                    'filename': video_filename,
                    'path': video_path,
                    'lead_name': first_name,
                    'size': os.path.getsize(video_path)
                })
                
                processed += 1
                progress = int((processed / total_leads) * 80) + 10  # 10-90%
                
                store.update_job(job_id, {
                    'progress': progress,
                    'message': f'Processed {processed}/{total_leads} leads...'
                })
            
            # Final completion
            store.update_job(job_id, {
                'status': 'done',
                'progress': 100,
                'message': f'Successfully rendered {processed} videos',
                'output_files': output_files,
                'completed_at': datetime.now().isoformat()
            })
            
            current_app.logger.info(f"Render job {job_id} completed successfully")
            
        except Exception as e:
            current_app.logger.error(f"Render job {job_id} failed: {e}")
            store.update_job(job_id, {
                'status': 'failed',
                'message': f'Job failed: {str(e)}',
                'progress': 0
            })

@render_bp.route('/list')
@login_required
def render_list():
    """Display render job list."""
    store = get_job_store()
    jobs = store.get_all_jobs()
    return render_template('render_list.html', jobs=jobs)

@render_bp.route('/start', methods=['POST'])
@login_required 
def start_render():
    """Start a new render job."""
    try:
        # Validate that we have leads
        data_dir = current_app.config.get('DATA_DIR', 'state')
        leads_file = os.path.join(data_dir, 'uploads', 'accepted_leads.csv')
        
        if not os.path.exists(leads_file):
            flash('No leads found. Please upload leads first.', 'error')
            return redirect(url_for('render.render_list'))
        
        # Create job
        store = get_job_store()
        job_data = {
            'type': 'video_render',
            'leads_file': leads_file,
            'requested_by': request.form.get('user', 'anonymous')
        }
        
        job_id = store.create_job(job_data)
        
        # Start background processing
        thread = threading.Thread(target=process_render_job, args=(job_id, current_app._get_current_object()))
        thread.daemon = True
        thread.start()
        
        flash(f'Render job started successfully! Job ID: {job_id}', 'success')
        current_app.logger.info(f"Started render job {job_id}")
        
        return redirect(url_for('render.render_status', job_id=job_id))
        
    except Exception as e:
        current_app.logger.error(f"Error starting render job: {e}")
        flash(f'Error starting render job: {str(e)}', 'error')
        return redirect(url_for('render.render_list'))

@render_bp.route('/status/<job_id>')
@login_required
def render_status(job_id):
    """Display render job status."""
    store = get_job_store()
    job = store.get_job(job_id)
    
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('render.render_list'))
    
    return render_template('render_status.html', job=job)

@render_bp.route('/api/status/<job_id>')
@login_required
def api_job_status(job_id):
    """API endpoint for job status."""
    store = get_job_store()
    job = store.get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)

@render_bp.route('/api/jobs')
@login_required 
def api_jobs_list():
    """API endpoint for jobs list."""
    store = get_job_store()
    jobs = store.get_all_jobs()
    return jsonify({'jobs': jobs})