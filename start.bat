@echo off
TITLE XHS Auto Project Console

:: Change to the script's directory to ensure paths are correct
cd /d "%~dp0"

:: Execute the PowerShell script, keeping the window open after it finishes
powershell.exe -ExecutionPolicy Bypass -NoExit -File ".\\start.ps1"
