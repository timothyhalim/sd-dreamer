@ECHO OFF
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
python stable_diffusion/install_dependencies.py
python -m pip install -r requirements.txt
python stable_diffusion/scripts/preload_models.py

ECHO Preparing Weight
rename "sd-v1-4.ckpt" "model.ckpt"
move "%~dp0/model.ckpt" "%~dp0/stable_diffusion/models/ldm/stable-diffusion-v1"

ECHO Install Complete
start run.bat
