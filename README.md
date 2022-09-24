# Stable Diffusion

PySide2 Powered stable-diffusion that can be run locally, sub module from [Stable Diffusion](https://github.com/timothyhalim/stable-diffusion)


## Installation
1. Install Python 3.7+ ( I use 3.9.7 ) 
2. Download or clone this repo using Git
3. Download weight from [https://huggingface.co/CompVis](https://cdn-lfs.huggingface.co/repos/4c/37/4c372b4ebb57bbd02e68413d4951aa326d4b3cfb6e62db989e529c6d4b26fb21/fe4efff1e174c627256e44ec2991ba279b3816e364b49f9be2abc0b3ff3f8556?response-content-disposition=attachment%3B%20filename%3D%22sd-v1-4.ckpt%22)
4. Rename the downloaded file to 'model.ckpt' 
5. Place the downloaded weight in dreamer\stable_diffusion\models\ldm\stable-diffusion-v1\model.ckpt
6. Run CMD as Administrator in repo directory
7. (Optional) Create virtual env using 'python -m venv venv'
8. (Optional) Activate the virtual env using '%cd%/venv/Scripts/activate.bat'
9. Run 'python dreamer/install_dependencies.py' to install dependencies (require admin)
10. Run 'python -m pip install -r requirements.txt' to install the required component
11. Run 'run.bat' to run the app