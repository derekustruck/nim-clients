#!/usr/bin/env python3
"""
Studio Voice Web UI
A Flask-based web interface for the Studio Voice NIM client
"""

import os
import sys
import json
import uuid
import threading
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import queue

# Add the parent directory to the path to import studio_voice
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'interfaces', 'studio_voice'))

# Import the studio voice processing functions
try:
    import studio_voice
    import grpc
    import studiovoice_pb2
    import studiovoice_pb2_grpc
    import soundfile as sf
    import numpy as np
    STUDIO_VOICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import studio voice modules: {e}")
    STUDIO_VOICE_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'studio-voice-ui-secret'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

socketio = SocketIO(app, cors_allowed_origins="*")

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

def process_audio_with_studio_voice(input_path, output_path, model_type="48k-hq", streaming=False, 
                                   server_target="127.0.0.1:8001", progress_callback=None):
    """
    Process audio file using Studio Voice NIM
    
    Args:
        input_path: Path to input audio file
        output_path: Path to output audio file
        model_type: Model type to use (48k-hq, 48k-ll, 16k-hq)
        streaming: Whether to use streaming mode
        server_target: gRPC server target
        progress_callback: Function to call with progress updates
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not STUDIO_VOICE_AVAILABLE:
        raise Exception("Studio Voice modules not available")
    
    try:
        # Create gRPC channel
        channel = grpc.insecure_channel(server_target)
        
        # Read audio file to get sample rate
        audio_data, sample_rate = sf.read(input_path)
        
        if progress_callback:
            progress_callback(10)
        
        # Create stub
        stub = studiovoice_pb2_grpc.MaxineStudioVoiceStub(channel)
        
        if progress_callback:
            progress_callback(20)
        
        # Generate request using the existing function
        request_generator = studio_voice.generate_request_for_inference(
            input_filepath=input_path,
            model_type=model_type,
            sample_rate=sample_rate,
            streaming=streaming
        )
        
        if progress_callback:
            progress_callback(40)
        
        # Process the request
        responses = stub.EnhanceAudio(request_generator)
        
        if progress_callback:
            progress_callback(60)
        
        # Write output using existing function
        studio_voice.write_output_file_from_response(
            response_iter=responses,
            output_filepath=output_path,
            sample_rate=sample_rate,
            streaming=streaming
        )
        
        if progress_callback:
            progress_callback(100)
        
        return True
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        raise e
    finally:
        try:
            channel.close()
        except:
            pass

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
                
                # Emit status update
                socketio.emit('job_status_update', job.to_dict())
                
                try:
                    # Process the audio file
                    output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"enhanced_{job.filename}")
                    
                    def progress_callback(progress):
                        job.progress = progress
                        socketio.emit('job_progress_update', {
                            'job_id': job.job_id,
                            'progress': progress
                        })
                    
                    # Use actual studio voice processing if available
                    if STUDIO_VOICE_AVAILABLE:
                        success = process_audio_with_studio_voice(
                            job.file_path, 
                            output_path, 
                            job.model_type, 
                            job.streaming,
                            progress_callback=progress_callback
                        )
                        
                        if success:
                            job.status = JobStatus.COMPLETED
                            job.output_path = output_path
                        else:
                            job.status = JobStatus.FAILED
                            job.error_message = "Processing failed"
                    else:
                        # Fallback: simulate processing for demo purposes
                        for progress in range(0, 101, 10):
                            time.sleep(0.5)
                            progress_callback(progress)
                        
                        # Copy input to output for demo
                        import shutil
                        shutil.copy2(job.file_path, output_path)
                        job.status = JobStatus.COMPLETED
                        job.output_path = output_path
                    
                    job.completed_at = datetime.now()
                    job.progress = 100
                    
                except Exception as e:
                    job.status = JobStatus.FAILED
                    job.error_message = str(e)
                    job.completed_at = datetime.now()
                
                # Move job to history
                job_history.append(job)
                if job.job_id in current_jobs:
                    del current_jobs[job.job_id]
                
                # Emit final status
                socketio.emit('job_status_update', job.to_dict())
                
                is_processing = False
            else:
                time.sleep(1)  # Wait before checking queue again
                
        except Exception as e:
            print(f"Error in processing thread: {e}")
            is_processing = False

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    model_type = request.form.get('model_type', '48k-hq')
    streaming = request.form.get('streaming', 'false').lower() == 'true'
    
    uploaded_jobs = []
    
    for file in files:
        if file.filename == '':
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
    
    return jsonify({
        'message': f'Uploaded {len(uploaded_jobs)} files',
        'jobs': uploaded_jobs
    })

@app.route('/api/jobs')
def get_jobs():
    """Get current jobs and history"""
    return jsonify({
        'current_jobs': [job.to_dict() for job in current_jobs.values()],
        'job_history': [job.to_dict() for job in job_history[-50:]],  # Last 50 jobs
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
            
            socketio.emit('job_status_update', job.to_dict())
            return jsonify({'message': 'Job cancelled'})
        else:
            return jsonify({'error': 'Job cannot be cancelled'}), 400
    else:
        return jsonify({'error': 'Job not found'}), 404

@app.route('/api/download/<job_id>')
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

@app.route('/api/settings')
def get_settings():
    """Get current settings"""
    return jsonify({
        'model_types': ['48k-hq', '48k-ll', '16k-hq'],
        'default_model_type': '48k-hq',
        'max_file_size': app.config['MAX_CONTENT_LENGTH'],
        'allowed_extensions': ['wav', 'mp3', 'flac', 'm4a']
    })

def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = {'wav', 'mp3', 'flac', 'm4a'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to Studio Voice UI'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    # Start the processing thread
    processing_thread = threading.Thread(target=process_jobs, daemon=True)
    processing_thread.start()
    
    # Run the Flask app
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
