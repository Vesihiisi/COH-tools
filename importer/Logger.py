import datetime
from os import path, makedirs


class Logger(object):

    def create_filename(self):
        return datetime.date.today().strftime("%Y-%m-%d" + ".log")

    def save_line_to_file(self, filename, text):
        with open(filename, 'a', encoding="utf-8") as f:
            f.write(text + "\n")

    def get_current_timestamp(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def append_timestamp_to_message(self, message):
        timestamp = self.get_current_timestamp()
        return timestamp + "\t" + message

    def logit(self, message):
        ts_mess = self.append_timestamp_to_message(message)
        self.save_line_to_file(self.file_path, ts_mess)

    def __init__(self):
        directory_path = "logs"
        filename = self.create_filename()
        self.file_path = path.join(directory_path, filename)
        if not path.exists(directory_path):
            makedirs(directory_path)
        filename = self.create_filename()
        if not path.exists(self.file_path):
            open(self.file_path, 'w', encoding="utf-8").close()
