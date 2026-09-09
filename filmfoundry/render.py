"""Deterministic static Creator Dashboard renderers."""
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
    if value is None or value == "":
        return "UNKNOWN"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _rows(values: Iterable[dict[str, Any]], columns: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    return tuple(tuple(_value(item.get(column)) for column in columns) for item in values)


def _provenance_label(item: dict[str, Any]) -> str:
    provenance = item.get("provenance")
    refs = provenance.get("source_refs") if isinstance(provenance, dict) else None
    if not isinstance(refs, list):
        return "UNKNOWN"
    return ", ".join(str(ref.get("source_id", "UNKNOWN")) for ref in refs if isinstance(ref, dict)) or "UNKNOWN"


def _views(model: CreatorReadModel) -> tuple[_View, ...]:
    data = model.to_dict()
    snapshot = data["snapshot"]
    navigation = data["navigation"]
    overview = snapshot["overview"]
    metrics = snapshot["metrics"]
    asset_rows = tuple(
        (_value(item.get("asset_id")), _value(item.get("asset_type")), _value(item.get("declared_state")), _value(item.get("observed_readiness")), _value(item.get("path")), _provenance_label(item))
        for item in snapshot.get("assets", [])
    )
    shot_rows = tuple(
        (_value(item.get("shot_id")), _value(item.get("generation_unit_id")), _value(item.get("runtime_status")), _value(item.get("historical_runtime_status")), _value(item.get("select_type")), _value(item.get("observed_state")))
        for item in snapshot.get("shots", [])
    )
    return (
        _View("overview", "Creator Overview", ("field", "value"), tuple((key, _value(overview.get(key))) for key in ("project_id", "phase", "current_authority", "historical_authority")) + tuple((str(metric.get("metric_id")), _value(metric.get("value"))) for metric in metrics) + (("blockers", str(len(snapshot.get("blockers", [])))), ("warnings", str(sum(1 for blocker in snapshot.get("blockers", []) if blocker.get("severity") == "WARNING"))), ("primary_action", _value((navigation.get("primary_action") or {}).get("action_id")))),),
        _View("emotional-map", "Emotional Map", ("point_id", "production_unit", "emotion", "tension", "direction"), _rows(snapshot.get("emotion_points", []), ("beat_id", "production_unit", "primary_emotion", "tension_level", "direction"))),
        _View("story-map", "Story Map", ("node_id", "node_type", "display_name", "responsibility", "canon_source"), _rows(snapshot.get("narrative_nodes", []), ("node_id", "node_type", "display_name", "narrative_responsibility", "canon_source"))),
        _View("assets", "Assets", ("asset_id", "type", "declared_state", "observed_readiness", "path", "provenance"), asset_rows),
        _View("shots", "Shots", ("shot_id", "generation_unit_id", "current_status", "historical_status", "select_type", "observed_state"), shot_rows),
        _View("continuity", "Continuity", ("from_shot_id", "to_shot_id", "field", "from_value", "to_value"), _rows(snapshot.get("continuity_edges", []), ("from_shot_id", "to_shot_id", "field", "from_value", "to_value"))),
    )


def _markdown(view: _View) -> str:
    lines = [f"# {view.title}", "", "| " + " | ".join(view.columns) + " |", "| " + " | ".join("---" for _ in view.columns) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in view.rows)
    return "\n".join(lines) + "\n"


def _safe_media_href(value: str) -> str | None:
    normalized = value.replace("\\", "/")
    path = Path(normalized)
    windows = PureWindowsPath(value)
    if not value or value == "UNKNOWN" or path.is_absolute() or windows.drive or windows.is_absolute() or any(part in {"", ".", ".."} for part in normalized.split("/")):
        return None
    return quote(normalized, safe="/._-~")


_HTML_CSS = """
:root { color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; background: #f4f6f8; color: #17202a; }
* { box-sizing: border-box; } body { margin: 0; } header { background: #17202a; color: #fff; padding: 18px clamp(16px, 4vw, 48px); }
header h1 { margin: 0 0 6px; font-size: 22px; } header p { margin: 0; color: #c8d1da; font-size: 13px; }
nav { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; } nav a { color: #e6edf3; border: 1px solid #536170; border-radius: 4px; padding: 6px 9px; text-decoration: none; font-size: 12px; }
nav a[aria-current="page"] { background: #dceeff; color: #17202a; border-color: #dceeff; } main { max-width: 1440px; margin: 0 auto; padding: 22px clamp(16px, 4vw, 48px); }
.status { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 18px; } .tag { border-radius: 4px; padding: 5px 8px; font-size: 12px; background: #e6edf3; }
.tag.warning { background: #fff1c2; color: #704d00; } .tag.blocker { background: #ffd9d6; color: #8a1c15; } .table-wrap { overflow-x: auto; background: #fff; border: 1px solid #d9e0e7; border-radius: 6px; }
table { width: 100%; border-collapse: collapse; min-width: 620px; } th, td { text-align: left; vertical-align: top; padding: 10px 12px; border-bottom: 1px solid #edf0f2; font-size: 13px; }
th { background: #f8fafb; color: #4a5968; font-weight: 600; position: sticky; top: 0; } tr:last-child td { border-bottom: 0; } a.media { color: #075985; }
@media (max-width: 600px) { header h1 { font-size: 19px; } main { padding: 16px; } th, td { padding: 8px; } }
""".strip()


def _html(view: _View, project_id: str, data_status: str, warning_count: int, blocker_count: int) -> str:
    headers = "".join(f"<th>{html.escape(column)}</th>" for column in view.columns)
    rows: list[str] = []
    for row in view.rows:
        cells: list[str] = []
        for index, value in enumerate(row):
            href = _safe_media_href(value) if view.name == "assets" and view.columns[index] == "path" else None
            rendered = f'<a class="media" href="{html.escape(href, quote=True)}">{html.escape(value)}</a>' if href else html.escape(value)
            cells.append(f"<td>{rendered}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    nav = "".join(f'<a href="{name}.html" aria-current="page">{html.escape(name.replace("-", " ").title())}</a>' if name == view.name else f'<a href="{name}.html">{html.escape(name.replace("-", " ").title())}</a>' for name in VIEW_NAMES)
    tags = f'<span class="tag">DATA {html.escape(data_status)}</span><span class="tag warning">WARNINGS {warning_count}</span><span class="tag blocker">BLOCKERS {blocker_count}</span>'
    return f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(view.title)}</title><style>{_HTML_CSS}</style></head><body><header><h1>FilmFoundry Creator Dashboard</h1><p>{html.escape(project_id)} · current and historical authority remain distinct</p><nav>{nav}</nav></header><main><div class="status">{tags}</div><h2>{html.escape(view.title)}</h2><div class="table-wrap"><table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table></div></main></body></html>\n'


def _svg(view: _View) -> str:
    width = max(640, len(view.columns) * 150)
    height = max(120, 70 + len(view.rows) * 28)
    text = [f'<text x="24" y="30" font-size="18" font-family="sans-serif">{html.escape(view.title)}</text>']
    for row_index, row in enumerate((view.columns, *view.rows)):
        y = 58 + row_index * 26
        for column_index, value in enumerate(row):
            text.append(f'<text x="{24 + column_index * 150}" y="{y}" font-size="12" font-family="sans-serif">{html.escape(value)}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">' + "".join(text) + "</svg>\n"


def _status(model: CreatorReadModel) -> tuple[str, list[str], list[str], dict[str, int]]:
    data = model.to_dict()
    snapshot = data["snapshot"]
    statuses = [str(item.get("data_status", "UNKNOWN")) for item in (*snapshot.get("metrics", []), *snapshot.get("coverage", []))]
    data_status = "INVALID" if "INVALID" in statuses else "UNKNOWN" if "UNKNOWN" in statuses else "KNOWN"
    warnings = [f"{item.get('blocker_id', 'UNKNOWN')}: {item.get('reason', 'warning')}" for item in snapshot.get("blockers", []) if item.get("severity") == "WARNING"]
    blockers = [f"{item.get('blocker_id', 'UNKNOWN')}: {item.get('reason', 'blocker')}" for item in snapshot.get("blockers", []) if item.get("severity") in {"CRITICAL", "ERROR", "BLOCKER"}]
    source_summary: dict[str, int] = {}
    for item in snapshot.get("coverage", []):
        source_summary[str(item.get("source_kind"))] = source_summary.get(str(item.get("source_kind")), 0) + int(item.get("successful_sources", 0))
    return data_status, warnings, blockers, source_summary


def render_read_model(model: CreatorReadModel, output_dir: Path, *, formats: tuple[str, ...] = FORMAT_NAMES) -> dict[str, Any]:
    selected = tuple(formats)
    if not selected or any(fmt not in FORMAT_NAMES for fmt in selected) or len(set(selected)) != len(selected):
        raise ValueError(f"formats must be a unique subset of {FORMAT_NAMES}")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_status, warnings, blockers, source_summary = _status(model)
    artifacts: list[dict[str, str]] = []
    for view in _views(model):
        rendered = {"html": _html(view, model.snapshot.project_id, data_status, len(warnings), len(blockers)), "markdown": _markdown(view), "svg": _svg(view)}
        for fmt in selected:
            path = output_dir / f"{view.name}.{fmt if fmt != 'markdown' else 'md'}"
            content = rendered[fmt]
            path.write_text(content, encoding="utf-8", newline="\n")
            artifacts.append({"view": view.name, "format": fmt, "path": path.name, "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()})
    manifest = {
        "schema_version": "render-manifest.v2",
        "project_id": model.snapshot.project_id,
        "views": list(VIEW_NAMES),
        "formats": list(selected),
        "artifacts": artifacts,
        "coverage": model.to_dict()["snapshot"].get("coverage", []),
        "warnings": warnings,
        "blockers": blockers,
        "data_status": data_status,
        "source_summary": source_summary,
    }
    (output_dir / "render-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


__all__ = ["FORMAT_NAMES", "VIEW_NAMES", "render_read_model"]
