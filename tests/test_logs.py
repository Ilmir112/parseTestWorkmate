import json

import pytest
from unittest.mock import patch, mock_open
from main import ParseLogs


# Тест для parse_args с разными аргументами
@pytest.mark.parametrize(
    "argv, expected_files, expected_report",
    [
        (
            ["main.py", "--file", "logs_files/example1.log"],
            ["logs_files/example1.log"],
            "average",
        ),
        (
            [
                "main.py",
                "--file",
                "logs_files/example1.log",
                "logs_files/example2.log",
                "--report",
                "average",
            ],
            ["logs_files/example1.log", "logs_files/example2.log"],
            "average",
        ),
    ],
)
def test_parse_args_parametrized(argv, expected_files, expected_report):
    with patch("sys.argv", argv):
        args = ParseLogs.parse_args()
        assert args.file == expected_files
        assert args.report == expected_report


# Тест для read_logs с разными содержимым файлов
@pytest.mark.parametrize(
    "file_content, expected_logs",
    [
        (
            json.dumps({"url": "/api", "response_time": 0.1})
            + "\n"
            + "not a json\n"
            + json.dumps({"url": "/api", "response_time": 0.2}),
            [
                {"url": "/api", "response_time": 0.1},
                {"url": "/api", "response_time": 0.2},
            ],
        ),
        ("", []),  # пустой файл
    ],
)
def test_read_logs_parametrized(file_content, expected_logs):
    with patch("builtins.open", mock_open(read_data=file_content)):
        logs = ParseLogs.read_logs(["dummy_path"])
        assert logs == expected_logs


# Тест для generate_report с разными наборами логов
@pytest.mark.parametrize(
    "logs_input, expected",
    [
        (
            [
                {"url": "/endpoint1", "response_time": 0.2},
                {"url": "/endpoint1", "response_time": 0.4},
                {"url": "/endpoint2", "response_time": 0.3},
            ],
            [["/endpoint1", 2, "0.300"], ["/endpoint2", 1, "0.300"]],
        ),
        ([], []),  # пустой список логов
    ],
)
def test_generate_report_with_various_logs(logs_input, expected):
    parser_instance = ParseLogs(logs_input)
    result = parser_instance.generate_report()
    for exp_row in expected:
        assert exp_row in result


# Тест для filter_logs_by_date
def test_filter_logs_by_date():
    logs = [
        {"@timestamp": "2025-07-01T12:00:00Z", "url": "/api"},
        {"@timestamp": "2025-07-02T12:00:00Z", "url": "/api"},
        {"@timestamp": "invalid-date", "url": "/api"},
        {"@timestamp": None, "url": "/api"},
    ]
    parser = ParseLogs(logs)
    filtered = parser.filter_logs_by_date("2025-07-01")
    filtered_none = parser.filter_logs_by_date("2024-07-01")

    assert len(filtered) == 1
    assert len(filtered_none) == 0
    assert filtered[0]["@timestamp"].startswith("2025-07-01")


# Тест для print_report — проверка вывода
def test_print_report(capsys):
    report_data = [["/test", 3, "0.123"]]
    ParseLogs.print_report(report_data)
    captured = capsys.readouterr()
    assert "/test" in captured.out
    assert "3" in captured.out


# Новый тест для ситуации, когда --file не передан
def test_parse_args_missing_file():
    with patch("sys.argv", ["main.py"]):
        # Ожидаем SystemExit из-за отсутствия обязательных аргументов
        with pytest.raises(SystemExit):
            ParseLogs.parse_args()


# Тест для ситуации, когда передан неправильный аргумент --report
def test_parse_args_invalid_report():
    with patch("sys.argv", ["main.py", "--file", "log.log", "--report", "invalid"]):
        # Ожидаем SystemExit из-за неправильного выбора в argparse
        with pytest.raises(SystemExit):
            ParseLogs.parse_args()


def test_read_logs_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        logs = ParseLogs.read_logs(["nonexistent.log"])
        # Логи должны быть пустыми при ошибке открытия файла
        assert logs == []


def test_read_logs_json_decode_error():
    mock_data = "{invalid json}\n" + json.dumps({"url": "/test"})
    with patch("builtins.open", mock_open(read_data=mock_data)):
        logs = ParseLogs.read_logs(["dummy"])
        # Должен пропустить некорректные строки и вернуть только валидные
        assert len(logs) == 1
        assert logs[0]["url"] == "/test"


def test_generate_report_with_zero_response_time():
    logs = [{"url": "/zero", "response_time": 0}]
    parser = ParseLogs(logs)
    report = parser.generate_report()
    assert report[0][2] == "0.000"


# Проверка метода get_name()
def test_get_name():
    parser = ParseLogs([])
    assert parser.get_name() == "ParseLogs"
