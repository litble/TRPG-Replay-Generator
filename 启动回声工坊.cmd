@echo off
rem RplGen Studio launcher - runs gui.py with the local .venv
setlocal
cd /d "%~dp0"

rem make sure the app can find ffmpeg (see "????.md")
set "PATH=D:\tools\ffmpeg\bin;%PATH%"

if not exist ".venv\Scripts\python.exe" goto novenv

".venv\Scripts\python.exe" gui.py
if errorlevel 1 pause
goto end

:novenv
echo [ERROR] .venv not found in this folder.
echo Please create it first - see the setup notes.
pause

:end
endlocal
