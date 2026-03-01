@echo off
REM Build DoodleBob as a standalone Windows executable
REM Requires: pip install pyinstaller

echo Building DoodleBob...

pyinstaller --onefile --noconsole --name DoodleBob ^
    --add-data "assets;assets" ^
    --icon=NONE ^
    main.py

echo.
echo Done! Find DoodleBob.exe in the dist\ folder.
pause
