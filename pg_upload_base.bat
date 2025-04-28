@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: Проверяем, существует ли файл .env
if not exist ".env" (
    echo Файл .env не найден!
    exit /b 1
)

:: Читаем файл .env построчно
for /f "usebackq delims=" %%i in (".env") do (
    :: Пропускаем пустые строки и комментарии (начинающиеся с #)
    if not "%%i"=="" (
        echo %%i | findstr /b "#" >nul
        if errorlevel 1 (
            :: Разделяем ключ и значение
            for /f "tokens=1,* delims==" %%a in ("%%i") do (
                set "key=%%a"
                set "value=%%b"
                :: Устанавливаем переменную среду
                set "!key!=!value!"
            )
        )
    )
)

REM ВЫПОЛНЕНИЕ КОМАНДЫ (ПРОГРАММЫ) ДЛЯ СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ БАЗЫ 
CALL "%PGBIN%\pg_restore" -U %PGUSER% -d %PGDATABASE% %BACKUPFOLDER%\%BACKUPFILE%

endlocal

