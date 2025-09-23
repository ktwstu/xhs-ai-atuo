@echo off
TITLE XHS Auto Project Launcher

:: Change to the script's directory to ensure paths are correct
cd /d "%~dp0"

ECHO Starting MCP in a new window...
start "MCP" cmd /k "cd E:\DevSouce\ccrcode\xhs-auto\xiaohongshu-mcp && go run . -headless=false"

ECHO Starting Python environment in a second window...
start "XHS Auto" cmd /k "call venv\Scripts\activate.bat && echo. && echo ================================================================== && echo  Virtual environment activated successfully. && echo. && echo  To start the application, run the following command: && echo. && echo    python xhs-ai-auto/main.py && echo ================================================================== && echo."