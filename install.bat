ECHO Setting Current Directory
%~d0
cd "%~dp0"

ECHO Initializing Submodule
git submodule init
git submodule update --remote

ECHO Creating Environment Variable
python -m venv venv

ECHO Activating Environment Variable
call "%~dp0/venv/Scripts/activate.bat"

ECHO Installing Dependencies
python dreamer/install_dependencies.py
python -m pip install -r requirements.txt

ECHO Preparing Weight
rename "%~dp0/sd-v1-4.ckpt" "%~dp0/model.ckpt"
move "%~dp0/model.ckpt" "%~dp0/dreamer/stable_diffusion/models/ldm/stable-diffusion-v1"

ECHO Install Complete
start run.bat
