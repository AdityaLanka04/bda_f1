from csie.nl_parser.query_parser import parse_query


def test_parse_query():
    q = "If car 16 pits on lap 14 for soft"
    inter = parse_query(q)
    assert inter.car == "16"
    assert inter.lap == 14
