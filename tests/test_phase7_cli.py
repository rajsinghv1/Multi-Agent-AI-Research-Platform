from app import phase7_cli


def test_cli_history_function_exists():
    assert callable(phase7_cli.show_history)


def test_cli_report_function_exists():
    assert callable(phase7_cli.show_research)


def test_cli_keyword_search_exists():
    assert callable(phase7_cli.keyword_search)


def test_cli_graph_functions_exist():
    assert callable(phase7_cli.show_entities)
    assert callable(phase7_cli.show_relationships)


def test_cli_statistics_function_exists():
    assert callable(phase7_cli.show_stats)


def test_cli_semantic_function_exists():
    assert callable(phase7_cli.semantic_search)