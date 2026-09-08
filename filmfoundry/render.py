"""Deterministic, provider-neutral renderers for the Creator Read Model."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import html
import json
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable
from urllib.parse import quote

from .creator_read_model import CreatorReadModel


VIEW_NAMES = ("overview", "emotional-map", "story-map", "assets", "shots", "continuity")
FORMAT_NAMES = ("html", "markdown", "svg")


@dataclass(frozen=True)
class _View:
    name: str
    title: str
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


def _value(value: object) -> str:
    if value is None:
        return "UNKNOWN"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _rows(values: Iterable[dict[str, Any]], columns: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    return tuple(tuple(_value(item.get(column)) for column in columns) for item in values)


def _views(model: CreatorReadModel) -> tuple[_View, ...]:
    data = model.to_dict()
    snapshot = data["snapshot"]
    navigation = data["navigation"]
    overview = snapshot["overview"]
    metrics = snapshot["metrics"]
    return (
        _View(
            "overview",
            "Creator Overview",
            ("field", "value"),
            tuple((key, _value(overview.get(key))) for key in ("project_id", "phase", "current_authority", "historical_authority"))
            + tuple((str(metric.get("metric_id")), _value(metric.get("value"))) for metric in metrics)
            + (("primary_action", _value((navigation.get("primary_action") or {}).get("action_id"))),),
        ),
        _View(
            "emotional-map",
            "Emotional Map",
            ("point_id", "node_id", "emotion", "intensity", "status"),
            _rows(snapshot.get("emotion_points", []), ("point_id", "node_id", "emotion", "intensity", "data_status")),
        ),
        _View(
            "story-map",
            "Story Map",
            ("node_id", "node_type", "display_name", "responsibility", "canon_source"),
            _rows(snapshot.get("narrative_nodes", []), ("node_id", "node_type", "display_name", "narrative_responsibility", "canon_source")),
        ),
        _View(
            "assets",
            "Assets",
            ("asset_id", "type", "state", "readiness", "path"),
            _rows(snapshot.get("assets", []), ("asset_id", "asset_type", "declared_state", "observed_readiness", "path")),
        ),
        _View(
            "shots",
            "Shots",
            ("shot_id", "generation_unit_id", "runtime_status", "select_type", "observed_state"),
            _rows(snapshot.get("shots", []), ("shot_id", "generation_unit_id", "runtime_status", "select_type", "observed_state")),
        ),
        _View(
            "continuity",
            "Continuity",
            ("from_shot_id", "to_shot_id", "field", "from_value", "to_value"),
            _rows(snapshot.get("continuity_edges", []), ("from_shot_id", "to_shot_id", "field", "from_value", "to_value")),
        ),
    )


def _markdown(view: _View) -> str:
    lines = [f"# {view.title}", "", "| " + " | ".join(view.columns) + " |", "| " + " | ".join("---" for _ in view.columns) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in view.rows)
    return "\n".join(lines) + "\n"


def _html(view: _View) -> str:
    headers = "".join(f"<th>{html.escape(column)}</th>" for column in view.columns)
    cells: list[str] = []
    for row in view.rows:
        row_cells: list[str] = []
        for index, value in enumerate(row):
            safe_href = _safe_media_href(value) if view.name == "assets" and view.columns[index] == "path" else None
            rendered = f'<a href="{html.escape(safe_href, quote=True)}">{html.escape(value)}</a>' if safe_href else html.escape(value)
            row_cells.append(f"<td>{rendered}</td>")
        cells.append("<tr>" + "".join(row_cells) + "</tr>")
    rows = "".join(cells)
    return "<!doctype html>\n<html lang=\"en\"><meta charset=\"utf-8\"><title>" + html.escape(view.title) + "</title><main><h1>" + html.escape(view.title) + f"</h1><table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></main></html>\n"


def _safe_media_href(value: str) -> str | None:
    normalized = value.replace("\\", "/")
    path = Path(normalized)
    windows = PureWindowsPath(value)
    if not value or value == "UNKNOWN" or path.is_absolute() or windows.drive or windows.is_absolute() or any(part in {"", ".", ".."} for part in normalized.split("/")):
        return None
    return quote(normalized, safe="/._-~")


def _svg(view: _View) -> str:
    width = max(640, len(view.columns) * 150)
    height = max(120, 70 + len(view.rows) * 28)
    text = [f'<text x="24" y="30" font-size="18" font-family="sans-serif">{html.escape(view.title)}</text>']
    for row_index, row in enumerate((view.columns, *view.rows)):
        y = 58 + row_index * 26
        for column_index, value in enumerate(row):
            text.append(f'<text x="{24 + column_index * 150}" y="{y}" font-size="12" font-family="sans-serif">{html.escape(value)}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">' + "".join(text) + "</svg>\n"


def render_read_model(model: CreatorReadModel, output_dir: Path, *, formats: tuple[str, ...] = FORMAT_NAMES) -> dict[str, Any]:
    selected = tuple(formats)
    if not selected or any(fmt not in FORMAT_NAMES for fmt in selected) or len(set(selected)) != len(selected):
        raise ValueError(f"formats must be a unique subset of {FORMAT_NAMES}")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts: list[dict[str, str]] = []
    for view in _views(model):
        rendered = {"html": _html(view), "markdown": _markdown(view), "svg": _svg(view)}
        for fmt in selected:
            path = output_dir / f"{view.name}.{fmt if fmt != 'markdown' else 'md'}"
            content = rendered[fmt]
            path.write_text(content, encoding="utf-8", newline="\n")
            artifacts.append({"view": view.name, "format": fmt, "path": path.name, "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()})
    manifest = {
        "schema_version": "render-manifest.v1",
        "project_id": model.snapshot.project_id,
        "views": list(VIEW_NAMES),
        "formats": list(selected),
        "artifacts": artifacts,
        "warnings": [],
    }
    (output_dir / "render-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


__all__ = ["FORMAT_NAMES", "VIEW_NAMES", "render_read_model"]
