from gunicorn.app.base import BaseApplication
import multiprocessing

def number_of_workers():
    """Calculate the number of Gunicorn workers based on CPU count."""
    return (multiprocessing.cpu_count() * 2) + 1

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application