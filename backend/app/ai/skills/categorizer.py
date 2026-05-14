from __future__ import annotations


def categorize_skills(skills: list[str], taxonomy: dict[str, list[str]]) -> dict[str, list[str]]:
    # Map normalized skill names back into taxonomy categories.
    # Only categories with matched skills are returned to keep the result compact.
    categories: dict[str, list[str]] = {category: [] for category in taxonomy}
    normalized_skill_lookup: dict[str, str] = {
        skill.lower(): skill for category in taxonomy for skill in taxonomy[category]
    }

    for skill in skills:
        lower_skill = skill.lower()
        for category, entries in taxonomy.items():
            if lower_skill in {entry.lower() for entry in entries}:
                categories[category].append(skill)
                break

    return {category: values for category, values in categories.items() if values}
