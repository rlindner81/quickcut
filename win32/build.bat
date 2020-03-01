@ECHO OFF
SETLOCAL
SET NAME=quickcut

rmdir /s/q build
rmdir /s/q dist
del /f/q *.spec
del /f/q %NAME%.zip
python -m pip install pip --upgrade
pip install pyinstaller --upgrade
mkdir dist
pyinstaller ^
    --clean ^
    --noupx ^
    ../src/%NAME%.py
copy %NAME%.bat dist
7z a %NAME%.zip .\dist\*
ENDLOCAL
