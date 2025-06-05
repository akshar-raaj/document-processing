"""
Responsible for doing Natural Language Processing.
It should ideally operate on the extracted text.

It should have ability to perform things like:
- Parts of Speech tagging.
- Named Entity Recognition
- Finding digits, words etc.
- Stopwords removal
- Compute Lexical Diversity

Later, we want it to perform:
- Summarization
- Answer basic question
"""

import logging
import spacy

logger = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_sm")


def parts_of_speech(text: str):
    """
    Extracts parts of speech from the text
    """
    nouns = []
    verbs = []
    doc = nlp(text)
    for token in doc:
        if token.pos_ == "PROPN":
            nouns.append(token)
        elif token.pos_ == "VERB":
            verbs.append(token)
    data = {
        "nouns": nouns,
        "verbs": verbs
    }
    return data


def entities(text: str):
    doc = nlp(text)
    ents = [ent.text for ent in doc.ents]
    return ents


def remove_punctuations(text: str):
    doc = nlp(text)
    return [token.text for token in doc if not token.is_punct]


def remove_stopwords(text: str):
    doc = nlp(text)
    return [token.text for token in doc if not token.is_stop]


def remove_punctuations_and_stopwords(text: str):
    doc = nlp(text)
    tokens = []
    for token in doc:
        if not token.is_stop and not token.is_punct:
            tokens.append(token)
    return tokens


def summarize(text: str):
    pass


def converse(text: str, question: str):
    """
    Answer simple questions like:
    - Who did something?
    - When something happened?
    - How much does something take.
    - Where did something happen.

    The following constructs will play a role here:
    - Parts of Speech (POS tagging)
    - Named Entities (NER)
    - Syntactic Dependencies (dep_)
    - Rule based matching. In addition to regex, use token attributes like is_punct, is_stop etc.
    """
    proper_nouns = []
    verbs = []
    subjects = []
    objects = []
    prepositions = []
    numerics = []
    dates = []
    doc = nlp(text)
    lowered_question = question.lower()
    for token in doc:
        logger.info(f"Token: {token.text}, POS: {token.pos_}")
        if token.pos_ == "PROPN":
            proper_nouns.append(token)
        if token.pos_ == "VERB":
            verbs.append(token)
        if token.dep_ == "nsubj":
            subjects.append(token)
        if token.dep_ == "pobj":
            objects.append(token)
        if token.pos_ == 'ADP':
            prepositions.append(token)
        if token.like_num:
            numerics.append(token)
    for ent in doc.ents:
        logger.info(f"Entity: {ent.text}, Type: {ent.label_}")
        if ent.label_ == "DATE":
            dates.append(ent)
    logger.info(f"Nouns: {proper_nouns}")
    logger.info(f"Verbs: {verbs}")
    logger.info(f"Subjects: {subjects}")
    logger.info(f"Prepositions: {prepositions}")
    if "who" in lowered_question:
        # The answer should probably be a proper noun.
        if len(proper_nouns) == 1:
            return proper_nouns[0].text
        # If there are multiple nouns, then most probably the subject instead of the object is the answer.
        # Hence dependency parsing can help us get that.
        # We are currently dealing with single sentences.
        # TODO: Modify it to get more context from the question, and then infer the correct subject
        return subjects[0]
    if "where" in lowered_question:
        # It means we want a place as answer
        # The answer should probably be a noun
        # Very likely it is followed by a prepositional phrase.
        # Examples: They went "to" Colombo, kept on "the" table. etc.
        if len(objects) > 0:
            return objects[0]
        # Statements like "apaar went to play"
        # Here play is not an object. So use the token appearing right after preposition
        if len(prepositions) > 0:
            prep = prepositions[0]
            return doc[prep.i + 1]
    if "how much" in lowered_question:
        # A quantity has to be returned
        # A quantity would mean a numeric
        if len(numerics) > 0:
            return numerics[0]
    if "when" in lowered_question:
        # A date has to be returned
        if len(dates) > 0:
            return dates[0]
    return None
