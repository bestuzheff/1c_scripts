@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

rem Удаляем лишние файлы из папки с базой


rem Укажите путь к папке с базой
set FOLDER=C:\base_1c

rem Проверяем, существует ли папка
if not exist "%FOLDER%" (
    echo Указанная папка не существует.
    exit /b
)

rem Переход в папку
cd /d "%FOLDER%"

rem Удаляем все файлы, кроме 1cv8.1cd и DoNotCopy.txt
for %%F in (*) do (
    if /I not "%%F"=="1cv8.1cd" if /I not "%%F"=="DoNotCopy.txt" del "%%F"
)
rem Удаляем вложенные папки
for /D %%D in (*) do rd /s /q "%%D"

echo Очистка завершена.
exit /b
