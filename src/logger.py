import os
import logging
from datetime import datetime


LOG_FORMAT = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
file_path = os.path.join(os.getcwd(), "logs", LOG_FORMAT)
os.makedirs(file_path, exist_ok=True)

FILE = os.path.join(file_path, LOG_FORMAT)

logging.basicConfig(
    filename= FILE,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level= logging.INFO

)