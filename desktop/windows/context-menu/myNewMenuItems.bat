@echo off
rem  set __COMPAT_LAYER=RunAsInvoker 
set SCRIPTPATH=
rem echo %SCRIPTPATH%

echo Removing unwanted menu items
timeout /t 2 /nobreak

rem REGEDIT.EXE  /S  "%SCRIPTPATH%\gdoc.reg"
rem REGEDIT.EXE  /S  "%SCRIPTPATH%\gsheets.reg"
rem REGEDIT.EXE  /S  "%SCRIPTPATH%\gsheets.reg"

echo removing: ".accdb" 
REGEDIT.EXE  /S  "%SCRIPTPATH%\accdb.reg"



echo Adding new menu items
timeout /t 2 /nobreak

echo adding: ".sh"
REGEDIT.EXE  /S  "%SCRIPTPATH%\bash.reg"
echo adding: ".cmd"
REGEDIT.EXE  /S  "%SCRIPTPATH%\cmd.reg"
echo adding: ".cpp"
REGEDIT.EXE  /S  "%SCRIPTPATH%\cpp.reg"
echo adding: ".csv"
REGEDIT.EXE  /S  "%SCRIPTPATH%\csv.reg"
echo adding: ".go"
REGEDIT.EXE  /S  "%SCRIPTPATH%\go.reg"
echo adding: ".html"
REGEDIT.EXE  /S  "%SCRIPTPATH%\html.reg"
echo adding: ".json"
REGEDIT.EXE  /S  "%SCRIPTPATH%\json.reg"
echo adding: ".md"
REGEDIT.EXE  /S  "%SCRIPTPATH%\markdown.reg"
echo adding: ".ps1"
REGEDIT.EXE  /S  "%SCRIPTPATH%\ps1.reg"
echo adding: ".py"
REGEDIT.EXE  /S  "%SCRIPTPATH%\py.reg"



pause
