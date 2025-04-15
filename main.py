import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Pattern, Tuple


def check_files(files: List[str]) -> List[str]:
    """Проверяет существование файлов и возвращает список отсутствующих."""
    missing_files = []
    for file in files:
        if not Path(file).exists():
            missing_files.append(file)
    return missing_files


def write_handlers_report(stats: Dict[str, Dict[str, int]], output_file: str = "report_han.txt") -> None:
    """Формирует и сохраняет отчет по обработчикам в виде таблицы."""
    handlers = sorted([h for h in stats.keys() if h != "Total requests"])

    max_handler_len = max(len(h) for h in handlers) if handlers else 20
    max_handler_len = max(max_handler_len, len("HANDLER"))

    header = f"{'HANDLER':<{max_handler_len}}   DEBUG   INFO    WARNING ERROR   CRITICAL"
    separator = "-" * (max_handler_len + 40)

    lines = [
        f"Total requests: {stats['Total requests']}",
        "",
        header,
        separator
    ]

    totals = {
        'DEBUG': 0,
        'INFO': 0,
        'WARNING': 0,
        'ERROR': 0,
        'CRITICAL': 0
    }

    for handler in handlers:
        data = stats[handler]
        line = (
            f"{handler:<{max_handler_len}}   "
            f"{data['DEBUG']:>6}   "
            f"{data['INFO']:>6}   "
            f"{data['WARNING']:>7}   "
            f"{data['ERROR']:>6}   "
            f"{data['CRITICAL']:>8}"
        )
        lines.append(line)

        for level in totals:
            totals[level] += data[level]

    total_line = (
        f"{'TOTAL':<{max_handler_len}}   "
        f"{totals['DEBUG']:>6}   "
        f"{totals['INFO']:>6}   "
        f"{totals['WARNING']:>7}   "
        f"{totals['ERROR']:>6}   "
        f"{totals['CRITICAL']:>8}"
    )
    lines.append(separator)
    lines.append(total_line)

    print("\n".join(lines))

    with open(output_file, 'w') as f:
        f.write("\n".join(lines))


def parse_log_line(line: str, patterns: Tuple[Pattern[str], Pattern[str], Pattern[str]]) -> Optional[Tuple[str, str]]:
    """Парсит строку лога и возвращает уровень и обработчик, если применимо."""
    log_pattern, success_pattern, error_pattern = patterns
    match = log_pattern.match(line.strip())
    if not match:
        return None

    level = match.group('level')
    logger = match.group('logger')
    message = match.group('message')

    if logger != 'django.request':
        return None

    handler = None
    if level == 'INFO':
        handler_match = success_pattern.search(message)
        if handler_match:
            handler = handler_match.group("handler")
    elif level == 'ERROR':
        handler_match = error_pattern.search(message)
        if handler_match:
            handler = handler_match.group("handler")

    return (level, handler) if handler else None


def parse_logs(files: List[str]) -> Dict[str, Dict[str, int]]:
    """Анализирует логи и возвращает статистику по обработчикам."""
    stats = {"Total requests": 0}

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
    patterns = (log_pattern, success_pattern, error_pattern)

    for file in files:
        with open(file, 'r') as f:
            for line in f:
                result = parse_log_line(line, patterns)
                if not result:
                    continue

                level, handler = result
                stats["Total requests"] += 1
                handler = handler.split('?')[0]

                if handler not in stats:
                    stats[handler] = {
                        "DEBUG": 0,
                        "INFO": 0,
                        "WARNING": 0,
                        "ERROR": 0,
                        "CRITICAL": 0,
                    }

                stats[handler][level] += 1

    return stats


def main() -> None:
    """Основная функция для обработки аргументов командной строки и запуска анализа."""
    parser = argparse.ArgumentParser(description='Анализатор логов Django')
    parser.add_argument(
        'log_files',
        nargs='+',
        help='Файлы логов для анализа'
    )
    parser.add_argument(
        '--report',
        choices=['handlers'],
        default='handlers',
        help='Тип отчета (по умолчанию: handlers)'
    )

    args = parser.parse_args()
    missing = check_files(args.log_files)
    if missing:
        print(f"Ошибка: файлы не найдены: {', '.join(missing)}")
        return

    result = parse_logs(args.log_files)
    write_handlers_report(result)


if __name__ == '__main__':
    main()