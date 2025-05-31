"""
Natural Language Processing.

Can perform things like:
- Parts of Speech tagging.
- Named Entity Recognition
- Finding digits, words etc.
- Stopwords removal
- Compute Lexical Diversity

TODO:
- Summarization
"""
import nltk

# It's an idempotent operatation
nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('words')


def analyze(text: str):
    """
    Performs analysis on text using nltk.
    Currently does the following:
    - Length of the text
    - Most common words
    - Unique words
    - Collocations
    """
    words = nltk.word_tokenize(text)
    # Remove stopwords
    words = [word for word in words if word not in nltk.corpus.stopwords.words("english")]
    uniques = set(words)
    text = nltk.Text(words)
    freq_dist = nltk.FreqDist(text)
    length = len(text)
    most_common = freq_dist.most_common(10)
    collocations = text.collocations()
    return {"length": length, "most_common": most_common, "uniques": uniques, "collocations": collocations}


def is_meaningful_content(text: str):
    # If lot of single character words, which isn't even 'a' or 'i'.
    SINGLE_CHARACTER_PERCENTAGE_THRESHOLD = 0.5
    words = nltk.word_tokenize(text)
    single_character_count = 0
    for word in words:
        if len(word) == 1 and word.lower() not in ['a', 'i']:
            single_character_count += 1
    if single_character_count / len(words) > SINGLE_CHARACTER_PERCENTAGE_THRESHOLD:
        return False
    # If we are able to extract only page end markers, then it's an non meaningful content.
    # \x0c is the page end marker.
    return True
