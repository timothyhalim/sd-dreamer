python -m venv venv

call %~dp0/venv/Scripts/activate.bat

python dreamer/install_dependencies.py
python -m pip install -r requirements.txt