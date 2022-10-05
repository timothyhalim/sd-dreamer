from Qt.QtWidgets import QMenu, QWidgetAction

class PopupMenu(QMenu):
    def addWidget(self, widget):
        act = QWidgetAction(self)
        act.setDefaultWidget(widget)
        self.addAction(act) 

    def mouseReleaseEvent(self, e):
        print(e.pos())
        super(PopupMenu, self).mouseReleaseEvent(e)
        
    def mouseReleaseEvent(self, e):
        return
        # super(PopupMenu, self).mouseReleaseEvent(e)