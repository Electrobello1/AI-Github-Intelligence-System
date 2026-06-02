from typing import TypedDict, List, Dict

class A3State(TypedDict):
    repo_url: str
    readme: str
    stars: int
    forks: int
    language: str
    quality_score: int
    title: str
    summary: str
    tags: List[str]
    improvements: List[str]
    missing_sections: List[str]
    attempts: int
    review_feedback: Dict
    status: str
    confidence: float
    prev_issue_count: int
    user_question: str
    chat_history:str

def ensure_defaults(state: dict):
        return {
            "attempts": 0,
            "prev_issue_count": 999,
            **state
        }