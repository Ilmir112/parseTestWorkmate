import argparse
import json
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime

from tabulate import tabulate

from logger import logger


class Report(ABC):
    HEADERS = []

    def __init__(self, logs):
        self.logs = logs

    @abstractmethod
    def generate_report(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    @classmethod
    def print_report(cls, report_data):
        print(tabulate(report_data, headers=cls.HEADERS, tablefmt="grid"))

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="Генерация отчета по логам")
        parser.add_argument(
            "--file", nargs="+", required=True, help="Путь к лог-файлу(ам)"
        )
        parser.add_argument(
            "--report",
            choices=["average", "user_agent"],
            default="average",
            help="Тип отчета",
        )
        parser.add_argument("--date", help="Дата запроса в формате ГГГГ-ММ-ДД")
        return parser.parse_args()

    @staticmethod
    def read_logs(file_paths):
        logs = []
        for path in file_paths:
            try:
                with open(path, "r", encoding="utf-8") as file:
                    for line in file:
                        try:
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue
            except FileNotFoundError:
                logger.error(f"Файл не найден: {path}")
            except Exception as e:
                logger.error(f"Ошибка при чтении файла {path}: {e}")
        return logs


class UserAgentReport(Report):
    HEADERS = []

    def __init__(self, logs):
        super().__init__(logs)
        self.logs = logs

    def get_name(self):
        return "UserAgentAnalysis"

    def generate_report(self):
        pass


class ParseLogs(Report):
    HEADERS = ["handler", "total", "avg_response_time"]

    def __init__(self, logs):
        super().__init__(logs)
        self.logs = logs

    def get_name(self):
        return "ParseLogs"

    def filter_logs_by_date(self, date_str):
        if not date_str:
            return self.logs
        filtered_logs = []
        for log in self.logs:
            timestamp_str = log.get("@timestamp")
            if not timestamp_str:
                continue
            try:
                log_date = datetime.fromisoformat(timestamp_str.rstrip("Z"))
                filter_date = datetime.strptime(date_str, "%Y-%m-%d")
                if log_date.date() == filter_date.date():
                    filtered_logs.append(log)
            except ValueError:
                continue
        return filtered_logs

    def generate_report(self):
        try:
            endpoint_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0})

            for log in self.logs:
                url = log.get("url")
                response_time = log.get("response_time")
                if url and response_time is not None:
                    endpoint_stats[url]["count"] += 1
                    endpoint_stats[url]["total_time"] += response_time

            report_data = []
            for endpoint, data in endpoint_stats.items():
                avg_time = data["total_time"] / data["count"]
                report_data.append([endpoint, data["count"], f"{avg_time:.3f}"])

            return report_data

        except Exception as e:
            logger.error(f"Критическая ошибка при генерации отчета: {e}")
            raise RuntimeError


def main():
    args = ParseLogs.parse_args()

    logs = ParseLogs.read_logs(args.file)
    logger.info(f"Всего загружено логов: {len(logs)}")

    if args.report == "average":
        parser_instance = ParseLogs(logs)
    else:
        raise ValueError("Неизвестный тип отчета")

    if args.date:
        logger.info(f"Фильтрация логов по дате: {args.date}")
        parser_instance.logs = parser_instance.filter_logs_by_date(args.date)
        logger.info(f"Всего загружено логов по дате: {len(parser_instance.logs)}")

    report_data = parser_instance.generate_report()

    parser_instance.print_report(report_data)


if __name__ == "__main__":
    main()
