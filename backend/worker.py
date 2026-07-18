from PySide6.QtCore import QObject
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from backend.downloader import DownloadWorker

from backend.analyzer import VideoAnalyzer


class AnalyzeWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, url: str):
        super().__init__()

        self.url = url

    def run(self):

        try:
            analyzer = VideoAnalyzer()

            info = analyzer.analyze(self.url)

            self.finished.emit(info)

        except Exception as e:
            self.error.emit(str(e))


class WorkerThread(QThread):
    def __init__(self, worker: AnalyzeWorker):
        super().__init__()

        self.worker = worker

        self.worker.moveToThread(self)

        self.started.connect(self.worker.run)

        self.worker.finished.connect(self.quit)
        self.worker.error.connect(self.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        self.finished.connect(self.deleteLater)
class DownloadThread(QThread):
    def __init__(self, worker: DownloadWorker):
        super().__init__()

        self.worker = worker

        self.worker.moveToThread(self)

        self.started.connect(self.worker.run)

        self.worker.finished.connect(self.quit)
        self.worker.error.connect(self.quit)

        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)

        self.finished.connect(self.deleteLater)        
