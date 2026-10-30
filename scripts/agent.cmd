@echo off
chcp 65001 >nul
rem Telegram bot: Claude Code session in agent\ with the Telegram channel. Keep the window open.
rem The Telegram server comes from agent\.mcp.json, not from the plugin: Claude Code 2.1.310 does not
rem start the plugin's server with --channels. Hence the development channel flag (confirm at startup).
rem Only Latin text in this file: cmd misreads multibyte lines after chcp 65001.
cd /d "%~dp0..\agent"
set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.bun\bin;%PATH%"
if not exist "%USERPROFILE%\.claude\plugins\cache\claude-plugins-official\telegram\0.0.7\server.ts" (
  echo Telegram plugin 0.0.7 not found - fix the version in agent\.mcp.json and this file.
  exit /b 1
)
claude --dangerously-load-development-channels server:telegram --permission-mode dontAsk %*
