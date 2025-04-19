@echo off
:begin
echo What floor do you want the bot to start on?
echo =============================================
echo -
echo 1) Floor 1
echo 2) Floor 2
echo 3) Floor 3
echo 4) Floor 4
echo 5) Floor 5
echo -
set /p op=Type option:
if "%op%"=="1" goto opt1
if "%op%"=="2" goto opt2
if "%op%"=="3" goto opt3
if "%op%"=="4" goto opt4
if "%op%"=="5" goto opt5

echo Please pick a floor:
goto begin

:opt1
echo You picked floor 1
del .\json_files\gacha.json
copy ".\json_files\gacha - Floors 1-5.json" ".\json_files\gacha.json
run.bat
goto exit

:opt2
echo You picked floor 2
del .\json_files\gacha.json
copy ".\json_files\gacha - Floors 2-5-1.json" ".\json_files\gacha.json
run.bat
goto exit

:opt3
echo You picked floor 3
del .\json_files\gacha.json
copy ".\json_files\gacha - Floors 3-5-1-2.json" ".\json_files\gacha.json
run.bat
goto exit

:opt4
echo You picked floor 4
del .\json_files\gacha.json
copy ".\json_files\gacha - Floors 4-5-1-3.json" ".\json_files\gacha.json
run.bat
goto exit

:opt5:
echo You picked floor 5
del .\json_files\gacha.json
copy ".\json_files\gacha - Floors 5-1-4.json" ".\json_files\gacha.json
run.bat
goto exit


:exit
@exit