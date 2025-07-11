# Studio Voice - Enhanced User Interfaces

This directory contains modern user interface options for the Studio Voice NIM client, making audio enhancement more interactive and user-friendly.

## Available UIs

### 🌐 Web Dashboard (`web-ui/`)
A modern, responsive web interface with real-time progress tracking and drag-and-drop file upload.

**Features:**
- 📁 Drag & drop file upload or folder selection
- 📊 Real-time progress tracking with visual progress bars
- 🎵 Audio preview and comparison (planned)
- 📋 Queue management (pause, resume, reorder)
- ⚙️ Settings panel for model selection and parameters
- 📈 Processing history and statistics
- 🔄 WebSocket-based real-time updates
- 📱 Responsive design for mobile and desktop

**Quick Start:**
```bash
# Start the web interface
start_web_ui.bat

# Open browser to http://127.0.0.1:5000
```

### 🖥️ Desktop Application (`desktop-ui/`)
A native desktop GUI using tkinter for integrated Windows experience.

**Features:**
- 🗂️ Native file browser integration
- 📊 Visual progress tracking
- 📝 Real-time processing log
- ⚙️ Easy settings configuration
- 🎵 Support for batch and individual file processing
- 📁 Folder scanning for audio files

**Quick Start:**
```bash
# Start the desktop application
start_desktop_ui.bat
```

### 💻 Enhanced Command Line
Improved CLI with better interactivity and visual feedback.

**Features:**
- 🌈 Color-coded output
- 📊 Interactive progress bars
- ⚙️ Interactive prompts for settings
- 📈 Real-time status updates

## Installation & Setup

### Prerequisites
- Python 3.10 or above
- NVIDIA Studio Voice NIM server running
- Virtual environment (recommended)

### Setup Instructions

1. **Ensure your virtual environment is set up:**
   ```bash
   python -m venv nim
   nim\Scripts\activate.bat
   pip install -r requirements.txt
   ```

2. **For Web UI - Install additional dependencies:**
   ```bash
   cd web-ui
   pip install -r requirements.txt
   ```

3. **Start your preferred interface:**
   - Web UI: `start_web_ui.bat`
   - Desktop UI: `start_desktop_ui.bat`

## Configuration

### Server Settings
All UIs connect to the Studio Voice NIM server. Default settings:
- **Server:** `127.0.0.1:8001`
- **Model Types:** 48k-hq, 48k-ll, 16k-hq
- **Supported Formats:** WAV, MP3, FLAC, M4A

### Customizing Settings
You can modify default settings in each UI:

**Web UI:** Edit `web-ui/app.py` configuration section
**Desktop UI:** Settings are saved per session in the GUI

## Usage Examples

### Batch Processing with Web UI
1. Open http://127.0.0.1:5000
2. Drag audio files or folders to the upload area
3. Select model type and processing mode
4. Click "Start Processing"
5. Monitor progress in real-time
6. Download enhanced files when complete

### Desktop Processing
1. Run `start_desktop_ui.bat`
2. Click "Select Files" or "Select Folder"
3. Configure processing settings
4. Click "Start Processing"
5. Monitor progress and log output
6. Find enhanced files in the output directory

## File Management

Both UIs follow the same file management approach as your existing batch script:

- **Enhanced files:** Replace originals in the same location
- **Original files:** Moved to `../original audio/` folders
- **Directory structure:** Preserved exactly

Example:
```
Before: D:\Media\MyProject\Audio\audio.wav
After:  D:\Media\MyProject\Audio\audio.wav (enhanced)
        D:\Media\MyProject\original audio\audio.wav (original)
```

## Architecture

### Web UI Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask Server   │    │  Studio Voice   │
│   (HTML/JS)     │◄──►│   (Python)       │◄──►│   NIM Server    │
│                 │    │                  │    │   (gRPC)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        ▲                        ▲
        │                        │
        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐
│   WebSockets    │    │  Job Queue       │
│   (Real-time)   │    │  (Background)    │
└─────────────────┘    └──────────────────┘
```

### Desktop UI Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Tkinter GUI   │    │   Subprocess     │    │  Studio Voice   │
│   (Python)      │◄──►│   (Python)       │◄──►│   Script        │
│                 │    │                  │    │   (Direct)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Advanced Usage

### Custom Model Types
Add custom model types by modifying the model selection lists in:
- Web UI: `templates/index.html` and `app.py`
- Desktop UI: `studio_voice_gui.py`

### Integration with Existing Scripts
Both UIs can work alongside your existing batch processing scripts:
- Use the UI for interactive processing
- Use batch scripts for automated workflows
- Share the same virtual environment and dependencies

### API Extensions
The Web UI provides REST endpoints for integration:
- `POST /api/upload` - Upload files
- `GET /api/jobs` - Get job status
- `POST /api/jobs/{id}/cancel` - Cancel jobs
- `GET /api/download/{id}` - Download results

## Troubleshooting

### Common Issues

**Web UI won't start:**
- Check if port 5000 is available
- Ensure Flask dependencies are installed: `pip install -r web-ui/requirements.txt`

**Desktop UI displays incorrectly:**
- Ensure you have a full Python installation with tkinter
- Try running: `python -c "import tkinter; tkinter.Tk()"`

**Processing fails:**
- Verify Studio Voice NIM server is running
- Check server address in settings (default: 127.0.0.1:8001)
- Ensure audio files are in supported formats

**File permissions:**
- Ensure write permissions to output directories
- Check that original files aren't locked by other applications

### Performance Tips

- Use 16k-hq model for faster processing of speech
- Use 48k-ll for low-latency requirements
- Enable streaming mode for real-time applications
- Process smaller batches for better responsiveness

## Contributing

To add new features or modify the UIs:

1. **Web UI:** Modify Flask routes in `app.py` and frontend in `templates/index.html`
2. **Desktop UI:** Update the tkinter interface in `studio_voice_gui.py`
3. **Common:** Update batch scripts for new functionality

## Support

For issues specific to the UI:
1. Check the console/log output for detailed error messages
2. Verify your Studio Voice NIM server is accessible
3. Ensure all dependencies are properly installed

For Studio Voice NIM issues, refer to the main project documentation.
