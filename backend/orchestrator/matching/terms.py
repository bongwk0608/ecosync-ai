def terms_from_startup(startup):
    values = [
        startup.get("domain", ""),
        startup.get("stage", ""),
        startup.get("location", ""),
        startup.get("market", ""),
        *startup.get("pain_points", []),
        *startup.get("goals", []),
        *startup.get("requested_support", []),
    ]
    return normalize_terms(values)


def terms_from_mentor(mentor):
    values = [
        mentor.get("location", ""),
        mentor.get("mentoring_style", ""),
        *mentor.get("expertise", []),
        *mentor.get("industries", []),
        *mentor.get("past_roles", []),
        *mentor.get("preferred_stage", []),
    ]
    return normalize_terms(values)


def normalize_terms(values):
    terms = set()
    for value in values:
        lowered = str(value).lower()
        if lowered:
            terms.add(lowered)
        for piece in lowered.replace("/", " ").replace("-", " ").split():
            if len(piece) > 2:
                terms.add(piece)
    return terms


def lower_list(values):
    return [str(value).lower() for value in values]


def ratio_overlap(source_terms, target_terms):
    clean_source = {term for term in source_terms if term}
    if not clean_source:
        return 0
    return min(1, len(clean_source.intersection(target_terms)) / len(clean_source))
