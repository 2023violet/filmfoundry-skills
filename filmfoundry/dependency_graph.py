"""Asset dependency graph with explicit relation semantics."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping
from .contracts import ID_RE
from .report import ValidationIssue, ValidationReport
from .script_analysis import _extensions, _load_mapping, _unknown

_ROOT={"schema_version","graph_id","nodes","edges","extensions"}; _EDGE={"source","target","relation","extensions"}; _RELATIONS={"DEPENDS_ON_APPROVAL","STATE_VARIANT_OF","DERIVED_FROM","RESEMBLANCE_TARGET","NARRATIVE_RELATION","RECURS_IN","MUST_PRECEDE"}
@dataclass(frozen=True)
class DependencyGraph:
    graph_id:str; nodes:tuple[str,...]=(); edges:tuple[Mapping[str,Any],...]=(); raw:Mapping[str,Any]=field(default_factory=dict,repr=False,compare=False)
    def to_dict(self)->dict[str,Any]: return dict(self.raw)
def parse_dependency_graph(value:str|Path|Mapping[str,Any])->DependencyGraph:
    if isinstance(value,DependencyGraph): return value
    p=_load_mapping(value,"asset dependency graph"); return DependencyGraph(str(p.get("graph_id","")),tuple(str(x) for x in p.get("nodes",()) if isinstance(x,str)),tuple(dict(x) for x in p.get("edges",()) if isinstance(x,Mapping)),dict(p))
def validate_dependency_graph(value:DependencyGraph|Mapping[str,Any],*,source:str="")->ValidationReport:
    d=value.to_dict() if isinstance(value,DependencyGraph) else value; issue=lambda c,m,p:ValidationIssue("ERROR",c,m,source=source,json_pointer=p)
    if not isinstance(d,Mapping): return ValidationReport("dependency_graph",[],[issue("INVALID_TYPE","dependency graph: top-level object required","")])
    issues=_unknown(d,_ROOT,"",source)
    if d.get("schema_version")!="asset-dependency-graph.v3": issues.append(issue("INVALID_SCHEMA_VERSION","schema_version: expected asset-dependency-graph.v3","/schema_version"))
    if not isinstance(d.get("graph_id"),str) or not ID_RE.fullmatch(d["graph_id"]): issues.append(issue("INVALID_ID","/graph_id: stable ASCII ID required","/graph_id"))
    nodes=d.get("nodes"); node_set=set(nodes) if isinstance(nodes,list) else set()
    if not isinstance(nodes,list) or any(not isinstance(x,str) or not ID_RE.fullmatch(x) for x in nodes): issues.append(issue("INVALID_NODES","/nodes: stable ASCII IDs required","/nodes"))
    if isinstance(nodes,list) and len(node_set)!=len(nodes): issues.append(issue("DUPLICATE_ID","/nodes: duplicate node ID","/nodes"))
    edges=d.get("edges")
    if not isinstance(edges,list): issues.append(issue("INVALID_TYPE","/edges: list required","/edges")); edges=[]
    seen=set()
    for i,e in enumerate(edges):
        p=f"/edges/{i}"
        if not isinstance(e,Mapping): issues.append(issue("INVALID_TYPE",f"{p}: object required",p)); continue
        issues.extend(_unknown(e,_EDGE,p,source)); key=(e.get("source"),e.get("target"),e.get("relation"))
        if key in seen: issues.append(issue("DUPLICATE_EDGE",f"{p}: duplicate edge",p))
        seen.add(key)
        for n in ("source","target"):
            if not isinstance(e.get(n),str) or e[n] not in node_set: issues.append(issue("UNKNOWN_NODE",f"{p}/{n}: node must exist",f"{p}/{n}"))
        if e.get("relation") not in _RELATIONS: issues.append(issue("INVALID_RELATION",f"{p}/relation: unsupported relation",f"{p}/relation"))
        issues.extend(_extensions(e.get("extensions"),f"{p}/extensions",source))
    issues.extend(_extensions(d.get("extensions"),"/extensions",source)); return ValidationReport("dependency_graph",[source] if source else [],issues)
def build_dependency_graph(value:Mapping[str,Any])->DependencyGraph: return parse_dependency_graph(value)
__all__=["DependencyGraph","parse_dependency_graph","validate_dependency_graph","build_dependency_graph"]
