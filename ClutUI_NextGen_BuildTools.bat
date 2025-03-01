@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title ClutUI Nextgen Build Tools V0.0.1Alpha	

REM 检测编码环境
for /f "tokens=2 delims=:" %%i in ('chcp') do set CODEPAGE=%%i
set CODEPAGE=!CODEPAGE: =!

if "!CODEPAGE!"=="65001" (
    set "ENCODING=utf-8"
) else if "!CODEPAGE!"=="936" (
    set "ENCODING=gb2312"
) else (
    set "ENCODING=其他编码(!CODEPAGE!)"
)

echo 当前编码环境: !ENCODING!
echo.

echo ===== ClutUI-Nextgen Build Tool =====
echo Version 0.0.1Alpha
echo 正在准备环境...

REM 更新依赖
pip install --upgrade pip
pip install --upgrade pyinstaller pillow

echo 开始打包应用...
echo ==============================================
pyinstaller --noconfirm --onefile --windowed --icon="resources/logo.png" ^
--add-data="core/font/icons/MaterialIcons-Regular.ttf;core/font/icons" ^
--add-data="core/font/icons/codepoints;core/font/icons" ^
--add-data="core/font/icons/statement.txt;core/font/icons" ^
--add-data="core/font/font/HarmonyOS_Sans_SC_Bold.ttf;core/font/font" ^
--add-data="core/font/font/HarmonyOS_Sans_SC_Regular.ttf;core/font/font" ^
--add-data="core/font/font/Mulish-Bold.ttf;core/font/font" ^
--add-data="core/font/font/Mulish-Regular.ttf;core/font/font" ^
--add-data="locales;locales" ^
--add-data="core;core" ^
--add-data="pages;pages" ^
--add-data="preview;preview" ^
--add-data="resources;resources" ^
--add-data="FontLicense;FontLicense" ^
--add-data="tools;tools" ^
--add-data="LICENSE;." ^
--name="ClutUI_Nextgen" ^
ClutUI_Nextgen_Main.py

if %errorlevel% neq 0 (
    echo "打包过程中出现错误，请检查日志。"
    echo "尽管出现错误，程序将继续执行..."
) else (
    echo "打包完成！"
    echo "可执行文件位于 dist/ClutUI_Nextgen.exe"
)

echo ===== 打包过程结束 =====
echo All Done

pause
exit /b 0