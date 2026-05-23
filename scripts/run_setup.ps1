# Windows setup helper for Potens RAG project
# Usage: .\scripts\run_setup.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "Creating virtual environment..."
python -m venv .venv

Write-Host "Activating venv..."
.\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies (first run may take several minutes)..."
python -m pip install --upgrade pip -q
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env — add your GEMINI_API_KEY before running the API."
}

Write-Host "Generating sample PDFs..."
python scripts/generate_sample_documents.py

Write-Host ""
Write-Host "Setup complete. Next steps:"
Write-Host "  1. Edit .env and set GEMINI_API_KEY"
Write-Host "  2. python main.py"
Write-Host "  3. streamlit run streamlit_app/app.py"
