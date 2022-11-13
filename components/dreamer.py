import os

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

from omegaconf import OmegaConf
from stable_diffusion.ldm.generate import Generate
from utils import absolute_path

from Qt.QtCompat import loadUi 
from Qt.QtWidgets import (
    QApplication, QMainWindow,
    QProgressBar, QFileDialog, QSpinBox
)
from Qt.QtGui import (
    QPixmap, QImage, QRegExpValidator, QIcon, QCursor, QColor
)
from Qt.QtCore import QRegExp
from PIL import Image
import qdarktheme

from . import dreamer_resource # Required to show icon
from .colorpicker import ColorPicker
from .popupmenu import PopupMenu
from .painting import Canvas

class Dreamer(QMainWindow):
    def __init__(self, parent = None):
        super(Dreamer, self).__init__(parent)
        ui = os.path.join(os.path.realpath(__file__), "..", "dreamer.ui")
        loadUi(ui, self)
        self.setStyleSheet(qdarktheme.load_stylesheet())

        rx  = QRegExp("[0-9]{30}")
        onlyInt = QRegExpValidator(rx)
        self.seed.setValidator(onlyInt)

        self.canvas = Canvas(self.image_area)
        self.canvas.resize(50, 50)

        self.progressbar = QProgressBar()
        self.progressbar.setMaximumHeight(10)
        self.statusBar().addPermanentWidget(self.progressbar)
        self.progressbar.hide()

        self.actionNew.triggered.connect(self.toggle_generator)
        self.actionOpenImage.triggered.connect(self.open_image)
        self.actionSaveImage.triggered.connect(self.save_image)
        self.actionPaint.triggered.connect(self.toggle_painter)
        self.actionErase.triggered.connect(self.toggle_eraser)
        self.actionBrushColor.triggered.connect(self.open_color_picker)
        self.actionBrushSize.triggered.connect(self.open_brush_size)

        self.mode.currentIndexChanged.connect(self.change_mode)
        self.steps.valueChanged.connect(lambda value: self.steps_value.setText("%02d" %value))
        self.random_seed.stateChanged.connect(lambda : self.seed.setEnabled(not self.random_seed.isChecked()))
        self.random_seed.stateChanged.connect(lambda : self.variation.setEnabled(not self.random_seed.isChecked()))
        self.generate_btn.clicked.connect(self.generate)
        self.upscale_btn.clicked.connect(self.upscale_image)

        models_config  = absolute_path("stable_diffusion/configs/models.yaml")
        model   = "stable-diffusion-1.4"

        models  = OmegaConf.load(models_config)
        config  = absolute_path("stable_diffusion/" + models[model].config)
        weights = absolute_path("stable_diffusion/" + models[model].weights)

        self.generator = Generate(
                        embedding_path=None,
                        # These args are deprecated, but we need them to specify an absolute path to the weights.
                        weights=weights,
                        config=config
                    )
        self.generator.load_model()

        self.seed.setText(str(self.generator.seed or 0))
        
        self.set_brush_color(QColor.fromRgb(255, 255, 255, 255))
        self.change_mode()

    def toggle_generator(self):
        self.generator_widget.setVisible(self.actionNew.isChecked())

    def toggle_painter(self):
        self.actionErase.setChecked(False)
        self.canvas.enableDrawing(self.actionPaint.isChecked())
        self.canvas.painting.setBrushMode("draw")

    def toggle_eraser(self):
        self.actionPaint.setChecked(False)
        self.canvas.enableDrawing(self.actionErase.isChecked())
        self.canvas.painting.setBrushMode("erase")

    def change_mode(self):
        self.current_mode = self.mode.currentText()
        self.actionPaint.setChecked(False)
        self.actionErase.setChecked(False)

        self.general_widget.setVisible(True)
        self.training_widget.setVisible(False)
        self.upscale_widget.setVisible(False)

        self.general_settings.setVisible(True)
        self.prompt_settings.setVisible(False)
        self.image_settings.setVisible(False)
        self.actionPaint.setVisible(False)
        self.actionErase.setVisible(False)
        self.actionBrushColor.setVisible(False)
        self.actionBrushSize.setVisible(False)

        if self.current_mode == "Text to Image":
            self.prompt_settings.setVisible(True)
        elif self.current_mode == "Image to Image":
            self.canvas.painting.setDrawMode("paint")
            self.image_settings.setVisible(True)
            self.actionPaint.setVisible(True)
            self.actionErase.setVisible(True)
            self.actionBrushColor.setVisible(True)
            self.actionBrushSize.setVisible(True)
        elif self.current_mode == "InPainting":
            self.canvas.painting.setDrawMode("mask")
            self.actionPaint.setVisible(True)
            self.actionErase.setVisible(True)
            self.actionBrushSize.setVisible(True)
        elif self.current_mode == "Upscaling":
            self.general_widget.setVisible(False)
            self.upscale_widget.setVisible(True)
        elif self.current_mode == "Training":
            self.general_widget.setVisible(False)
            self.training_widget.setVisible(True)

    def open_color_picker(self):
        menu = PopupMenu(self)
        cc = self.canvas.brushColor()
        cp = ColorPicker(self, rgb=(cc.red(), cc.green(), cc.blue()))
        cp.colorChanged.connect(self.set_brush_color)
        cp.setMaximumWidth(500)
        
        menu.addWidget(cp) 
        menu.exec_(QCursor.pos())

    def set_brush_color(self, color):
        color_pixmap = QPixmap(64, 64)
        color_pixmap.fill(color)
        icon = QIcon()
        icon.addPixmap(color_pixmap, QIcon.Normal, QIcon.On)
        self.actionBrushColor.setIcon(icon)
        self.brush_color = color
        self.canvas.setBrushColor(self.brush_color)

    def open_brush_size(self):
        menu = PopupMenu(self)
        sp = QSpinBox(self)
        sp.setValue(self.canvas.brushSize())
        sp.valueChanged.connect(self.set_brush_size)

        menu.addWidget(sp) 
        menu.exec_(QCursor.pos())

    def set_brush_size(self, size):
        self.canvas.setBrushSize(size)

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
        step_image = self.generator.sample_to_image(samples)
        pix = self.pil2pixmap(step_image)
        self.canvas.setPainting(pix)
        self.progressbar.setValue(step+1)
        QApplication.processEvents()

    def image_writer(self, image, seed, *args, **kwargs):
        pix = self.pil2pixmap(image)
        self.canvas.setPainting(pix)
        self.generate_btn.setEnabled(True)
        self.progressbar.hide()
        self.seed.setText(str(seed))
        self.statusBar().clearMessage()
        QApplication.processEvents()

    def upscale_image(self):
        upscale = None if self.upscale.value() == 1 else [self.upscale.value()]
        if upscale:
            self.generator.upscale(self.canvas.getPainting(), int(self.seed.text()), upscale, self.image_writer)

    def generate(self):
        prompt=self.prompt_edit.toPlainText()
        steps = self.steps.value()
        seed = None if self.random_seed.isChecked() else int(self.seed.text())
        width = self.image_width.value()
        height = self.image_height.value()
        seamless = self.seamless.isChecked() # generate tileable/seamless textures
        init_img = None if self.current_mode == "Text to Image" else self.canvas.getPainting()  # path to an initial image - its dimensions override width and height
        init_mask = self.canvas.painting.getMask() if self.current_mode == "InPainting" else None
        prompt_strength = self.strength.value() # how strongly the prompt influences the image (7.5) (must be >1)
        image_change = min(max(1-self.preserve_image.value(), 0.01), 0.99) if self.current_mode == "Image to Image" else 0.99 # strength for noising/unnoising init_img. 0.0 preserves image exactly, 1.0 replaces it completely
        upscaling = None  # strength for GFPGAN. 0.0 preserves image exactly, 1.0 replaces it completely
        reconstruct = self.reconstruct.value() # strength for GFPGAN. 0.0 preserves image exactly, 1.0 replaces it completely
        seed_randomness = self.variation.value() # image randomness (eta=0.0 means the same seed always produces the same image)
        sampler_name = self.sampler.currentText()

        self.progressbar.setValue(0)
        self.progressbar.setMaximum(steps)
        self.generate_btn.setEnabled(False)
        self.statusBar().showMessage("Generating Image from Prompt")
        self.progressbar.show()
        QApplication.processEvents()

        try:
            self.generator.prompt2image(
                prompt=prompt,
                iterations=1,
                steps=steps,
                seed=seed,
                width=width,
                height=height,
                cfg_scale=prompt_strength,
                init_img=init_img,
                init_mask=init_mask,
                seamless=seamless,
                fit=True,
                strength=image_change,
                upscale=upscaling,
                gfpgan_strength=reconstruct,
                ddim_eta=seed_randomness,
                step_callback=self.view_step,
                image_callback=self.image_writer,
                sampler_name=sampler_name
            )
        except:
            self.generate_btn.setEnabled(True)
            self.statusBar().showMessage("Error")


    def open_image(self):
        filepath = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            filter="All Files (*)", selectedFilter="All Files (*)"
        )
        if filepath:
            filepath = filepath[0]

        if os.path.exists(filepath):
            image = Image.open(filepath)
            self.canvas.setPainting(self.pil2pixmap(image))

    def save_image(self):
        fileName = QFileDialog.getSaveFileName(
            self, "Save Image", "image.jpg", 
            filter="Image (*.jpg);;All Files (*)", selectedFilter="Image (*.jpg)"
        )
        if fileName:
            filename = fileName[0]
            image = self.canvas.getPainting()
            if image:
                image.save(filename)

if __name__ == "__main__":
    from Qt.QtWidgets import QApplication
    from sd_dreamer import Dreamer
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

    w = Dreamer()
    w.show()

    if new:
        app.exec_()