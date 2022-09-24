if __name__ == "__main__":
    from Qt.QtWidgets import QApplication
    from sd_dreamer import SDDreamer
    import sys

    app = QApplication.instance()
    new = False
    if not app:
        app = QApplication(sys.argv)
        new = True

    w = SDDreamer()
    w.show()

    if new:
        app.exec_()