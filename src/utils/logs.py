import logging

from pathlib import Path


class Logs:
    def __init__(self):
        """Инициализация и настройка системы логирования"""
        self.project_root = Path(__file__).parent.parent.parent
        self.log_dir = self.project_root / "logs"
        self.log_file = self.log_dir / "bot.log"

        self.project_root.mkdir(exist_ok=True)

        time_format = '%H:%M - %d.%m.%Y'

        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] - %(levelname)s - %(message)s',
            datefmt=time_format,
            filename=self.log_file,
            filemode="a"
        )

        logging.info("Инициализация логирования успешна")

logs = Logs()