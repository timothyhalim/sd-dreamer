if __name__ == "__main__":
    import sys
    from utils import absolute_path
    sys.path.append(absolute_path("stable_diffusion"))

    import ctypes

    from Qt.QtWidgets import QApplication
    from components.dreamer import Dreamer
    import qdarktheme

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