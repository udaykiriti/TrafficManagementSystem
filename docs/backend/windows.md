# Comprehensive Windows Backend Setup Guide

This guide provides a detailed, step-by-step walkthrough for setting up and running the AI Traffic Management System backend on a Windows machine without Docker.

> [!NOTE]
> This guide assumes you are running Windows 10 or Windows 11. All commands should be executed in PowerShell unless otherwise specified.

---

## 1. Prerequisites & Environment Setup

### 1.1 Python Installation

Python is required to run the Flask backend and AI inference scripts.

1. **Download Python:** Navigate to [python.org](https://www.python.org/downloads/windows/) and download the latest Python 3.10 (or newer) 64-bit Windows installer.
2. **Run Installer:** Execute the downloaded installer.
3. **Critical Step:** At the very bottom of the first installation screen, you must check the box that says **"Add Python to PATH"** before clicking "Install Now". 

> [!WARNING]
> If you forget to check the "Add Python to PATH" box, the `python` and `pip` commands will not be recognized in your terminal. You will need to rerun the installer and choose "Modify" to enable it.

4. **Verify Installation:** Open a new PowerShell window and run the following command to verify Python is installed correctly:
   ```powershell
   python --version
   ```
   You should see a version number like `Python 3.10.x`.

### 1.2 C++ Build Tools (MinGW-w64)

The optimization engine (Genetic Algorithm) is written in C++ for performance and requires a compiler with C++17 support and OpenMP.

1. **Download MSYS2:** Go to [msys2.org](https://www.msys2.org/) and download the installer.
2. **Install MSYS2:** Run the installer and follow the standard installation prompts (the default installation directory `C:\msys64` is recommended).
3. **Install GCC/G++:** Open the **"MSYS2 MSYS"** application from your Start Menu and run the following command to download and install the Mingw-w64 GCC package:
   ```bash
   pacman -S mingw-w64-x86_64-gcc
   ```
   Press `Y` when prompted to proceed with the installation.
4. **Update Environment Variables:**
   - Press the Windows Key and type "Environment Variables", then select **"Edit the system environment variables"**.
   - Click the **"Environment Variables..."** button at the bottom.
   - Under "System variables" (or "User variables"), find the **Path** variable, select it, and click **Edit**.
   - Click **New** and add the path to the MinGW binaries, which is typically `C:\msys64\mingw64\bin`.
   - Click **OK** on all windows to save the changes.
5. **Verify Installation:** Open a new PowerShell window and type:
   ```powershell
   g++ --version
   ```
   This should output the GCC/G++ version information.

> [!TIP]
> If PowerShell still says "g++ is not recognized", ensure you have completely closed and reopened PowerShell after changing the environment variables.

---

## 2. Project Installation Steps

### 2.1 Clone Repository

You need to clone the project to your local machine using Git.

> [!NOTE]
> Ensure you have [Git for Windows](https://gitforwindows.org/) installed before running this step.

```powershell
# Navigate to the folder where you want to store the project
cd C:\Path\To\Your\Workspace

# Clone the repository
git clone https://github.com/2200031066/TrafficManagementSystem
cd TrafficManagementSystem
```

### 2.2 Create a Virtual Environment (Recommended)

Using a virtual environment prevents dependency conflicts with other Python projects on your machine.

```powershell
# Create the virtual environment inside the project root
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```

> [!WARNING]
> If you receive an "Execution of scripts is disabled on this system" error when trying to activate the virtual environment, run this command in PowerShell as Administrator:
> `Set-ExecutionPolicy Unrestricted -Scope CurrentUser`, then try activating again.

### 2.3 Install Python Dependencies

With your virtual environment activated, install the required Python packages.

```powershell
# Execute from the project root
pip install -r backend/requirements.txt
```

### 2.4 Download YOLO Model Files

The computer vision component utilizes the YOLO (You Only Look Once) architecture and requires pre-trained weight and configuration files.

> [!IMPORTANT]
> The weights files are large (up to 250MB). Depending on your internet connection, the `Invoke-WebRequest` command might take several minutes to complete. Please be patient and do not close the window.

Execute the following commands in PowerShell (from the project root) to download the standard YOLOv4 files into the `backend/` directory:

```powershell
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4.weights' -OutFile 'backend/yolov4.weights'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg' -OutFile 'backend/yolov4.cfg'"
```

**Optional: YOLOv4-tiny (Optimized for Speed/Low Specs):**
If you are running on less powerful hardware, you can download the "tiny" versions, which perform inference much faster but with slightly lower accuracy.

```powershell
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights' -OutFile 'backend/yolov4-tiny.weights'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg' -OutFile 'backend/yolov4-tiny.cfg'"
```

### 2.5 Compile the Genetic Algorithm Core

The optimization engine must be compiled into a binary executable named `Algo1`.

```powershell
# Execute from the project root
g++ -std=c++17 -O3 -fopenmp -o backend/Algo1 backend/Algo.cpp
```

> [!NOTE]
> - `-std=c++17` forces the use of the C++17 standard.
> - `-O3` applies maximum performance optimizations.
> - `-fopenmp` enables multi-threading support for faster execution.
>
> If your specific compiler version does not support OpenMP, you can safely omit the `-fopenmp` flag.

---

## 3. Configuration Verification

Before attempting to start the server, verify your system structure. To check that all required files exist, you can use the `dir` command or simply check your File Explorer.

Ensure the following files are present directly inside your `backend/` folder:
- `Algo1.exe` (The compiled C++ binary, on Windows it often automatically appends `.exe`)
- `yolov4.weights`
- `yolov4.cfg`
- `yolov4-tiny.weights` (if downloaded)
- `yolov4-tiny.cfg` (if downloaded)

---

## 4. Running the Backend Server

You are now ready to launch the Flask REST API server.

> [!TIP]
> Ensure your virtual environment is activated before starting the server. You should see `(venv)` at the beginning of your PowerShell prompt.

Launch the Flask server from the root directory:
```powershell
python backend/app.py
```

### Accessing the API

Once the server indicates it is "Running on http://127.0.0.1:5000", you can access the API.

- **Base API URL:** `http://localhost:5000`
- **Health Check Endpoint:** `http://localhost:5000/health`

**Verifying Health Status:**
Open your web browser or use a tool like Postman to visit the Health Check Endpoint. A fully healthy setup will return a JSON response similar to this:

```json
{
  "components": {
    "api": "ok",
    "ga_binary": "ok",
    "yolo_config": "ok",
    "yolo_weights": "ok"
  },
  "status": "healthy",
  "timestamp": "2023-10-27T10:00:00Z"
}
```

> [!WARNING]
> If any component inside the `"components"` block returns `"missing"`, the system will not function correctly. Double check the file paths in the `backend/` directory if you see a missing component.

---

## 5. Troubleshooting Common Issues

| Issue | Potential Cause | Solution |
| :--- | :--- | :--- |
| **"g++" or "python" is not recognized as an internal or external command** | Missing Environment Variable PATH | Add your MinGW/MSYS2 `bin` folder and/or Python installation folder to the Windows System PATH. Close and reopen PowerShell. |
| **Execution of scripts is disabled on this system** | PowerShell Execution Policy | Run PowerShell as Administrator and execute `Set-ExecutionPolicy Unrestricted -Scope CurrentUser`. |
| **503 Service Unavailable / Component Missing** | Missing compiled binary or weights | Check the `/health` endpoint to see which component is missing. Re-run the compile step or the download step for the missing file, ensuring you are in the project root directory. |
| **Permission Denied during pip install or file download** | Lack of administrative rights | Run your PowerShell terminal as Administrator and attempt the command again. |
| **ImportError: No module named 'flask' (or others)** | Virtual Environment not active | Ensure you have activated your virtual environment, and that you ran `pip install -r backend/requirements.txt` while it was active. |
