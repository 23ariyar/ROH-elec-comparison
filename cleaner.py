from collections import Counter
from social_media import twitter_data, instagram_data


def most_common(text: str, FTR: tuple = ['.', ',', '!', 'of', 'and', 'is', 'the', 'for', '-', 'to', 'in', 'a', '\\x80\\x94', '"', 's', '(', ')', '\\x80¢']) -> list:
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

def extract_social_media_data(urls):
    data = {}
    for url in urls:
        if 'instagram' in url: 
            try: data['instagram'] = instagram_data(url)
            except: pass
        
        elif 'twitter' in url:
            try: data['twitter'] = twitter_data(url)
            except: pass
    return data
