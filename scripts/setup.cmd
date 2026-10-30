@echo off
chcp 65001 >nul
rem First install: Python environment and packages for voice recognition.
rem Only Latin text in this file: cmd misreads multibyte lines after chcp 65001.
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv || goto :error
)
.venv\Scripts\python.exe -m pip install --disable-pip-version-check -q -r requirements.txt || goto :error
echo.
echo Done. Start the bot: scripts\agent.cmd
exit /b 0
:error
echo Setup failed.
exit /b 1
