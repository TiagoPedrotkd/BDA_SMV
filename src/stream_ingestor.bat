@echo off

cd /d D:\Repositories\BDA_SMV
set PYTHONPATH=%cd%

echo Iniciando main.py numa nova janela...
start "Main Script" cmd /c "python src\main.py"

echo Esperando 10 segundos antes de iniciar run_api.py...
timeout /t 10

echo Iniciando run_api.py - Execução 1
python src\run_api.py

echo Esperando 60 segundos...
timeout /t 60

echo Iniciando run_api.py - Execução 2
python src\run_api.py

echo Esperando 60 segundos...
timeout /t 60

echo Iniciando run_api.py - Execução 3
python src\run_api.py

echo Esperando 60 segundos...
timeout /t 60

echo Iniciando run_api.py - Execução 4
python src\run_api.py

echo Todas as execuções concluídas.
pause