@echo off
chcp 65001 >nul
title Bookmark Manager 启动器
echo =====================================
echo   Bookmark Manager 一键启动脚本
echo =====================================
echo.

set "BACKEND_DIR=bookmark-manager-admin"
set "FRONTEND_DIR=bookmark-manager-web"

echo [启动] 正在启动后端服务...
cd "%BACKEND_DIR%"

:: 检查并激活虚拟环境
if exist "venv_new\Scripts\activate.bat" (
    echo [信息] 检测到虚拟环境，正在激活...
    call venv_new\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [信息] 检测到虚拟环境，正在激活...
    call venv\Scripts\activate.bat
)

:: 启动后端
start "后端服务" cmd /k "python run.py"
cd ..

echo [启动] 后端服务已启动
ping -n 3 127.0.0.1 >nul

echo [启动] 正在启动前端服务...
cd "%FRONTEND_DIR%"

:: 检查 pnpm
where pnpm >nul 2>&1
if %errorlevel% == 0 (
    start "前端服务" cmd /k "pnpm dev"
) else (
    echo [警告] 未检测到 pnpm，使用 npm...
    start "前端服务" cmd /k "npm run dev"
)

cd ..

echo.
echo =====================================
echo   所有服务已启动！
echo =====================================
echo.
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:9001
echo.
echo 关闭窗口即可停止服务
echo.
pause
