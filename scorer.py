"""Score whether an answer contains the expected phrase."""


def judge(question, expects, answer, results) -> bool:
    """Return True when the expected phrase appears in the answer."""
    if not expects or not expects.strip():
        return False

    normalized_answer = " ".join(answer.casefold().split())
    normalized_expected = " ".join(expects.casefold().split())

    return normalized_expected in normalized_answer