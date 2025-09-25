@echo off
chcp 65001 >nul
title 水印工具
echo.
echo ========================================
echo           水印工具启动器
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo.
    echo 请先安装Python 3.6或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

REM 检查并安装依赖
echo 🔍 检查依赖...
python -c "import tkinter, PIL" >nul 2>&1
if errorlevel 1 (
    echo 📦 安装依赖中...
    pip install Pillow
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        echo 请手动运行: pip install Pillow
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
) else (
    echo ✅ 依赖检查通过
)

echo.
echo 🚀 启动水印工具...
echo.

REM 运行应用
python "水印工具.py"

if errorlevel 1 (
    echo.
    echo ❌ 应用启动失败
    echo 请检查Python环境和依赖
    pause
)
