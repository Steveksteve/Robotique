$ErrorActionPreference = "Stop"

$ComposeFile = "docker-compose.test.yml"
$ApiBase = if ($env:API_BASE) { $env:API_BASE } else { "http://localhost:8000" }
$WsUrl = if ($env:WS_URL) { $env:WS_URL } else { "ws://localhost:8765" }
$WebBase = if ($env:WEB_BASE) { $env:WEB_BASE } else { "http://localhost:8080" }

function Cleanup {
    docker compose -f $ComposeFile down -v | Out-Null
}

try {
    docker compose -f $ComposeFile up --build -d

    $apiReady = $false
    for ($i = 1; $i -le 90; $i++) {
        try {
            Invoke-WebRequest -Uri "$ApiBase/health" -UseBasicParsing | Out-Null
            $apiReady = $true
            Write-Host "API ready"
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $apiReady) {
        docker compose -f $ComposeFile logs api
        throw "API not ready"
    }

    $webReady = $false
    for ($i = 1; $i -le 90; $i++) {
        try {
            Invoke-WebRequest -Uri "$WebBase/" -UseBasicParsing | Out-Null
            $webReady = $true
            Write-Host "Web ready"
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $webReady) {
        docker compose -f $ComposeFile logs web
        throw "Web not ready"
    }

    python -m pip install -r tests/integration/requirements-test.txt
    New-Item -ItemType Directory -Force -Path reports | Out-Null
    python -m pytest tests/unit/iot -q --junitxml=reports/junit-unit.xml
    $env:API_BASE = $ApiBase
    $env:WS_URL = $WsUrl
    $env:WEB_BASE = $WebBase
    python -m pytest tests/integration/ -q --junitxml=reports/junit.xml
}
finally {
    Cleanup
}
