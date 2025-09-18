@echo off
chcp 65001 > nul
echo === Тест 1: Запуск с VFS и скриптом 1 ===
python Main.py --vfs C:\Users\%USERNAME%\my_vfs --script test_script1.sh

echo.
echo === Тест 2: Запуск только со скриптом 2 ===
python Main.py --script test_script2.sh

echo.
echo === Тест 3: Запуск только с VFS ===
echo exit | python Main.py --vfs C:\Temp\custom_vfs

echo.
echo === Тест 4: Запуск без параметров ===
echo exit | python Main.py

echo.
echo === Тестирование завершено ===
pause