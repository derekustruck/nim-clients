#!/usr/bin/env python3
"""
Studio Voice Simple Web UI
A simplified Flask-based web interface for the Studio Voice NIM client
Uses polling instead of WebSockets to avoid compatibility issues
"""

import os
import sys
import json
import uuid
import threading
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import queue
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'studio-voice-simple-ui-secret'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Global variables for job management
job_queue = queue.Queue()
current_jobs = {}
job_history = []
processing_thread = None
is_processing = False

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

class JobStatus:
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingJob:
    def __init__(self, job_id, file_path, filename, model_type="48k-hq", streaming=False):
        self.job_id = job_id
        self.file_path = file_path
        self.filename = filename
        self.model_type = model_type
        self.streaming = streaming
        self.status = JobStatus.QUEUED
        self.progress = 0
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.output_path = None
        # For proper file management like the original script
        self.original_path = None
        self.relative_path = None

    def to_dict(self):
        return {
            'job_id': self.job_id,
            'filename': self.filename,
            'model_type': self.model_type,
            'streaming': self.streaming,
            'status': self.status,
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'output_path': self.output_path
        }

def process_jobs():
    """Background thread to process jobs from the queue"""
    global is_processing
    
    while True:
        try:
            if not job_queue.empty():
                job = job_queue.get()
                is_processing = True
                
                # Update job status
                job.status = JobStatus.PROCESSING
                job.started_at = datetime.now()
                current_jobs[job.job_id] = job
                
                try:
                    # Process the audio file with proper file management
                    if hasattr(job, 'original_path') and job.original_path:
                        # This is from folder mode - replace original file
                        output_path = job.original_path
                        backup_dir = os.path.join(os.path.dirname(job.original_path), '..', 'original audio')
                        backup_file = os.path.join(backup_dir, job.filename)
                        
                        # Create backup directory if it doesn't exist
                        os.makedirs(backup_dir, exist_ok=True)
                        
                        # Move original to backup location
                        shutil.move(job.original_path, backup_file)
                        
                    else:
                        # This is from file upload mode - save to output folder
                        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"enhanced_{job.filename}")
                    
                    # Simulate processing with progress updates
                    for progress in range(0, 101, 10):
                        time.sleep(0.5)  # Simulate processing time
                        job.progress = progress
                    
                    # TODO: Replace with actual studio voice processing
                    # For now, copy the input to the output location
                    shutil.copy2(job.file_path, output_path)
                    
                    job.status = JobStatus.COMPLETED
                    job.completed_at = datetime.now()
                    job.output_path = output_path
                    job.progress = 100
                    
                except Exception as e:
                    job.status = JobStatus.FAILED
                    job.error_message = str(e)
                    job.completed_at = datetime.now()
                    
                    # If we moved the original file, restore it
                    if hasattr(job, 'original_path') and job.original_path:
                        try:
                            backup_dir = os.path.join(os.path.dirname(job.original_path), '..', 'original audio')
                            backup_file = os.path.join(backup_dir, job.filename)
                            if os.path.exists(backup_file):
                                shutil.move(backup_file, job.original_path)
                        except:
                            pass  # Don't fail the whole process if restore fails
                
                # Move job to history
                job_history.append(job)
                if job.job_id in current_jobs:
                    del current_jobs[job.job_id]
                
                is_processing = False
            else:
                time.sleep(1)  # Wait before checking queue again
                
        except Exception as e:
            print(f"Error in processing thread: {e}")
            is_processing = False

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('simple_index.html')

@app.route('/api/scan-folder', methods=['POST'])
def scan_folder():
    """Scan a folder for audio files"""
    data = request.get_json()
    folder_path = data.get('folder_path', '').strip()
    
    if not folder_path:
        return jsonify({'error': 'No folder path provided'}), 400
    
    if not os.path.exists(folder_path):
        return jsonify({'error': 'Folder does not exist'}), 400
    
    if not os.path.isdir(folder_path):
        return jsonify({'error': 'Path is not a directory'}), 400
    
    try:
        audio_extensions = {'.wav', '.mp3', '.flac', '.m4a'}
        files = []
        
        # Walk through all subdirectories
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                if Path(filename).suffix.lower() in audio_extensions:
                    files.append(os.path.join(root, filename))
        
        return jsonify({
            'files': files,
            'count': len(files),
            'folder_path': folder_path
        })
        
    except Exception as e:
        return jsonify({'error': f'Error scanning folder: {str(e)}'}), 500

@app.route('/upload', methods=['GET', 'POST'])
def upload_files():
    """Handle file uploads"""
    if request.method == 'GET':
        return render_template('upload.html')
    
    mode = request.form.get('mode', 'files')
    model_type = request.form.get('model_type', '48k-hq')
    streaming = request.form.get('streaming', 'false').lower() == 'true'
    
    uploaded_jobs = []
    
    if mode == 'folder':
        # Handle folder mode
        folder_path = request.form.get('folder_path', '').strip()
        
        if not folder_path or not os.path.exists(folder_path):
            return jsonify({'error': 'Invalid folder path'}), 400
        
        # Scan folder for audio files
        audio_extensions = {'.wav', '.mp3', '.flac', '.m4a'}
        files_to_process = []
        
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                if Path(filename).suffix.lower() in audio_extensions:
                    files_to_process.append({
                        'path': os.path.join(root, filename),
                        'filename': filename,
                        'relative_path': os.path.relpath(os.path.join(root, filename), folder_path)
                    })
        
        # Create jobs for each file
        for file_info in files_to_process:
            job_id = str(uuid.uuid4())
            # Copy file to upload folder with job_id prefix
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{file_info['filename']}")
            shutil.copy2(file_info['path'], upload_path)
            
            # Create processing job with original path info
            job = ProcessingJob(job_id, upload_path, file_info['filename'], model_type, streaming)
            job.original_path = file_info['path']  # Store original path for proper file management
            job.relative_path = file_info['relative_path']
            job_queue.put(job)
            current_jobs[job_id] = job
            uploaded_jobs.append(job.to_dict())
    
    else:
        # Handle individual files mode
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        
        for file in files:
            if file.filename == '' or not file.filename:
                continue
                
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                job_id = str(uuid.uuid4())
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
                file.save(file_path)
                
                # Create processing job
                job = ProcessingJob(job_id, file_path, filename, model_type, streaming)
                job_queue.put(job)
                current_jobs[job_id] = job
                uploaded_jobs.append(job.to_dict())
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Dashboard page with job status"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current status via polling"""
    return jsonify({
        'current_jobs': [job.to_dict() for job in current_jobs.values()],
        'job_history': [job.to_dict() for job in job_history[-20:]],  # Last 20 jobs
        'queue_size': job_queue.qsize(),
        'is_processing': is_processing
    })

@app.route('/api/jobs/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """Cancel a specific job"""
    if job_id in current_jobs:
        job = current_jobs[job_id]
        if job.status == JobStatus.QUEUED:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now()
            job_history.append(job)
            del current_jobs[job_id]
            return jsonify({'message': 'Job cancelled'})
        else:
            return jsonify({'error': 'Job cannot be cancelled'}), 400
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/download/<job_id>')
def download_result(job_id):
    """Download processed audio file"""
    # Look for job in history
    job = None
    for hist_job in job_history:
        if hist_job.job_id == job_id:
            job = hist_job
            break
    
    if job and job.output_path and os.path.exists(job.output_path):
        return send_file(job.output_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = {'wav', 'mp3', 'flac', 'm4a'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

if __name__ == '__main__':
    # Start the processing thread
    processing_thread = threading.Thread(target=process_jobs, daemon=True)
    processing_thread.start()
    
    # Run the Flask app
    print("Starting Studio Voice Simple Web UI...")
    print("Open your browser to: http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
