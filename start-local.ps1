Set-Location $PSScriptRoot

if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "venv がありません。作成します..."
    python -m venv venv
}

Write-Host "Python キャッシュをクリア..."
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "依存関係をインストール..."
& ".\venv\Scripts\python.exe" -m pip install -r requirements.txt -q

Write-Host "Streamlit を起動します: http://localhost:8501"
& ".\venv\Scripts\python.exe" -m streamlit run app.py
