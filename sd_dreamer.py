import os

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

from omegaconf import OmegaConf
from dreamer.stable_diffusion.ldm.generate import Generate
from dreamer.utils import absolute_path

from Qt.QtCompat import loadUi 
from Qt.QtWidgets import (
    QApplication, QMainWindow, QMenu, QWidgetAction, 
    QLineEdit, QPushButton
)
from Qt.QtGui import QPixmap, QImage, QCursor
from PIL import Image

class SDDreamer(QMainWindow):
    def __init__(self, parent = None):
        super(SDDreamer, self).__init__(parent)
        ui = os.path.join(os.path.realpath(__file__), "..", "sd_dreamer.ui")
        loadUi(ui, self)

        self.prompt = "Blank White Space"

        models_config  = absolute_path('stable_diffusion/configs/models.yaml')
        model   = 'stable-diffusion-1.4'

        models  = OmegaConf.load(models_config)
        config  = absolute_path('stable_diffusion/' + models[model].config)
        weights = absolute_path('stable_diffusion/' + models[model].weights)

        self.generator = Generate(
                        conf=models_config,
                        model=model,
                        # These args are deprecated, but we need them to specify an absolute path to the weights.
                        weights=weights,
                        config=config,
                        full_precision=True
                    )
        self.generator.load_model()

        self.actionNew.triggered.connect(self.new)

    def view_step(self, samples, step):
        step_image = self.generator._sample_to_image(samples)
        pix = self.pil2pixmap(step_image)
        self.label.setPixmap(pix)
        QApplication.processEvents()

    def image_writer(self, image, seed, upscaled=False):
        # if not upscaled:
        #     image.save(absolute_path(f"output/{seed}.jpg"))
        pix = self.pil2pixmap(image)
        self.label.setPixmap(pix)
        QApplication.processEvents()

    def pil2pixmap(self, im):
        if im.mode == "RGB":
            r, g, b = im.split()
            im = Image.merge("RGB", (b, g, r))
        elif  im.mode == "RGBA":
            r, g, b, a = im.split()
            im = Image.merge("RGBA", (b, g, r, a))
        elif im.mode == "L":
            im = im.convert("RGBA")
            
        im2 = im.convert("RGBA")
        data = im2.tobytes("raw", "RGBA")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        return pixmap

    def new(self):
        menu = QMenu(self)
        widget = QWidgetAction(menu)
        prompt = QLineEdit()
        prompt.setText(self.prompt)
        prompt.textChanged.connect(self.update_prompt)
        widget.setDefaultWidget(prompt)
        prompt.setMaximumWidth(500)
        menu.addAction(widget) 

        widget = QWidgetAction(menu)
        generate = QPushButton("Generate")
        generate.clicked.connect(self.generate)
        widget.setDefaultWidget(generate)
        generate.setMaximumWidth(500)
        menu.addAction(widget) 

        menu.exec_(QCursor.pos())

    def update_prompt(self, value):
        self.prompt = value

    def generate(self):
        self.generator.prompt2image(
            # prompt string (no default)
            prompt=self.prompt,
            # iterations (1); image count=iterations
            iterations=1,
            # refinement steps per iteration
            steps=25,
            # seed for random number generator
            seed=None, #if scene.dream_textures_prompt.seed == -1 else scene.dream_textures_prompt.seed,
            # width of image, in multiples of 64 (512)
            width=512,
            # height of image, in multiples of 64 (512)
            height=512,
            # how strongly the prompt influences the image (7.5) (must be >1)
            cfg_scale=7.5,
            # path to an initial image - its dimensions override width and height
            init_img=None,

            # generate tileable/seamless textures
            seamless=False,

            fit=True,
            # strength for noising/unnoising init_img. 0.0 preserves image exactly, 1.0 replaces it completely
            strength=0.75,
            # strength for GFPGAN. 0.0 preserves image exactly, 1.0 replaces it completely
            gfpgan_strength=0.0, # 0 disables upscaling, which is currently not supported by the addon.
            # image randomness (eta=0.0 means the same seed always produces the same image)
            ddim_eta=0.0,
            # a function or method that will be called each step
            step_callback=self.view_step,
            # a function or method that will be called each time an image is generated
            image_callback=self.image_writer,
            
            sampler_name='k_lms'
        )