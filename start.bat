@echo off
chcp 65001

set ENV_NAME=xiaodouobu
set PROJECT_DIR=%~dp0

echo 正在检测 Conda 路径...
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    set CONDA_PATH=%USERPROFILE%\miniconda3
) else if exist "%USERPROFILE%\Anaconda3\Scripts\activate.bat" (
    set CONDA_PATH=%USERPROFILE%\Anaconda3
) else if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" (
    set CONDA_PATH=C:\ProgramData\miniconda3
) else if exist "C:\ProgramData\Anaconda3\Scripts\activate.bat" (
    set CONDA_PATH=C:\ProgramData\Anaconda3
) else (
    echo ❌ 未找到 Miniconda/Anaconda，请手动设置 CONDA_PATH
    pause
    exit
)

echo ✅ 检测到 Conda 路径：%CONDA_PATH%
echo 正在启动小豆包...

echo 启动后端 API 服务...
start "小豆包-后端" cmd /k "%CONDA_PATH%\Scripts\activate.bat %CONDA_PATH% && conda activate %ENV_NAME% && cd /d %PROJECT_DIR% && set PYTORCH_ALLOC_CONF=expandable_segments:True && uvicorn backend.api:app --host 0.0.0.0 --port 8000"

echo 等待后端+模型加载（90秒）...
timeout /t 90 /nobreak

echo 启动前端页面...
start "小豆包-前端" cmd /k "%CONDA_PATH%\Scripts\activate.bat %CONDA_PATH% && conda activate %ENV_NAME% && cd /d %PROJECT_DIR% && python frontend/app.py"

echo 等待前端启动（15秒）...
timeout /t 15 /nobreak

if exist "%PROJECT_DIR%cloudflared.exe" (
    echo 启动公网隧道...
    start "小豆包-公网" cmd /k "cd /d %PROJECT_DIR% && cloudflared.exe tunnel --url http://localhost:7860"
    echo 公网链接请查看"小豆包-公网"窗口
) else (
    echo 未找到 cloudflared.exe，跳过公网隧道
)

echo.
echo ✅ 小豆包已启动！
echo    本地访问：http://localhost:7860
echo    公网链接：请查看"小豆包-公网"窗口（如已启动）
pause