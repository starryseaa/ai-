@echo off
cd /d %~dp0
echo 正在启动AI智能伴侣...
python -m streamlit run app.py
pause
