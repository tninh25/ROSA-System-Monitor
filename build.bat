@echo off
title 🚀 Build main.py with Nuitka (PyQt5)
echo ==============================================
echo 🔧 Đang build main.py -> main.exe ...
echo ==============================================
echo.

REM --- Cấu hình ---
set SRC_FILE=main.py
set ICON_FILE=rosa-monitor.ico
set OUTPUT_NAME=main.exe

REM --- Kiểm tra file nguồn ---
if not exist "%SRC_FILE%" (
    echo ❌ Không tìm thấy %SRC_FILE%
    pause
    exit /b
)

REM --- Kiểm tra icon ---
if not exist "%ICON_FILE%" (
    echo ⚠️  Không tìm thấy %ICON_FILE% (sẽ build không icon)
    set ICON_FLAG=
) else (
    set ICON_FLAG=--windows-icon-from-ico=%ICON_FILE%
)

REM --- Build ---
nuitka ^
  %SRC_FILE% ^
  --onefile ^
  --enable-plugin=pyqt5 ^
  --follow-imports ^
  --include-data-dir=assets=assets ^
  %ICON_FLAG% ^
  --windows-disable-console ^
  --output-filename=%OUTPUT_NAME%

echo.
echo ✅ Build hoàn tất: %OUTPUT_NAME%
echo.
pause
