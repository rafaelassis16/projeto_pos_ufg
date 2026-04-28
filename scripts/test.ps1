# scripts/test.ps1
Write-Host "Executando testes com cobertura..." -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    Write-Host "Ambiente virtual não encontrado. Execute 'make install' primeiro." -ForegroundColor Red
    exit 1
}

& .venv\Scripts\python -m pytest --cov=app --cov-report=term-missing --cov-report=html:app/tests/results/htmlcov
