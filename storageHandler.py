class StorageHandler:
    def __init__(self):
        pass

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StorageHandler, cls).__new__(cls)
        return cls.instance

    def get_image_blob(self, name):
        pass
