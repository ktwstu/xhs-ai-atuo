try {
    # Activate the virtual environment using a relative path
    . ".\\venv\\Scripts\\Activate.ps1"

    # Clear the screen and show instructions
    Clear-Host
    Write-Host "==================================================================" -ForegroundColor Green
    Write-Host " Virtual environment activated successfully." -ForegroundColor Green
    Write-Host ""
    Write-Host " To start the application, run the following command:"
    Write-Host ""
    Write-Host "   python xhs-ai-auto/main.py" -ForegroundColor Yellow
    Write-Host "==================================================================" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host "AN ERROR OCCURRED:" -ForegroundColor Red
    Write-Host $_
    Read-Host "Press ENTER to exit"
}
