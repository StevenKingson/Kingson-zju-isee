@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" "scripts\upload-github.py" %*
) else (
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 "scripts\upload-github.py" %*
  ) else (
    where python >nul 2>nul
    if errorlevel 1 (
      echo 没有找到 Python。请打开“网站操作指南.html”，查看故障处理。
      pause
      exit /b 1
    )
    python "scripts\upload-github.py" %*
  )
)
set "UPLOAD_RESULT=%ERRORLEVEL%"
echo.
if not "%UPLOAD_RESULT%"=="0" echo 上传没有完成，请查看上方提示。文件和已有提交均保留。
echo 按任意键关闭此窗口。
pause >nul
exit /b %UPLOAD_RESULT%
