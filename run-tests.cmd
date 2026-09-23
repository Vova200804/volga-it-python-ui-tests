@echo off
pushd "%~dp0" || exit /b 1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-tests.ps1" %*
set "TEST_EXIT_CODE=%ERRORLEVEL%"
popd
exit /b %TEST_EXIT_CODE%
