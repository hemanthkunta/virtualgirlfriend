@echo off

:loop
git pull
git add .
git commit -m "Auto sync" 2>nul
git push

timeout /t 10 >nul
goto loop