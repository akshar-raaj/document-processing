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
    # No word could be extracted
    if len(words) == 0:
        return False
    single_character_count = 0
    for word in words:
        if len(word) == 1 and word.lower() not in ['a', 'i']:
            single_character_count += 1
    if single_character_count / len(words) > SINGLE_CHARACTER_PERCENTAGE_THRESHOLD:
        return False
    # If we are able to extract only page end markers, then it's an non meaningful content.
    # \x0c is the page end marker.
    PAGE_MARGER_PERCENTAGE_THRESHOLD = 0.5
    if text.count("\x0c") / len(text) > PAGE_MARGER_PERCENTAGE_THRESHOLD:
        return False
    return True


def classify(text: str):
    """
    Classifies a text into various categories. Currently supported categories are:
    - PAN Card
    - Aadhar Card
    - Passport

    It currently does a simple string matching. We will move to NLP NaiveBayes Classification soon.
    And gradually to more advanced classification models.
    """
    lowered_text = text.lower()
    passport_needed_words = ['india', 'indian', 'surname', 'nationality', 'given', 'name', 'passport', 'date of birth', 'place of birth', 'place of issue', 'date of issue', 'passport no']
    passport_found_words = 0
    for passport_word in passport_needed_words:
        if passport_word in lowered_text:
            passport_found_words += 1
    if passport_found_words >= 6:
        # Also ensure Passport number REGEX is found
        return "passport"
    pan_needed_words = ['income', 'tax', 'department', 'govt', 'india']
    pan_found_words = 0
    for pan_word in pan_needed_words:
        # Enhance it to make it lenient. For example, 'indome' could be found instead of 'income'
        # OCR makes such kind of mistakes and hence accommodation for such must be made.
        if pan_word in lowered_text:
            pan_found_words += 1
    if pan_found_words >= 3:
        # TODO: Also make sure that a Regex of form 'AZMPR1111L' is found.
        # This text is dark and bold and OCR would have definitely picked it up.
        return "pan"
    # In Aadhaar Card, Government of India is shaded, hence binarization causes it not to be read properly.
    aadhaar_needed_words = ['issue', 'date']
    aadhaar_found_words = 0
    for aadhaar_word in aadhaar_needed_words:
        # Enhance it to make it lenient. For example, 'isdue' could be found instead of 'issue'
        if aadhaar_word in lowered_text:
            aadhaar_found_words += 1
    if aadhaar_found_words >= 1:
        # aadhaar has a regex of form 1234 1234 1234
        # This finding is a must because it is dark and bold and OCR would have definitely picked it up.
        return "aadhaar"
    return None