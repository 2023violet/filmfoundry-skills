from __future__ import annotations
from filmfoundry_v2 import parse_scene_topology, validate_scene_topology, parse_location_coverage, validate_location_coverage

def topology():
    return {"schema_version":"scene-topology.v2","topology_id":"TOPO_INN","location_id":"LOC_INN","nodes":[{"node_id":"NODE_DOOR","node_type":"ROOM","adjacent_nodes":[],"entrances":[],"exits":[],"floor":"GROUND","elevation":"0","orientation":"north","anchor_ids":["ANCHOR_LAMP"],"light_sources":["LAMP"],"camera_side_regions":["NORTH"]}],"movement_paths":[],"review_status":"REVIEWED"}

def coverage():
    return {"schema_version":"location-coverage-set.v2","coverage_id":"COVER_INN","location_id":"LOC_INN","views":[{"view_id":"VIEW_INN_A","node_id":"NODE_DOOR","camera_side":"NORTH","screen_direction":"left-to-right","visible_anchor_ids":["ANCHOR_LAMP"],"occluded_anchor_ids":[],"framing_result":"door and lamp readable","source_asset_id":"ASSET_INN_A","qc_status":"PASS"}],"review_status":"REVIEWED"}

def test_topology_and_coverage_parse_and_validate():
    assert validate_scene_topology(parse_scene_topology(topology())).ok
    assert validate_location_coverage(parse_location_coverage(coverage())).ok

def test_topology_rejects_unknown_path_node_and_coverage_duplicate_view():
    value = topology(); value["movement_paths"] = [{"path_id":"PATH_A","subject_id":"CHAR_A","node_ids":["NODE_DOOR","NODE_MISSING"],"anchor_ids":[],"screen_direction":"right"}]
    assert any(issue.code == "UNKNOWN_NODE" for issue in validate_scene_topology(value).errors)
    value = coverage(); value["views"].append(dict(value["views"][0])); assert any(issue.code == "DUPLICATE_ID" for issue in validate_location_coverage(value).errors)

def test_character_reference_package_schema_is_present():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    assert (root / "schemas" / "character-reference-package.v2.json").is_file()
