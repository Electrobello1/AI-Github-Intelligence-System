
from Backend.Tools import (
    extract_title,
    extract_summary,
    extract_tags,
    readme_quality_score
)

# =========================
# TITLE TESTS
# =========================

def test_extract_title_normal():
    assert extract_title("# Hello World") == "Hello World"


def test_extract_title_no_header():
    result = extract_title("just plain text no header")
    assert result in ["Untitled Project", ""]


def test_extract_title_empty():
    result = extract_title("")
    assert result in ["Untitled Project", ""]


# =========================
# SUMMARY TESTS
# =========================

def test_extract_summary_basic():
    text = "This is a README.\n\nThis is second paragraph."
    summary = extract_summary(text)

    assert isinstance(summary, str)
    assert len(summary) > 0


def test_extract_summary_empty():
    summary = extract_summary("")
    assert isinstance(summary, str)


def test_extract_summary_long_text():
    text = "word " * 300
    summary = extract_summary(text)

    assert isinstance(summary, str)
    assert len(summary) <= 200  # based on your implementation


# =========================
# TAG EXTRACTION TESTS
# =========================

def test_extract_tags_normal():
    text = "machine learning python ai machine learning"
    tags = extract_tags(text)

    assert isinstance(tags, list)
    assert len(tags) <= 5


def test_extract_tags_noise():
    text = "!!! ### $$$ machine@@@ learning### python123 ai!!!"
    tags = extract_tags(text)

    assert isinstance(tags, list)
    assert len(tags) <= 5


def test_extract_tags_empty():
    tags = extract_tags("")
    assert tags == []


# =========================
# QUALITY SCORE TESTS
# =========================

def test_quality_score_empty():
    score = readme_quality_score("")
    assert score == 0


def test_quality_score_basic():
    text = "## Title\nSome text here"
    score = readme_quality_score(text)

    assert isinstance(score, int)
    assert score >= 0


def test_quality_score_with_code():
    text = "## Title\n```python\nprint('hello')\n```"
    score = readme_quality_score(text)

    assert score >= 1


def test_quality_score_full_structure():
    text = """
    # Project
    ## Installation
    ```bash
    pip install x
    ```
    """
    score = readme_quality_score(text)

    assert score >= 2