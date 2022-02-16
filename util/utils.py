from PyQt5.QtCore import QObject, pyqtSignal, QEvent
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from datetime import date
import hashlib, time, threading


def clickable(widget):

    class Filter(QObject):
        clicked = pyqtSignal()

        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        return True
            return False

    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked


def hashDigest(value:str)->bytes:
    if not isinstance(value, str):
        raise TypeError('string argument needed')
    m = hashlib.sha256()
    m.update(value.encode('utf-8'))
    return m.digest()


def createSvgFromText(svg_txt):
    svg_str = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
    svg_str += svg_txt
    svg_str = svg_str.strip()
    svg_bytes = bytearray(svg_str, encoding='utf-8')
    svgWidget = QSvgWidget()
    svgWidget.renderer().load(svg_bytes)
    return svgWidget


OS_PATH_INHIBITION = list('.\"\\:?<>|*')
def filter_window_path(name):
    for inhibit in OS_PATH_INHIBITION:
        name = name.replace(inhibit, '')
    return name


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def _run(self):
        self.is_running = True
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run())
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
