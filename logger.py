import os 
import logging

from config import BASE_DIR
        
class Logger():
    log_path = os.path.join(BASE_DIR, 'logs')
    log_file = os.path.join(BASE_DIR, 'logs', "messages.log")
    logging = logging

    def __init__(self, module_name, file_path):
        if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)
        else:
            # Clear log contents
            open(self.log_file, 'w').close()
            
        self.logging.getLogger(module_name)
        self.logging.basicConfig(
            filename=self.log_file, 
            level=logging.INFO,
            format='%(asctime)s — %(levelname)s - %(message)s',
            datefmt='%Y-%m/%dT%H:%M:%S',
        )
        self.module = module_name
        self.path = file_path
    
    def log(self, level, message:  str):
        level = level.upper()
        
        if level == "WARNING":
            self.logging.warning(message)
        elif level == "DEBUG":
            self.logging.debug(message)
        elif level == "ERROR":
            self.logging.error(message)
        elif level == "CRITICAL":
            self.logging.critical(message)
        else:
            self.logging.info(message)