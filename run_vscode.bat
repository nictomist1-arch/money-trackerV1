@echo off
echo Запуск проекта в VS Code...

cd /d "C:\Users\User\money-tracker"

REM Создаем папку .vscode если нет
if not exist ".vscode" mkdir .vscode

REM Создаем launch.json
echo { > .vscode\launch.json
echo     "version": "0.2.0", >> .vscode\launch.json
echo     "configurations": [ >> .vscode\launch.json
echo         { >> .vscode\launch.json
echo             "name": "FastAPI", >> .vscode\launch.json
echo             "type": "python", >> .vscode\launch.json
echo             "request": "launch", >> .vscode\launch.json
echo             "module": "uvicorn", >> .vscode\launch.json
echo             "args": [ >> .vscode\launch.json
echo                 "app.main:app", >> .vscode\launch.json
echo                 "--reload", >> .vscode\launch.json
echo                 "--host", >> .vscode\launch.json
echo                 "0.0.0.0", >> .vscode\launch.json
echo                 "--port", >> .vscode\launch.json
echo                 "8000" >> .vscode\launch.json
echo             ], >> .vscode\launch.json
echo             "jinja": true, >> .vscode\launch.json
echo             "justMyCode": true >> .vscode\launch.json
echo         } >> .vscode\launch.json
echo     ] >> .vscode\launch.json
echo } >> .vscode\launch.json

REM Открываем проект в VS Code
code .

echo.
echo ✅ Проект открыт в VS Code!
echo.
echo Инструкция:
echo 1. Нажмите F5 для запуска сервера
echo 2. Или в терминале: uvicorn app.main:app --reload
echo 3. Откройте браузер: http://localhost:8000
pause