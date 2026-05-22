# Windows setup helper for Potens RAG project
# Usage: .\scripts\run_setup.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "Creating virtual environment..."
python -m venv .venv

Write-Host "Activating venv..."
.\.venv\Scripts\Activate.ps1

$pip = "python -m pip"
& python -m pip install --upgrade pip -q

Write-Host ""
Write-Host "Installing dependencies (3 steps — large wheels can take 10-20 min on Windows)..."
Write-Host ""

Write-Host "[1/3] PyTorch CPU (~120 MB download + extract). This step has no per-package progress bar."
& python -m pip install "torch>=2.2.0,<2.13" --index-url https://download.pytorch.org/whl/cpu
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "[2/3] Vector DB + embedding models (ChromaDB, sentence-transformers)..."
& python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "[3/3] Verifying imports..."
& python -c "import torch; import chromadb; import sentence_transformers; print('Dependencies OK:', torch.__version__, chromadb.__version__)"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

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
