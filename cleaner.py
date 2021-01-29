from collections import Counter


def most_common(text: str) -> dict:
    return Counter(text.split()).most_common(50)


def words_on(text: str, terms: tuple):
    words_to_count = {}
    for term in terms:
        words_to_count[term] = text.count(term)

    return words_to_count
