class BaseBot:
    def __init__(self, settings):
        self.settings = settings

    def run(self):
        raise NotImplementedError("Subclasses must implement run method")

    def get_statistics(self):
        raise NotImplementedError("Subclasses must implement get_statistics method")