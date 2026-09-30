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


def find_archetype(user_input: str) -> Optional[str]:
    """
    Finds the best-matching archetype for the user's input based on
    curriculum keywords. Returns the archetype string or None.
    """
    topics = _load_registry()
    lower = user_input.lower()
    best_archetype = None
    best_score = 0

    for topic in topics:
        score = 0
        topic_name = topic.get("name", "").lower()
        if topic_name in lower or lower in topic_name:
            score += 10

        for kw in topic.get("keywords", []):
            if kw.lower() in lower:
                score += len(kw.split())

        if score > best_score:
            best_score = score
            best_archetype = topic.get("archetype")

    if best_archetype and best_score > 0:
        print(f"CurriculumLoader: Matched archetype '{best_archetype}' (score={best_score})")
        return best_archetype

    return None


def get_by_id(topic_id: int) -> Optional[dict]:
    """Returns a topic by its numeric ID."""
    topics = _load_registry()
    return next((t for t in topics if t["id"] == topic_id), None)


def list_all() -> list[dict]:
    """Returns all topics."""
    return _load_registry()
