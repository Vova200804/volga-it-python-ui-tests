@echo off
pushd "%~dp0" || exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0make-allure-report.ps1" %*
set "REPORT_EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %REPORT_EXIT_CODE%
