@echo off
chcp 65001 > nul

echo === Тест 7: Загрузка VFS со скриптом ===
echo exit | python Main.py --vfs vfs2.xml --script test_vfs1.sh

echo.
echo === Тестирование завершено ===
pause