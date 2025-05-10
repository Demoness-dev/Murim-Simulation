import datetime

class log_writer():
    def __init__(self, filename="logs.txt"):
        self.filename = filename
    
    def _build_message(self, text, level, timestamp):
        return f"[{timestamp}] : [{level.upper()}] - {text}\n"
    def write(self, text, level="info"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filename, "a", encoding="utf-8") as file:
            file.write(self._build_message(text, level, timestamp))
    def info(self, text):
        self.write(text, "info")
    def warning(self, text):
        self.write(text, "warning")
    def error(self, text):
        self.write(text, "error")


log = log_writer()