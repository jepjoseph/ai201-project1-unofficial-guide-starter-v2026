"""Read-only historical Unit 9 evaluation report access."""

import json
import re
from pathlib import Path

import config


REPORT_NAME = re.compile(
    r"unit9_compare_\d{8}-\d{6}-\d+\.json"
)


def _root() -> Path:
    return Path(config.RESULTS_DIR).resolve()


def _validate(data):
    if not isinstance(data, dict):
        raise ValueError("Report must be a JSON object.")

    if not isinstance(data.get("metadata"), dict):
        raise ValueError("Missing report metadata.")

    if not isinstance(data.get("summary"), list):
        raise ValueError("Missing report summary.")

    if not isinstance(data.get("records"), list):
        raise ValueError("Missing report records.")

    summary_fields = {
        "mode",
        "scope",
        "trials",
        "mean_ms",
        "median_ms",
        "gate_correct",
        "expected_source_top1",
        "expected_source_topk",
    }

    record_fields = {
        "mode",
        "scope",
        "trial",
        "question",
        "duration_ms",
        "gate_correct",
        "expected_source_top1",
        "expected_source_topk",
    }

    for row in data["summary"]:
        if (
            not isinstance(row, dict)
            or not summary_fields <= row.keys()
        ):
            raise ValueError("Invalid summary row.")

    for row in data["records"]:
        if (
            not isinstance(row, dict)
            or not record_fields <= row.keys()
        ):
            raise ValueError("Invalid trial record.")

    return data


def _read(path: Path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("Invalid report file.")

    if path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError("Report exceeds the size limit.")

    with path.open("r", encoding="utf-8") as handle:
        return _validate(json.load(handle))


def list_reports():
    root = _root()

    if not root.is_dir():
        return []

    reports = []

    for path in sorted(
        root.glob("unit9_compare_*.json"),
        reverse=True,
    ):
        if not REPORT_NAME.fullmatch(path.name):
            continue

        try:
            data = _read(path)
        except (OSError, ValueError, UnicodeError):
            continue

        reports.append({
            "id": path.name,
            "metadata": data["metadata"],
            "summary_count": len(data["summary"]),
            "record_count": len(data["records"]),
        })

    return reports


def get_report(report_id: str):
    if not REPORT_NAME.fullmatch(report_id):
        raise ValueError("Invalid report identifier.")

    path = _root() / report_id

    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError("Report not found.")

    return _read(path)