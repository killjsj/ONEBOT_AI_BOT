@echo off
git remote add origin https://github.com/1qa2ws3ed4rf1/esp32_streamdeck.git
if  not "%1" == ""  (goto file)
:back
set /p mode=mode: 1=add all thing another=input your command(like be git add streamdeck.ino):
if "%mode%" == "1"  (goto all)
if NOT "%mode%" == 1 (goto command)

:command
set /p run=command:
%run%
goto upload

:all
git add .
goto upload

:upload
set /p comm=Please input commit:
git commit -m "%comm%"
git pull
git push -u origin main
pause
exit

:file
echo %1 will upload to github!
git add "%1"
goto back