$ErrorActionPreference = "Stop"

if (-not (Test-Path "allure-results")) {
    throw "Сначала запустите .\run-tests.ps1, чтобы создать allure-results."
}

if (Get-Command allure -ErrorAction SilentlyContinue) {
    allure generate allure-results --clean -o allure-report
    exit $LASTEXITCODE
}

if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    throw "Для сборки отчёта нужен установленный Allure CLI или pnpm: https://allurereport.org/docs/install/"
}

pnpm dlx allure-commandline@2.29.0 generate allure-results --clean -o allure-report
exit $LASTEXITCODE
