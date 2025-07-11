#!/usr/bin/env python3
"""
Studio Voice Desktop UI - Standalone Version
A tkinter-based desktop interface that handles dependencies more gracefully
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from pathlib import Path
from datetime import datetime
import subprocess
import shutil

class StudioVoiceDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Studio Voice - Audio Enhancement")
        self.root.geometry("800x600")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.selected_files = []
        self.processing_queue = queue.Queue()
        self.is_processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="WENS")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎵 Studio Voice Audio Enhancement", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Audio Files", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky="WE", pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Button(file_frame, text="Select Files", 
                  command=self.select_files).grid(row=0, column=0, padx=(0, 10))
        
        self.files_label = ttk.Label(file_frame, text="No files selected")
        self.files_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Button(file_frame, text="Select Folder", 
                  command=self.select_folder).grid(row=0, column=2, padx=(10, 0))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Processing Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky="WE", pady=(0, 10))
        
        # Model type
        ttk.Label(settings_frame, text="Model Type:").grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.model_var = tk.StringVar(value="48k-hq")
        model_combo = ttk.Combobox(settings_frame, textvariable=self.model_var, 
                                  values=["48k-hq", "48k-ll", "16k-hq"], state="readonly")
        model_combo.grid(row=0, column=1, padx=(0, 20), sticky=tk.W)
        
        # Streaming mode
        self.streaming_var = tk.BooleanVar()
        ttk.Checkbutton(settings_frame, text="Streaming Mode", 
                       variable=self.streaming_var).grid(row=0, column=2, sticky=tk.W)
        
        # Processing info
        ttk.Label(settings_frame, text="Processing Mode:", 
                 font=('Arial', 9, 'bold')).grid(row=1, column=0, padx=(0, 10), sticky=tk.W)
        ttk.Label(settings_frame, text="Files will be enhanced in place with originals backed up", 
                 foreground='blue').grid(row=1, column=1, columnspan=2, sticky=tk.W)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Processing frame
        process_frame = ttk.LabelFrame(main_frame, text="Processing", padding="10")
        process_frame.grid(row=3, column=0, columnspan=3, sticky="WENS", pady=(0, 10))
        process_frame.columnconfigure(0, weight=1)
        process_frame.rowconfigure(1, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(process_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="🚀 Start Processing", 
                                   command=self.start_processing, state=tk.DISABLED)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop Processing", 
                                  command=self.stop_processing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="🗑️ Clear Log", 
                                   command=self.clear_log)
        self.clear_btn.pack(side=tk.LEFT)
        
        # Add dependency check button
        self.check_deps_btn = ttk.Button(button_frame, text="🔧 Check Dependencies", 
                                        command=self.check_dependencies)
        self.check_deps_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(process_frame, mode='determinate')
        self.progress.grid(row=1, column=0, sticky="WE", padx=(0, 10))
        
        self.progress_label = ttk.Label(process_frame, text="Ready")
        self.progress_label.grid(row=1, column=1)
        
        # Log text area
        log_frame = ttk.Frame(process_frame)
        log_frame.grid(row=2, column=0, columnspan=2, sticky="WENS", pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky="WENS")
        scrollbar.grid(row=0, column=1, sticky="NS")
        
        # Initial log message
        self.log("Studio Voice Desktop UI initialized")
        self.log("Select audio files and configure settings to begin processing")
        self.log("💡 Use 'Check Dependencies' if you encounter import errors")
        
    def check_dependencies(self):
        """Check and install dependencies if needed"""
        self.log("🔧 Checking Studio Voice dependencies...")
        
        try:
            # Try to import required modules
            import grpc
            import soundfile
            import numpy
            
            # Try to import studio voice modules
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'interfaces', 'studio_voice'))
            
            import studiovoice_pb2
            import studiovoice_pb2_grpc
            
            self.log("✅ All dependencies are installed and working!")
            messagebox.showinfo("Dependencies Check", "All dependencies are installed and working correctly!")
            
        except ImportError as e:
            missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
            self.log(f"❌ Missing dependency: {missing_module}")
            
            result = messagebox.askyesno(
                "Missing Dependencies", 
                f"Missing required dependency: {missing_module}\n\n"
                "Would you like to try installing the Studio Voice requirements?\n\n"
                "This will run: pip install -r requirements.txt"
            )
            
            if result:
                self.install_dependencies()
                
    def install_dependencies(self):
        """Install Studio Voice dependencies"""
        self.log("📦 Installing Studio Voice dependencies...")
        
        try:
            # Find requirements.txt
            req_file = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
            
            if not os.path.exists(req_file):
                self.log("❌ requirements.txt not found")
                messagebox.showerror("Error", "requirements.txt not found in the studio-voice directory")
                return
            
            # Run pip install
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', req_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Dependencies installed successfully!")
                self.log("Please restart the application to use the new dependencies")
                messagebox.showinfo("Success", "Dependencies installed successfully!\nPlease restart the application.")
            else:
                self.log(f"❌ Failed to install dependencies: {result.stderr}")
                messagebox.showerror("Error", f"Failed to install dependencies:\n{result.stderr}")
                
        except Exception as e:
            self.log(f"❌ Error installing dependencies: {str(e)}")
            messagebox.showerror("Error", f"Error installing dependencies:\n{str(e)}")
    
    def select_files(self):
        """Select individual audio files"""
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.flac *.m4a"),
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("FLAC files", "*.flac"),
                ("M4A files", "*.m4a"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            self.selected_files = list(files)
            self.update_files_display()
            
    def select_folder(self):
        """Select a folder containing audio files"""
        folder = filedialog.askdirectory(title="Select Folder with Audio Files")
        
        if folder:
            # Find all audio files in the folder and subfolders
            audio_extensions = {'.wav', '.mp3', '.flac', '.m4a'}
            files = []
            
            for root, dirs, filenames in os.walk(folder):
                for filename in filenames:
                    if Path(filename).suffix.lower() in audio_extensions:
                        files.append(os.path.join(root, filename))
            
            if files:
                self.selected_files = files
                self.update_files_display()
                self.log(f"Found {len(files)} audio files in {folder}")
            else:
                messagebox.showwarning("No Files", "No audio files found in the selected folder")
                
    def update_files_display(self):
        """Update the files display and enable/disable start button"""
        if self.selected_files:
            count = len(self.selected_files)
            self.files_label.config(text=f"{count} file{'s' if count != 1 else ''} selected")
            self.start_btn.config(state=tk.NORMAL)
        else:
            self.files_label.config(text="No files selected")
            self.start_btn.config(state=tk.DISABLED)
            
    def log(self, message):
        """Add a message to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """Clear the log text"""
        self.log_text.delete(1.0, tk.END)
        
    def start_processing(self):
        """Start processing the selected files"""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select audio files to process")
            return
        
        # Confirm in-place processing
        result = messagebox.askyesno(
            "Confirm Processing", 
            f"This will process {len(self.selected_files)} files in place:\n\n"
            "• Enhanced audio will REPLACE the original files\n"
            "• Original files will be moved to '../original audio/' folders\n"
            "• Directory structure will be preserved\n\n"
            "Are you sure you want to continue?"
        )
        
        if not result:
            return
            
        # Disable start button, enable stop button
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_processing = True
        
        # Start processing in a separate thread
        self.processing_thread = threading.Thread(target=self.process_files, daemon=True)
        self.processing_thread.start()
        
    def stop_processing(self):
        """Stop the processing"""
        self.is_processing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_label.config(text="Stopped")
        self.log("Processing stopped by user")
        
    def process_files(self):
        """Process the selected files (runs in background thread)"""
        total_files = len(self.selected_files)
        successful = 0
        failed = 0
        
        self.log(f"Starting processing of {total_files} files...")
        self.log(f"Model: {self.model_var.get()}, Streaming: {self.streaming_var.get()}")
        self.log(f"Files will be enhanced in place with originals backed up")
        
        for i, input_file in enumerate(self.selected_files):
            if not self.is_processing:
                break
                
            # Update progress
            progress = (i / total_files) * 100
            self.progress['value'] = progress
            self.progress_label.config(text=f"Processing {i+1}/{total_files}")
            
            filename = os.path.basename(input_file)
            self.log(f"Processing: {filename}")
            
            try:
                # Process file in place (no separate output file needed)
                result = self.process_single_file(input_file)
                
                if result:
                    successful += 1
                    self.log(f"✅ Completed: {filename}")
                else:
                    failed += 1
                    self.log(f"❌ Failed: {filename}")
                    
            except Exception as e:
                failed += 1
                self.log(f"❌ Error processing {filename}: {str(e)}")
        
        # Final update
        self.progress['value'] = 100
        self.progress_label.config(text="Complete")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
        self.log(f"Processing complete! ✅ {successful} successful, ❌ {failed} failed")
        self.log("Enhanced files have replaced the originals")
        self.log("Original files have been moved to '../original audio/' folders")
        
        if successful > 0:
            messagebox.showinfo("Processing Complete", 
                              f"Successfully processed {successful} files!\n\n"
                              f"Enhanced files have replaced the originals.\n"
                              f"Original files backed up to '../original audio/' folders.")

    def process_single_file(self, input_file):
        """Process a single audio file using the existing Python script and manage files properly"""
        try:
            # Get the directory of the input file
            input_dir = os.path.dirname(input_file)
            filename = os.path.basename(input_file)
            
            # Create backup directory one level up from the audio file
            backup_dir = os.path.join(input_dir, '..', 'original audio')
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(backup_dir, filename)
            
            # Find the studio_voice.py script
            script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'studio_voice.py')
            
            if not os.path.exists(script_path):
                self.log(f"Error: studio_voice.py not found at {script_path}")
                return False
            
            # Process to a temporary output file first
            temp_output = input_file + ".temp_enhanced"
            
            # Build command to process to temp file
            cmd = [
                sys.executable, script_path,  # Use sys.executable instead of 'python'
                '--input', input_file,
                '--output', temp_output,
                '--model-type', self.model_var.get()
            ]
            
            if self.streaming_var.get():
                cmd.append('--streaming')
            
            # Run the processing command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(temp_output):
                # Processing successful - now do the file management
                try:
                    # Move original file to backup location
                    if os.path.exists(backup_file):
                        # If backup already exists, remove it first
                        os.remove(backup_file)
                    shutil.move(input_file, backup_file)
                    
                    # Move enhanced file to replace original
                    shutil.move(temp_output, input_file)
                    
                    self.log(f"✅ File management complete:")
                    self.log(f"   Enhanced: {input_file}")
                    self.log(f"   Backup: {backup_file}")
                    
                    return True
                    
                except Exception as e:
                    self.log(f"Error during file management: {str(e)}")
                    # Try to restore original file if it was moved
                    try:
                        if os.path.exists(backup_file) and not os.path.exists(input_file):
                            shutil.move(backup_file, input_file)
                    except:
                        pass
                    # Clean up temp file if it exists
                    if os.path.exists(temp_output):
                        os.remove(temp_output)
                    return False
            else:
                self.log(f"Error output: {result.stderr}")
                # Clean up temp file if it exists
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                return False
                
        except subprocess.TimeoutExpired:
            self.log("Error: Processing timed out")
            return False
        except Exception as e:
            self.log(f"Error running processing: {str(e)}")
            return False

def main():
    root = tk.Tk()
    app = StudioVoiceDesktopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
