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
import re
import nltk
import string
import logging
import Levenshtein

# It's an idempotent operatation
nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('words')

logger = logging.getLogger(__name__)


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
    if classify_passport(text):
        return "passport"
    if classify_pan(text):
        return "pan"
    lowered_text = text.lower()
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


def fuzzy_substring_match(text, phrase, max_distance=2):
    phrase_len = len(phrase)
    text = text.lower()
    phrase = phrase.lower()

    for i in range(len(text) - phrase_len + 1):
        window = text[i:i + phrase_len]
        logger.info(f"Comparing {window} with {phrase}")
        distance = Levenshtein.distance(window, phrase)
        if distance <= max_distance:
            return True, window, distance

    return False, None, None


def classify_passport(text: str):
    """
    Does this look like a passport?
    """
    text = text.lower()
    REPUBLIC_OF_INDIA = "republic of india"
    republic_of_india_found = False
    match_found, match_str, distance = fuzzy_substring_match(text, REPUBLIC_OF_INDIA)
    if match_found:
        logger.info(f"Matched {match_str} with {REPUBLIC_OF_INDIA} with distance {distance}")
        republic_of_india_found = True
    NATIONALITY = "nationality"
    nationality_found = False
    match_found, match_str, distance = fuzzy_substring_match(text, NATIONALITY)
    if match_found:
        logger.info(f"Matched {match_str} with {NATIONALITY} with distance {distance}")
        nationality_found = True
    PASSPORT_NUMBER = "passport no"
    passport_number_found = False
    match_found, match_str, distance = fuzzy_substring_match(text, PASSPORT_NUMBER)
    if match_found:
        logger.info(f"Matched {match_str} with {PASSPORT_NUMBER} with distance {distance}")
        passport_number_found = True
    DATE_OF_BIRTH = "date of birth"
    date_of_birth_found = False
    match_found, match_str, distance = fuzzy_substring_match(text, DATE_OF_BIRTH)
    if match_found:
        logger.info(f"Matched {match_str} with {DATE_OF_BIRTH} with distance {distance}")
        date_of_birth_found = True
    PLACE_OF_BIRTH = "place of birth"
    place_of_birth_found = False
    match_found, match_str, distance = fuzzy_substring_match(text, PLACE_OF_BIRTH)
    if match_found:
        logger.info(f"Matched {match_str} with {PLACE_OF_BIRTH} with distance {distance}")
        place_of_birth_found = True
    GIVEN_NAME = "given name"
    given_name_found = False
    match_found, match_str, distance = fuzzy_substring_match(text, GIVEN_NAME)
    if match_found:
        logger.info(f"Matched {match_str} with {GIVEN_NAME} with distance {distance}")
        given_name_found = True
    SURNAME = "surname"
    surname_found = False
    match_found, match_str, distance = fuzzy_substring_match(text, SURNAME)
    if match_found:
        logger.info(f"Matched {match_str} with {SURNAME} with distance {distance}")
        surname_found = True
    found_array = [republic_of_india_found, nationality_found, passport_number_found, date_of_birth_found, place_of_birth_found, given_name_found, surname_found]
    found_true = [x for x in found_array if x]
    # Consider 60% of the text as a threshold.
    if len(found_true)/len(found_array) >= 0.6:
        return True
    return False


def classify_pan(text: str):
    text = text.lower()
    INCOME_TAX_DEPARTMENT = 'income tax department'
    GOVT_OF_INDIA = 'govt of india'
    PERMANENT_ACCOUNT_NUMBER = 'permanent account number'
    income_tax_department_found = False
    govt_of_india_found = False
    permanent_account_number_found = False
    match_found, match_str, distance = fuzzy_substring_match(text, INCOME_TAX_DEPARTMENT, max_distance=5)
    if match_found:
        logger.info(f"Matched {match_str} with {INCOME_TAX_DEPARTMENT} with distance {distance}")
        income_tax_department_found = True
    match_found, match_str, distance = fuzzy_substring_match(text, GOVT_OF_INDIA, max_distance=4)
    if match_found:
        logger.info(f"Matched {match_str} with {GOVT_OF_INDIA} with distance {distance}")
        govt_of_india_found = True
    match_found, match_str, distance = fuzzy_substring_match(text, PERMANENT_ACCOUNT_NUMBER, max_distance=4)
    if match_found:
        logger.info(f"Matched {match_str} with {PERMANENT_ACCOUNT_NUMBER} with distance {distance}")
        permanent_account_number_found = True
    found_array = [income_tax_department_found, govt_of_india_found, permanent_account_number_found]
    found_true = [x for x in found_array if x]
    # Consider 60% of the text as a threshold.
    if len(found_true)/len(found_array) >= 0.6:
        return True
    return False


def analyze_passport(text: str):
    # Word boundary on both sides.
    # An upper case letter followed by exactly 7 digits
    logger.info("Analyzing passport")
    FIRST_NAME = "given name(s)"
    DOB = "date of birth"
    LAST_NAME = "surname"
    first_name = None
    last_name = None
    dob = None
    matches = re.findall(r'\b[A-Z]\d{7}\b', text)
    passport_number = None
    if len(matches) > 0:
        passport_number = matches[0]
    try:
        # Even if other fields break, atleast extract the passport number
        lines = text.splitlines()
        non_blank_lines = [line for line in lines if line.strip() != '']
        text = '\n'.join(non_blank_lines)
        text = text.lower()
        match_found, match_str, distance = fuzzy_substring_match(text, FIRST_NAME, max_distance=3)
        if match_found:
            index = text.index(match_str)
            new_line_index = text.find('\n', index)
            content_after_new_line = text[new_line_index+1:]
            name_and_others = content_after_new_line.split('\n')
            if len(name_and_others) > 0:
                first_name = name_and_others[0]
        match_found, match_str, distance = fuzzy_substring_match(text, LAST_NAME, max_distance=2)
        if match_found:
            index = text.index(match_str)
            new_line_index = text.find('\n', index)
            content_after_new_line = text[new_line_index+1:]
            name_and_others = content_after_new_line.split('\n')
            if len(name_and_others) > 0:
                last_name = name_and_others[0]
        match_found, match_str, distance = fuzzy_substring_match(text, DOB, max_distance=2)
        if match_found:
            index = text.index(match_str)
            new_line_index = text.find('\n', index)
            content_after_new_line = text[new_line_index+1:]
            name_and_others = content_after_new_line.split('\n')
            if len(name_and_others) > 0:
                dob = name_and_others[0]
    except Exception as e:
        logger.error(e)
        pass
    data = {
    }
    if passport_number is not None:
        data['Passport Number'] = passport_number
    if first_name is not None:
        data['First Name'] = first_name
    if last_name is not None:
        data['Last Name'] = last_name
    if dob is not None:
        data['Date Of Birth'] = dob
    return data


def analyze_pan(text: str):
    # Remove blank lines
    lines = text.splitlines()
    non_blank_lines = [line for line in lines if line.strip() != '']
    text = '\n'.join(non_blank_lines)
    lowered_text = text.lower()
    # Word boundary on both sides.
    # 5 upper case letters followed by exactly 4 digits, followed by a letter
    matches = re.findall(r'\b[A-Z]{5}\d{4}[A-Z]{1}\b', text)
    pan_number = None
    name = None
    father_name = None
    dob = None
    if len(matches) > 0:
        pan_number = matches[0]
    # Extract name
    # Find where "India" occurs
    match_found, match_str, distance = fuzzy_substring_match(lowered_text, "india")
    if match_found:
        # Find index of "India"
        index = lowered_text.index(match_str)
        # Find first new line after this index
        new_line_index = text.find('\n', index)
        # Name of person is after this new line
        content_after_new_line = text[new_line_index+1:]
        name_and_others = content_after_new_line.split('\n')
        # Get the name of the person
        if len(name_and_others) > 0:
            name = name_and_others[0]
            # Remove punctuation from name
            name = name.translate(str.maketrans('', '', string.punctuation))
            name = name.strip()
    if name is not None and len(name_and_others) > 1:
        # Father name is just after name, on the next line
        father_name = name_and_others[1]
        father_name = father_name.translate(str.maketrans('', '', string.punctuation))
        father_name = father_name.strip()
        if len(name_and_others) > 2:
            dob = name_and_others[2]
    data = {}
    if pan_number is not None:
        data['PAN No.'] = pan_number
    if name is not None:
        data['Name'] = name
    if father_name is not None:
        data["Father's Name"] = father_name
    if dob is not None:
        data['Date of Birth'] = dob
    return data
