import pytest
from pathlib import Path
from main import parse_log_line, parse_logs, check_files
from typing import Tuple, Pattern
import re


@pytest.fixture
def log_patterns() -> Tuple[Pattern[str], Pattern[str], Pattern[str]]:
    log_pattern = re.compile(
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} '
        r'(?P<level>\w+) '
        r'(?P<logger>\w+\.\w+): '
        r'(?P<message>.*?)'
        r'(?: \[.*?\])?$'
    )
    success_pattern = re.compile(
        r'^(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) '
        r'(?P<handler>/[^ ]+)'
    )
    error_pattern = re.compile(
        r'^Internal Server Error: '
        r'(?P<handler>/[^ ]+)'
    )
    return (log_pattern, success_pattern, error_pattern)


def test_parse_log_line_success(log_patterns):
    """Проверяет корректность парсинга строки лога с успешным запросом """
    line = "2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]"
    result = parse_log_line(line, log_patterns)
    assert result == ('INFO', '/api/v1/reviews/')


def test_parse_log_line_error(log_patterns):
    """Проверяет парсинг строки лога с ошибкой"""
    line = "2025-03-28 12:11:57,000 ERROR django.request: Internal Server Error: /admin/dashboard/ [192.168.1.29] - ValueError: Invalid input data"
    result = parse_log_line(line, log_patterns)
    assert result == ('ERROR', '/admin/dashboard/')


def test_parse_log_line_skip_non_request(log_patterns):
    """Проверяет, что логи, не относящиеся к django.request, игнорируются."""
    line = "2025-03-28 12:40:47,000 CRITICAL django.core.management: DatabaseError: Deadlock detected"
    result = parse_log_line(line, log_patterns)
    assert result is None


def test_check_files(tmp_path):
    """Проверяет работу функции check_files, которая ищет отсутствующие файлы."""
    existing_file = tmp_path / "test.log"
    existing_file.write_text("test")
    missing_file = tmp_path / "missing.log"

    assert check_files([str(existing_file)]) == []
    assert check_files([str(missing_file)]) == [str(missing_file)]
    assert check_files([str(existing_file), str(missing_file)]) == [str(missing_file)]


def test_parse_logs(tmp_path, log_patterns):
    """Проверяет основную логику анализа логов через функцию parse_logs."""
    log_file = tmp_path / "test.log"
    log_content = """\
2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/test/ 200 OK [192.168.1.1]
2025-03-28 12:44:47,000 ERROR django.request: Internal Server Error: /api/v1/test/ [192.168.1.1] - Error
2025-03-28 12:44:48,000 INFO django.request: GET /api/v1/another/ 200 OK [192.168.1.2]
"""
    log_file.write_text(log_content)

    result = parse_logs([str(log_file)])
    assert result["Total requests"] == 3
    assert result["/api/v1/test/"]["INFO"] == 1
    assert result["/api/v1/test/"]["ERROR"] == 1
    assert result["/api/v1/another/"]["INFO"] == 1