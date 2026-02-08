from textblob import TextBlob

BANNED = [
    "kill","die","suicide","hate","violence","blood","hurt","racist"
]

def is_safe(text):

    lower = text.lower()

    for w in BANNED:
        if w in lower:
            return False

    sentiment = TextBlob(text).sentiment.polarity
    if sentiment < -0.3:
        return False

    if len(text.split()) > 18:
        return False

    return True
