# NVIDIA Studio Voice NIM Client

This package has a sample client which demonstrates interaction with a Studio Voice NIM.

## Getting Started

NVIDIA Maxine NIM Client packages use gRPC APIs. Instructions below demonstrate usage of Studio Voice NIM using Python gRPC client.
Additionally, access the [Try API](https://build.nvidia.com/nvidia/studiovoice/api) feature to experience the NVIDIA Studio Voice NIM API without hosting your own servers, as it leverages the NVIDIA Cloud Functions backend.

## Pre-requisites

- Ensure you have Python 3.10 or above installed on your system.
Please refer to the [Python documentation](https://www.python.org/downloads/) for download and installation instructions.
- Access to NVIDIA Studio Voice NIM Container / Service.

## Usage guide

### 1. Clone the repository

```bash
git clone https://github.com/nvidia-maxine/nim-clients.git

// Go to the 'studio-voice' folder
cd nim-clients/studio-voice
```

### 2. Install Dependencies

#### Create Virtual Environment

Create a virtual environment named `nim` for dependency isolation:

**On Linux/macOS:**
```bash
python3 -m venv nim
source nim/bin/activate
pip install -r requirements.txt
```

**On Windows:**
```bash
python -m venv nim
nim\Scripts\activate.bat
pip install -r requirements.txt
```

#### Alternative Installation (without virtual environment)

If you prefer to install dependencies globally:

**On Linux:**
```bash
sudo apt-get install python3-pip
pip install -r requirements.txt
```

**On Windows:**
```bash
pip install -r requirements.txt
```

**Note:** The virtual environment approach is recommended, especially when using the interactive UI interfaces, as they rely on the `nim` virtual environment for dependency management and automatic installation features.

### 3. Host the NIM Server

Before running client part of Studio Voice, please set up a server.
The simplest way to do that is to follow the [quick start guide](https://docs.nvidia.com/nim/maxine/studio-voice/latest/index.html).
This step can be skipped when using [Try API](https://build.nvidia.com/nvidia/studiovoice/api).

podman run -it --name=studio-voice \
    --device nvidia.com/gpu=all \
    --shm-size=8GB \
    -e NGC_API_KEY=$NGC_API_KEY \
    -e FILE_SIZE_LIMIT=36700160 \
    -e STREAMING=false \
    -p 8000:8000 \
    -p 8001:8001 \
    nvcr.io/nim/nvidia/maxine-studio-voice:latest


### 4. Compile the Protos

Before running the python client, you can choose to compile the protos.
The grpcio version needed for compilation can be referred at requirements.txt

To compile protos on Linux, run:
```bash
// Go to studio-voice/protos folder
cd studio-voice/protos

chmod +x compile_protos.sh
./compile_protos.sh
```

To compile protos on Windows, run:
```bash
// Go to studio-voice/protos folder
cd studio-voice/protos

compile_protos.bat
```

### 5. Run the Python Client

Go to the scripts directory.

```bash
cd scripts
```

#### Usage for Transactional NIM Request

To run client in transactional mode. Set `--model-type` in accordance with the server, default is set to `48k-hq`. The following example command processes the packaged sample audio file in transactional mode and generates a `studio_voice_48k_output.wav` file in the current folder.

```bash
python studio_voice.py --target 127.0.0.1:8001 --input ../assets/studio_voice_48k_input.wav --output studio_voice_48k_output.wav --model-type 48k-hq
```

#### Usage for Streaming NIM Request

To run the client in streaming mode, add `--streaming`. The following example command processes the packaged sample audio file in streaming mode and generates a `studio_voice_48k_output.wav` file in the current folder.

```bash
python studio_voice.py --target 127.0.0.1:8001 --input ../assets/studio_voice_48k_input.wav --output studio_voice_48k_output.wav --streaming --model-type 48k-ll
```

Only WAV files are supported.

#### Usage for Preview API Request

```bash
python studio_voice.py --preview-mode \
    --ssl-mode TLS \
    --target grpc.nvcf.nvidia.com:443 \
    --function-id <function_id> \
    --api-key $API_KEY_REQUIRED_IF_EXECUTING_OUTSIDE_NGC \
    --input <input_file_path> \
    --output <output_file_path> \
```

#### Command Line Arguments

- `--preview-mode`  - Flag to send request to preview NVCF server on https://build.nvidia.com/nvidia/studiovoice/api.
- `--ssl-mode`      - Flag to control if SSL MTLS/TLS encryption should be used. When running preview SSL must be set to TLS. Default value is `None`.
- `--ssl-key`       - The path to ssl private key. Default value is `None`.
- `--ssl-cert`      - The path to ssl certificate chain. Default value is `None`.
- `--ssl-root-cert` - The path to ssl root certificate. Default value is `None`.
- `--target`        - <IP:port> of gRPC service, when hosted locally. Use grpc.nvcf.nvidia.com:443 when hosted on NVCF.
- `--api-key`       - NGC API key required for authentication, utilized when using `TRY API` ignored otherwise.
- `--function-id`   - NVCF function ID for the service, utilized when using `TRY API` ignored otherwise.
- `--input`         - The path to the input audio file. Default value is `../assets/studio_voice_48k_input.wav`.
- `--output`        - The path for the output audio file. Default is current directory (scripts) with name `studio_voice_48k_output.wav`.
- `--streaming`     - Flag to control if streaming mode should be used. Transactional mode will be used by default.
- `--model-type`    - Studio Voice model type hosted on server. It can be set to `48k-hq/48k-ll/16k-hq`. Default value is `48k-hq`.

Refer the [docs](https://docs.nvidia.com/nim/maxine/studio-voice/latest/index.html) for more information.

## Interactive User Interfaces

This package includes several interactive user interfaces to simplify bulk audio processing workflows. These UIs provide an intuitive way to process multiple audio files with progress tracking and automatic file management.

### Web-Based Interface

Launch a web interface for Studio Voice processing through your browser:

```bash
# Simple web UI (recommended for stability)
start_simple_web_ui.bat

# Advanced web UI (with real-time updates)
start_advanced_web_ui.bat
```

**Features:**
- Upload individual files or scan entire folder structures
- Real-time progress tracking with queue management
- Support for all Studio Voice model types (48k-hq, 48k-ll, 16k-hq)
- Automatic file backup and replacement workflow
- Browser-based interface accessible at http://localhost:5000

### Desktop Application

Launch a native Windows desktop application:

# Standalone version with built-in dependency management
start_desktop_ui_standalone.bat
```

**Features:**
- Native Windows GUI using tkinter
- Folder browsing and batch file selection
- Automatic dependency checking and installation
- In-place file processing with backup management
- Progress tracking with detailed status updates
- Support for all Studio Voice model configurations
- **Large file handling**: Automatically splits files over 35MB into chunks, processes them separately, and rejoins them

### Enhanced Command Line Interface

Launch an improved CLI with rich formatting and interactive prompts:

```bash
start_enhanced_cli.bat
```

**Features:**
- Interactive model selection and configuration
- Rich progress bars and status formatting
- Folder scanning with file filtering
- Batch processing with detailed logging
- Color-coded output and error handling

### File Management Workflow

All UI interfaces follow a consistent file management approach:

1. **Original files** are automatically backed up to `../original audio/` relative to the source location
2. **Processed files** replace the original files in their current location
3. **Folder structure** is preserved during batch operations
4. **File naming** remains unchanged to maintain existing workflows

### Dependency Management

The UI launchers include automatic dependency checking and installation:

- **Virtual environment** activation (uses existing `nim/` environment)
- **Requirements installation** from `requirements.txt`
- **Missing module detection** with automatic resolution
- **Error handling** with clear troubleshooting guidance

### Troubleshooting UI Issues

If you encounter dependency errors:

1. Run the dependency checker:
   ```bash
   cd desktop-ui
   python check_dependencies.py
   ```

2. Manually install missing packages:
   ```bash
   nim\Scripts\activate.bat
   pip install grpcio grpcio-tools protobuf flask
   ```

3. Use the standalone versions which include built-in dependency management

#### Zero-Byte Output Files

If the desktop application reports "successful processing" but produces zero-byte files:

1. **Check if the NIM server is running:**
   ```bash
   studio_voice_server.bat --status
   ```
   The server should show as "Up" and listening on ports 8000-8001.

2. **Start the server if not running:**
   ```bash
   studio_voice_server.bat
   ```

3. **Test the connection manually:**
   ```bash
   cd scripts
   nim\Scripts\activate.bat
   python studio_voice.py --input ../assets/studio_voice_48k_input.wav --output test.wav
   ```

4. **Check the desktop UI logs** for detailed error messages that now include:
   - Server connection issues
   - Empty output file detection
   - Detailed subprocess output

**Note:** The desktop UI has been improved to detect and report zero-byte output files with specific error messages to help diagnose server connectivity issues.

#### Large File Processing

The desktop and web UIs now automatically handle audio files larger than the server's 35MB limit:

1. **Automatic Detection**: Files exceeding the size limit are automatically detected
2. **Smart Chunking**: Large files are split into optimal chunks (typically 2-3 minutes each)
3. **Sequential Processing**: Each chunk is processed individually through the NIM server
4. **Seamless Rejoining**: Processed chunks are automatically merged back into a single file
5. **Progress Tracking**: Shows progress for both chunking and individual chunk processing

**Example**: A 45MB, 4-minute audio file would be split into two ~27MB and ~18MB chunks, processed separately, then rejoined into a single enhanced file.

This allows processing of audio files of virtually any size while respecting server limitations.

### UI Configuration

All interfaces support the same Studio Voice configuration options:

- **Model Types**: 48k-hq (default), 48k-ll, 16k-hq
- **Server Target**: 127.0.0.1:8001 (configurable)
- **Processing Modes**: Transactional and streaming
- **File Formats**: WAV files (same as command line client)

The UI system maintains full compatibility with the existing Studio Voice NIM server setup and does not require additional server-side configuration.

## Testing

The project includes a comprehensive test suite organized in the `tests/` directory:

```
tests/
├── core/                    # Core functionality tests
│   └── test_desktop_ui_fix.py
├── desktop-ui/              # Desktop UI specific tests
│   ├── test_chunking.py
│   ├── test_end_to_end.py
│   ├── test_large_file_handler.py
│   ├── test_processing_fix.py
│   └── test_temp_file_fix.py
├── scripts/                 # Batch script tests
│   ├── test_loop.bat
│   ├── test_podman.bat
│   └── test_server.bat
└── __init__.py
```

### Running Tests

To run all tests, use the provided test runner from the project root:

```bash
# Activate virtual environment first
nim\Scripts\activate.bat

# Run all tests
python run_tests.py
```

### Individual Test Categories

- **Core Tests**: Basic audio processing and server communication
- **Desktop UI Tests**: GUI functionality, large file handling, and chunking system
- **Script Tests**: Batch file functionality for server management

The test suite validates:
- Zero-byte file detection and prevention
- Large file chunking and merging (35MB+ files)
- End-to-end processing workflows
- Error handling and user feedback
- Server connectivity and status checks

## Project Structure

```
studio-voice/
├── assets/                  # Sample audio files
├── desktop-ui/              # Desktop GUI applications
├── enhanced-cli/            # Enhanced command-line interface
├── interfaces/              # Generated gRPC interfaces
├── protos/                  # Protocol buffer definitions
├── scripts/                 # Core processing scripts
├── tests/                   # Organized test suite
├── web-ui/                  # Web-based interfaces
├── README.md               # This file
├── run_tests.py            # Test runner script
└── *.bat                   # Startup and utility scripts
```