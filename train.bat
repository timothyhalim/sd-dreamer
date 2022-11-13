call %~dp0/venv/Scripts/activate.bat

SET PL_TORCH_DISTRIBUTED_BACKEND=gloo
SET CUDA_VISIBLE_DEVICES=0

python %~dp0/stable_diffusion/main.py -t ^
    --base ./configs/stable-diffusion/v1-finetune.yaml ^
    -n eva_owl_diary ^
    --gpus 1 ^
    --data_root D:/Scripts/sd-dreamer/training/owl-diary ^
    --init_word 'eva_owl_diary'

pause