import os

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

from omegaconf import OmegaConf
from dreamer.stable_diffusion.ldm.generate import Generate
from dreamer.utils import absolute_path

from Qt.QtCompat import loadUi 
from Qt.QtWidgets import (
    QApplication, QMainWindow, 
    QProgressBar, QFileDialog
)
from Qt.QtGui import QPixmap, QImage
from PIL import Image
import qrc # Required to show icon
import qdarktheme

class SDDreamer(QMainWindow):
    def __init__(self, parent = None):
        super(SDDreamer, self).__init__(parent)
        ui = os.path.join(os.path.realpath(__file__), "..", "sd_dreamer.ui")
        loadUi(ui, self)
        self.setStyleSheet(qdarktheme.load_stylesheet())

        self.progressbar = QProgressBar()
        self.progressbar.setMaximumHeight(10)
        self.statusBar().addPermanentWidget(self.progressbar)
        self.progressbar.hide()

        self.actionNew.triggered.connect(self.show_generator)
        self.actionSave.triggered.connect(self.save_image)

        self.steps.valueChanged.connect(lambda value: self.steps_value.setText("%02d" %value))
        self.iteration.valueChanged.connect(lambda value: self.iteration_value.setText("%02d" %value))
        self.random_seed.stateChanged.connect(lambda : self.seed.setEnabled(not self.random_seed.isChecked()))
        self.generate_btn.clicked.connect(self.generate)

        models_config  = absolute_path("stable_diffusion/configs/models.yaml")
        model   = "stable-diffusion-1.4"

        models  = OmegaConf.load(models_config)
        config  = absolute_path("stable_diffusion/" + models[model].config)
        weights = absolute_path("stable_diffusion/" + models[model].weights)

        self.generator = Generate(
                        # These args are deprecated, but we need them to specify an absolute path to the weights.
                        weights=weights,
                        config=config,
                        full_precision=True
                    )
        self.generator.load_model()

    def show_generator(self):
        self.widget.setVisible(self.actionNew.isChecked())

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

    def view_step(self, samples, step):
        step_image = self.generator._sample_to_image(samples)
        pix = self.pil2pixmap(step_image)
        self.image_preview.setPixmap(pix)
        self.progressbar.setValue(step+1)
        QApplication.processEvents()

    def image_writer(self, image, seed, upscaled=False):
        pix = self.pil2pixmap(image)
        self.image_preview.setPixmap(pix)
        self.progressbar.hide()
        self.statusBar().clearMessage()
        QApplication.processEvents()

    def generate(self):
        prompt=self.prompt_edit.toPlainText()
        iterations = self.iteration.value()
        steps = self.steps.value()
        seed = None if self.random_seed.isChecked() else self.seed.value()
        width = self.image_width.value()
        height = self.image_height.value()
        prompt_strength = 7.5 # how strongly the prompt influences the image (7.5) (must be >1)
        seamless = self.seamless.isChecked() # generate tileable/seamless textures
        init_img = None # path to an initial image - its dimensions override width and height
        strength = 0.75 # strength for noising/unnoising init_img. 0.0 preserves image exactly, 1.0 replaces it completely
        upscaling = 0.0 # strength for GFPGAN. 0.0 preserves image exactly, 1.0 replaces it completely
        seed_randomness = 0.0 # image randomness (eta=0.0 means the same seed always produces the same image)
        sampler_name = self.sampler.currentText()

        self.progressbar.setMaximum(steps)
        self.statusBar().showMessage("Generating Image from Prompt")
        self.progressbar.show()
        QApplication.processEvents()

        self.generator.prompt2image(
            prompt=prompt,
            iterations=iterations,
            steps=steps,
            seed=seed,
            width=width,
            height=height,
            cfg_scale=prompt_strength,
            init_img=init_img,
            seamless=seamless,
            fit=True,
            strength=strength,
            gfpgan_strength=upscaling, # 0 disables upscaling, which is currently not supported by the addon.
            ddim_eta=seed_randomness,
            step_callback=self.view_step,
            image_callback=self.image_writer,
            sampler_name=sampler_name
        )

    def save_image(self):
        fileName = QFileDialog.getSaveFileName(
            self, "Save Image", "image.jpg", 
            filter="Image (*.jpg);;All Files (*)", selectedFilter="Image (*.jpg)"
        )
        if fileName:
            filename = fileName[0]
            image = self.image_preview.pixmap()
            if image:
                image.save(filename)

if __name__ == "__main__":
    from Qt.QtWidgets import QApplication
    from sd_dreamer import SDDreamer
    import sys
    import ctypes

    app = QApplication.instance()
    new = False
    if not app:
        # Register to windows as proper application so we can change the icon
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Dreamer")

        app = QApplication(sys.argv)
        app.setStyleSheet(qdarktheme.load_stylesheet())
        new = True

    w = SDDreamer()
    w.show()

    if new:
        app.exec_()