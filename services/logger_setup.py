import logging
import os
from .config import Config

class LoggerSetup:
    @staticmethod
    def setup_logger(name, log_file, level=logging.DEBUG):
        # membuat logger baru.
        logger = logging.getLogger(name)
        
        # hanya setup handler jika belum ada.
        if not logger.hasHandlers():
            # set level logging.
            logger.setLevel(level)
            
            # buat file handler untuk menyimpan log ke file.
            handler = logging.FileHandler(os.path.join(Config.LOG_PATH, log_file))
            
            # set format log message
            handler.setFormatter(
                logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s - %(message)s [%(module)s.%(funcName)s:%(lineno)d]'
                )
            )
            # tambahkan handler ke logger
            logger.addHandler(handler)
            
        return logger
        