"""Provider-neutral visual look and palette contracts."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping
from .contracts import ID_RE
from .report import ValidationIssue, ValidationReport
from .script_analysis import _extensions, _load_mapping, _unknown

_ROOT = {"schema_version","look_id","scope","reference_sources","composition_language","camera_behavior","palette","contrast","saturation","color_temperature","light_direction","light_quality","weather","skin_tone_protection","does_not_control","review_status","extensions"}
_SOURCE = {"source_id","description","rights_status","extensions"}
@dataclass(frozen=True)
class LookBible:
    look_id: str; scope: str; raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)
    def to_dict(self) -> dict[str, Any]: return dict(self.raw)
def parse_look_bible(value: str | Path | Mapping[str, Any]) -> LookBible:
    if isinstance(value, LookBible): return value
    p = _load_mapping(value, "look bible"); return LookBible(str(p.get("look_id", "")), str(p.get("scope", "")), dict(p))
def validate_look_bible(value: LookBible | Mapping[str, Any], *, source: str = "") -> ValidationReport:
    d = value.to_dict() if isinstance(value, LookBible) else value; issue=lambda c,m,p: ValidationIssue("ERROR",c,m,source=source,json_pointer=p)
    if not isinstance(d, Mapping): return ValidationReport("look_bible",[],[issue("INVALID_TYPE","look bible: top-level object required","")])
    issues=_unknown(d,_ROOT,"",source)
    if d.get("schema_version")!="look-bible.v2": issues.append(issue("INVALID_SCHEMA_VERSION","schema_version: expected look-bible.v2","/schema_version"))
    if not isinstance(d.get("look_id"),str) or not ID_RE.fullmatch(d["look_id"]): issues.append(issue("INVALID_ID","/look_id: stable ASCII ID required","/look_id"))
    for n in ("scope","composition_language","camera_behavior","contrast","saturation","color_temperature","light_direction","light_quality","weather","skin_tone_protection","does_not_control","review_status"):
        if not isinstance(d.get(n),str) or not d[n].strip(): issues.append(issue("REQUIRED_FIELD",f"/{n}: non-empty string required",f"/{n}"))
    if not isinstance(d.get("palette"),list) or any(not isinstance(x,str) or not x.strip() for x in d.get("palette",[])): issues.append(issue("INVALID_TYPE","/palette: list of non-empty strings required","/palette"))
    sources=d.get("reference_sources")
    if not isinstance(sources,list): issues.append(issue("INVALID_TYPE","/reference_sources: list required","/reference_sources")); sources=[]
    for i,s in enumerate(sources):
        p=f"/reference_sources/{i}"; 
        if not isinstance(s,Mapping): issues.append(issue("INVALID_TYPE",f"{p}: object required",p)); continue
        issues.extend(_unknown(s,_SOURCE,p,source))
        for n in ("source_id","description","rights_status"):
            if not isinstance(s.get(n),str) or not s[n].strip(): issues.append(issue("REQUIRED_FIELD",f"{p}/{n}: non-empty string required",f"{p}/{n}"))
        issues.extend(_extensions(s.get("extensions"),f"{p}/extensions",source))
    issues.extend(_extensions(d.get("extensions"),"/extensions",source)); return ValidationReport("look_bible",[source] if source else [],issues)
__all__=["LookBible","parse_look_bible","validate_look_bible"]
