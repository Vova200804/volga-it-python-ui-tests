param(
    [string]$Marker = "",
    [switch]$Headed
)

$ErrorActionPreference = "Stop"
$startedAt = Get-Date
Write-Host "[1/3] Checking Python environment..."

if (Test-Path ".venv/Scripts/python.exe") {
    $venvVersion = (& ./.venv/Scripts/python.exe --version 2>&1 | Out-String).Trim()
    if ($venvVersion -notmatch 'Python (3\.(1[2-9]|[2-9][0-9])|[4-9][0-9])\.') {
        throw "Существующее .venv несовместимо с заданием ($venvVersion). Удалите .venv и повторите запуск с Python 3.12+."
    }
}

$createdVenv = -not (Test-Path ".venv/Scripts/python.exe")
if ($createdVenv) {
    $pythonCommand = $null
    $pythonPrefix = @()
    foreach ($minor in 30..12) {
        $localPython = Join-Path $env:LOCALAPPDATA "Programs/Python/Python3$minor/python.exe"
        if (Test-Path $localPython) {
            $pythonCommand = $localPython
            break
        }
    }
    if (-not $pythonCommand -and (Get-Command py -ErrorAction SilentlyContinue)) {
        foreach ($minor in 30..12) {
            $tag = "-3.$minor"
            $candidate = (& py $tag --version 2>&1 | Out-String).Trim()
            if ($LASTEXITCODE -eq 0 -and $candidate -match "Python 3\.$minor\.") {
                $pythonCommand = "py"
                $pythonPrefix = @($tag)
                break
            }
        }
    }
    if (-not $pythonCommand) {
        $pathPython = Get-Command python -ErrorAction SilentlyContinue
        if ($pathPython) {
            $candidate = (& $pathPython.Source --version 2>&1 | Out-String).Trim()
            if ($candidate -match 'Python (3\.(1[2-9]|[2-9][0-9])|[4-9][0-9])\.') {
                $pythonCommand = $pathPython.Source
            }
        }
    }
    if (-not $pythonCommand) {
        throw "Нужен установленный Python 3.12 или новее."
    }
    Write-Host "[2/3] Creating .venv with $pythonCommand. This can take several minutes on the first run..."
    & $pythonCommand @pythonPrefix -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Не удалось создать виртуальное окружение Python 3.12+." }
}

$requirementsHash = (Get-FileHash -Algorithm SHA256 requirements.txt).Hash
$stampPath = ".venv/.requirements.sha256"
$installedHash = if (Test-Path $stampPath) { (Get-Content $stampPath -Raw).Trim() } else { "" }
if ($createdVenv -or $installedHash -ne $requirementsHash) {
    Write-Host "[2/3] Installing or repairing dependencies..."
    & ./.venv/Scripts/python.exe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Не удалось установить зависимости из requirements.txt." }
    Set-Content -Path $stampPath -Value $requirementsHash
} else {
    Write-Host "[2/3] Using installed dependencies."
}

if ($Headed) { $env:HEADLESS = "0" }
if (-not $Headed) { $env:HEADLESS = "1" }
$pythonVersion = (& ./.venv/Scripts/python.exe --version 2>&1 | Out-String).Trim()
Write-Host "[3/3] Running tests with $pythonVersion. Chrome: $(if ($Headed) { 'visible' } else { 'background' })."
Write-Host "The first browser start may download a matching driver. The slowest tests will be listed at the end."
$pytestArgs = @("-m", "pytest", "-v", "--durations=10", "--alluredir", "allure-results", "--clean-alluredir")
if ($Marker) { $pytestArgs += @("-m", $Marker) }
& ./.venv/Scripts/python.exe @pytestArgs
$testExitCode = $LASTEXITCODE
$elapsed = (Get-Date) - $startedAt
Write-Host ("Run finished in {0:mm\:ss}. Exit code: {1}" -f $elapsed, $testExitCode)
exit $testExitCode
