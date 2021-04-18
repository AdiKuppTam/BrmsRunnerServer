from pydrive.drive import GoogleDrive as Gd
from pydrive.auth import GoogleAuth as Ga


class StorageHandler:

    def __init__(self):
        gauth = Ga()
        gauth.LocalWebserverAuth()
        self.drive = Gd(gauth)
        return

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StorageHandler, cls).__new__(cls)
        return cls.instance

    def get_image_blob(self, name):
        pass

    def delete_stimulus_of_experiment(self, experiment_name):
        pass

    def upload_file(self, file_path):
        """
        upload a single file to google drive
        :param file_path: the sile path
        :return: True if success, False else
        """
        self.drive.CreateFile()

    def upload_directory(self, directory_path):
        """
        upload a single file to google drive
        :param directory_path: the sile path
        :return: True if success, False else
        """
        self.drive.CreateFile()

    def delete_file(self, file_name):
        """
        deletes a filename
        :param file_name: the name of the file we are about to delete
        :return: True if success, False else
        """

    def download_file(self, file_path):
        """
        download a single file to google drive
        :param file_path: the sile path
        :return: True if success, False else
        """
        self.drive.CreateFile()

    def download_directory(self, directory_path):
        """
        download a single file to google drive
        :param directory_path: the sile path
        :return: True if success, False else
        """
        self.drive.CreateFile()

