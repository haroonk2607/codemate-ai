import argparse
import csv
import json
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


@dataclass
class ScraperConfig:
    base_url_template: str
    start_id: int
    end_id: int
    set_size: int
    export_size: int
    output_dir: Path
    headers: dict[str, str]
    cookies: dict[str, str]
    timeout_seconds: int
    min_delay_seconds: float
    max_delay_seconds: float
    max_retries: int
    retry_backoff_seconds: int
    css_selectors: dict[str, str]
    include_html: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape QBankly question pages in strict sequence with chunked exports."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Absolute path to JSON config file (see qbankly_scraper_config.example.json).",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> ScraperConfig:
    with config_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    return ScraperConfig(
        base_url_template=raw["base_url_template"],
        start_id=int(raw.get("start_id", 30000)),
        end_id=int(raw.get("end_id", 140000)),
        set_size=int(raw.get("set_size", 10000)),
        export_size=int(raw.get("export_size", 20000)),
        output_dir=Path(raw.get("output_dir", "exports/qbankly")).resolve(),
        headers=dict(raw.get("headers", {})),
        cookies=dict(raw.get("cookies", {})),
        timeout_seconds=int(raw.get("timeout_seconds", 30)),
        min_delay_seconds=float(raw.get("min_delay_seconds", 0.1)),
        max_delay_seconds=float(raw.get("max_delay_seconds", 0.4)),
        max_retries=int(raw.get("max_retries", 8)),
        retry_backoff_seconds=int(raw.get("retry_backoff_seconds", 30)),
        css_selectors=dict(raw.get("css_selectors", {})),
        include_html=bool(raw.get("include_html", False)),
    )


def create_session(config: ScraperConfig) -> requests.Session:
    session = requests.Session()
    if config.headers:
        session.headers.update(config.headers)
    if config.cookies:
        session.cookies.update(config.cookies)
    return session


def extract_fields(html: str, selectors: dict[str, str], include_html: bool) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    extracted: dict[str, Any] = {}

    for field_name, selector in selectors.items():
        if not selector:
            extracted[field_name] = ""
            continue
        node = soup.select_one(selector)
        extracted[field_name] = node.get_text(" ", strip=True) if node else ""

    if include_html:
        extracted["raw_html"] = html

    return extracted


def fetch_with_retries(
    session: requests.Session, question_id: int, config: ScraperConfig
) -> tuple[int, str, dict[str, Any], str]:
    url = config.base_url_template.format(question_id=question_id)
    backoff = config.retry_backoff_seconds

    for attempt in range(1, config.max_retries + 1):
        try:
            response = session.get(url, timeout=config.timeout_seconds)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                wait_time = int(retry_after) if retry_after and retry_after.isdigit() else backoff
                wait_time = int(wait_time + random.uniform(0, max(1, wait_time * 0.2)))
                time.sleep(wait_time)
                backoff = min(backoff * 2, 1800)
                continue

            if response.status_code == 404:
                return response.status_code, url, {}, "missing"

            if response.status_code >= 500:
                time.sleep(backoff + random.uniform(0, 2))
                backoff = min(backoff * 2, 1800)
                continue

            response.raise_for_status()
            data = extract_fields(response.text, config.css_selectors, config.include_html)
            return response.status_code, url, data, "ok"

        except requests.RequestException as error:
            if attempt == config.max_retries:
                return 0, url, {"error": str(error)}, "failed"
            time.sleep(backoff + random.uniform(0, 2))
            backoff = min(backoff * 2, 1800)

    return 0, url, {"error": "unreachable retry state"}, "failed"


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["sequence_index", "question_id", "status", "source_url", "fetched_at", "payload_json"]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "sequence_index": row["sequence_index"],
                    "question_id": row["question_id"],
                    "status": row["status"],
                    "source_url": row["source_url"],
                    "fetched_at": row["fetched_at"],
                    "payload_json": json.dumps(row["payload"], ensure_ascii=False),
                }
            )


def export_chunk(output_dir: Path, chunk_index: int, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    first_id = rows[0]["question_id"]
    last_id = rows[-1]["question_id"]
    chunk_dir = output_dir / f"export_{chunk_index:03d}_{first_id}_{last_id}"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(chunk_dir / "questions.jsonl", rows)
    write_csv(chunk_dir / "questions.csv", rows)


def write_checkpoint(path: Path, checkpoint: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(checkpoint, file, indent=2)


def run(config: ScraperConfig) -> None:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = config.output_dir / "checkpoint.json"
    run_log_path = config.output_dir / "run_summary.json"

    session = create_session(config)

    sequence_index = 1
    export_chunk_index = 1
    buffer_rows: list[dict[str, Any]] = []
    set_summaries: list[dict[str, Any]] = []

    total_ids = config.end_id - config.start_id + 1
    if total_ids <= 0:
        raise ValueError("end_id must be >= start_id")

    for set_start in range(config.start_id, config.end_id + 1, config.set_size):
        set_end = min(set_start + config.set_size - 1, config.end_id)
        set_stats = {"set_start": set_start, "set_end": set_end, "ok": 0, "missing": 0, "failed": 0}

        for question_id in range(set_start, set_end + 1):
            status_code, url, payload, status = fetch_with_retries(session, question_id, config)

            row = {
                "sequence_index": sequence_index,
                "question_id": question_id,
                "status": status,
                "http_status": status_code,
                "source_url": url,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "payload": payload,
            }

            buffer_rows.append(row)
            set_stats[status] += 1
            sequence_index += 1

            write_checkpoint(
                checkpoint_path,
                {
                    "last_sequence_index": row["sequence_index"],
                    "last_question_id": question_id,
                    "active_set": {"start": set_start, "end": set_end},
                    "counts": set_stats,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            if len(buffer_rows) >= config.export_size:
                export_chunk(config.output_dir, export_chunk_index, buffer_rows[: config.export_size])
                buffer_rows = buffer_rows[config.export_size :]
                export_chunk_index += 1

            time.sleep(random.uniform(config.min_delay_seconds, config.max_delay_seconds))

        set_summaries.append(set_stats)

    if buffer_rows:
        export_chunk(config.output_dir, export_chunk_index, buffer_rows)

    run_summary = {
        "range": {"start_id": config.start_id, "end_id": config.end_id},
        "set_size": config.set_size,
        "export_size": config.export_size,
        "total_expected": total_ids,
        "sets": set_summaries,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }

    with run_log_path.open("w", encoding="utf-8") as file:
        json.dump(run_summary, file, indent=2)


def main() -> None:
    args = parse_args()
    config = load_config(Path(args.config).resolve())
    run(config)


if __name__ == "__main__":
    main()
