import yaml
from pathlib import Path
from typing import Optional


_registry = None


def _load_registry() -> list[dict]:
    global _registry
    if _registry is None:
        path = Path("curriculum/topics.yaml")
        if not path.exists():
            print("CurriculumLoader: topics.yaml not found.")
            _registry = []
        else:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            _registry = data.get("topics", [])
            print(f"CurriculumLoader: Loaded {len(_registry)} topics.")
    return _registry


def find_by_keyword(user_input: str) -> Optional[dict]:
    """
    Finds a curriculum topic matching any of the user's words.
    Returns the topic dict (with archetype + params) or None.
    """
    topics = _load_registry()
    lower = user_input.lower()
    best_match = None
    best_score = 0

    for topic in topics:
        score = 0
        for kw in topic.get("keywords", []):
            if kw.lower() in lower:
                score += len(kw.split())  # Reward longer keyword matches
        if score > best_score:
            best_score = score
            best_match = topic

    if best_match and best_score > 0:
        print(f"CurriculumLoader: Matched topic {best_match['id']} '{best_match['name']}' (score={best_score})")
        return best_match

    return None


def get_by_id(topic_id: int) -> Optional[dict]:
    """
    Returns a topic by its numeric ID.
    """
    topics = _load_registry()
    return next((t for t in topics if t["id"] == topic_id), None)


def list_all() -> list[dict]:
    """
    Returns all 50 topics.
    """
    return _load_registry()
