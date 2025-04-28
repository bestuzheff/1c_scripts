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
 
:: Формирование имени файла резервной копии и log файла отчета
SET DAT=%date:~0,2%.%date:~3,2%.%date:~6,4%
SET DUMPFILE=%BACKUPFOLDER%\%DAT%_%PGDATABASE%.backup
SET LOGFILE=%BACKUPFOLDER%\%DAT%_%PGDATABASE%.log
SET DUMPPATH="%DUMPFILE%"
SET LOGPATH="%LOGFILE%"

:: Выполнение программы создания резервной копии
CALL "%PGBIN%\pg_dump.exe" --format=custom --verbose --file=%DUMPPATH% 2>%LOGPATH%

:: Удаляем все файлы которые старше 30 дней
ForFiles /p "D:\1c_base_backup" /s /c "cmd /c del @file /f /q" /d -30

endlocal