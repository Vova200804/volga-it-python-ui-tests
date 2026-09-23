param(
    [string]$Marker = "",
    [switch]$Headed
)

$ErrorActionPreference = "Stop"

if (Test-Path ".venv/Scripts/python.exe") {
    $venvVersion = (& ./.venv/Scripts/python.exe --version 2>&1 | Out-String).Trim()
    if ($venvVersion -notmatch 'Python (3\.(1[2-9]|[2-9][0-9])|[4-9][0-9])\.') {
        throw "Существующее .venv несовместимо с заданием ($venvVersion). Удалите .venv и повторите запуск с Python 3.12+."
    }
}

if (-not (Test-Path ".venv/Scripts/python.exe")) {
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
    & $pythonCommand @pythonPrefix -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Не удалось создать виртуальное окружение Python 3.12+." }
    & ./.venv/Scripts/python.exe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Не удалось установить зависимости из requirements.txt." }
}

if ($Headed) { $env:HEADLESS = "0" }
$pytestArgs = @("-m", "pytest", "-v", "--alluredir", "allure-results", "--clean-alluredir")
if ($Marker) { $pytestArgs += @("-m", $Marker) }
& ./.venv/Scripts/python.exe @pytestArgs
exit $LASTEXITCODE
