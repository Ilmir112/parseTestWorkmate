import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Уровень логгера — чтобы он обрабатывал все сообщения

file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.ERROR)  # Только ERROR и CRITICAL

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Все сообщения от DEBUG и выше

# Форматтер для обоих обработчиков
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
