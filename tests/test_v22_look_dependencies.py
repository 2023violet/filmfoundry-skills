from filmfoundry_v2 import parse_look_bible, validate_look_bible, parse_dependency_graph, validate_dependency_graph

def look(): return {"schema_version":"look-bible.v2","look_id":"LOOK_NIGHT","scope":"season","reference_sources":[{"source_id":"SRC_01","description":"low-key night reference","rights_status":"internal"}],"composition_language":"anchored depth","camera_behavior":"slow deliberate moves","palette":["blue-black","lantern amber"],"contrast":"high","saturation":"muted","color_temperature":"cool with warm practicals","light_direction":"side and back","light_quality":"soft haze","weather":"mist","skin_tone_protection":"keep faces readable","does_not_control":"dialogue or provider behavior","review_status":"REVIEWED"}
def graph(): return {"schema_version":"asset-dependency-graph.v2","graph_id":"GRAPH_CHAR","nodes":["CHAR_PARENT","CHAR_CHILD"],"edges":[{"source":"CHAR_CHILD","target":"CHAR_PARENT","relation":"DEPENDS_ON_APPROVAL"}]}
def test_look_and_dependency_parse_validate(): assert validate_look_bible(parse_look_bible(look())).ok and validate_dependency_graph(parse_dependency_graph(graph())).ok
def test_dependency_rejects_unknown_node_and_relation():
    p=graph(); p["edges"][0]["target"]="MISSING"; p["edges"][0]["relation"]="MADE_UP"; r=validate_dependency_graph(p); assert {i.code for i in r.errors}>={"UNKNOWN_NODE","INVALID_RELATION"}
def test_look_rejects_unknown_field(): p=look(); p["movie_title"]="Reference"; assert any(i.code=="UNKNOWN_FIELD" for i in validate_look_bible(p).errors)
