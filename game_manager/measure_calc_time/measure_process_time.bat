@echo off
set time2=%time: =0%
set year=%date:~0,4%
set month=%date:~5,2%
set day=%date:~8,2%
set hour=%time2:~0,2%
set minute=%time2:~3,2%
set second=%time2:~6,2%

set filename=%year%%month%%day%%hour%%minute%%second%

python -m cProfile -o process_time_%filename%.prof .\strategy_test.py