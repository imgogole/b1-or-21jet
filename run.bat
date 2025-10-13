@echo off
REM Lancer Flask
start "Flask Server" cmd /k "cd backend && python app.py"

REM Lancer serveur local pour le site
start "Site Frontend" cmd /k "cd frontend && python -m http.server 8000"

echo Les serveurs sont lancés.
pause
