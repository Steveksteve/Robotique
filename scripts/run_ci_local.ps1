Param()

$ErrorActionPreference = 'Stop'
$composeFile = "docker-compose.test.yml"

Write-Host "Building & starting services..."
docker compose -f $composeFile up --build -d

Write-Host "Waiting for API at http://localhost:8000/ ..."
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri http://localhost:8000/ -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { Write-Host "API available"; break }
    } catch { }
    Start-Sleep -Seconds 1
}

Write-Host "Installing test deps (if needed)..."
python -m pip install --upgrade pip
python -m pip install -r tests/integration/requirements-test.txt

Write-Host "Running integration tests..."
if (-not (Test-Path -Path reports)) { New-Item -ItemType Directory -Path reports | Out-Null }
python -m pytest tests/integration/ -q --junitxml=reports/junit.xml
$exit = $LASTEXITCODE

Write-Host "Tearing down..."
docker compose -f $composeFile down -v

exit $exit
