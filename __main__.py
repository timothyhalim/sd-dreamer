if __name__ == "__main__":
    from Qt.QtWidgets import QApplication
    from sd_dreamer import SDDreamer
    import qdarktheme
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