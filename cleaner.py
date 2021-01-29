from collections import Counter


def most_common(text: str, FTR: tuple = ['.', ',', '!', 'of', 'and', 'is', 'the']) -> list:
    absolute = Counter(text.split()).most_common(50)

    cleaned = []
    for word, count in absolute:
        if word not in FTR:
            cleaned.append((word, count))

    return cleaned


def words_on(text: str, terms: tuple) -> dict:
    words_to_count = {}
    for term in terms:
        words_to_count[term] = text.count(term)

    return words_to_count
