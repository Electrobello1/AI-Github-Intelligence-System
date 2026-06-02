from Backend.graph import build_graph

def test_graph_runs_successfully():
    app = build_graph()

    result = app.invoke({
        "repo_url": "https://github.com/octocat/Hello-World",
        "attempts": 0
    })

    # -------------------------
    # BASIC STRUCTURE CHECK
    # -------------------------
    assert isinstance(result, dict)

    assert "status" in result
    assert "review_feedback" in result
    assert "quality_score" in result
    assert "title" in result
    assert "summary" in result

    # -------------------------
    # VALUE SANITY CHECKS
    # -------------------------
    assert result["status"] in ["pass", "retry"]
    assert isinstance(result["review_feedback"], dict)

def test_graph_invalid_repo_url():
        app = build_graph()

        result = app.invoke({
            "repo_url": "invalid_url",
            "attempts": 0
        })

        # system should NOT crash
        assert isinstance(result, dict)
        assert "status" in result
def test_graph_handles_missing_readme():
            app = build_graph()

            result = app.invoke({
                "repo_url": "https://github.com/some/nonexistent-repo-123456",
                "attempts": 0
            })

            # should gracefully degrade
            assert isinstance(result, dict)
            assert "title" in result
            assert "summary" in result