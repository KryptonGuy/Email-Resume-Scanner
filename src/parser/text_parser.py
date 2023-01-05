import spacy
from spacy.matcher import Matcher
import re
import locationtagger
import os
import pandas as pd

def extract_names_from_text(text):
    
    # Get Name
    nlp = spacy.load('en_core_web_sm')

    # initialize matcher with a vocab
    matcher = Matcher(nlp.vocab)

    nlp_text = nlp(text)

    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    matcher.add('NAME', [pattern])

    matches = matcher(nlp_text)
    
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text


def extract_email_from_text(text):

    emails = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    email = ""
    if emails:
        try:
            email = emails[0].split()[0].strip(';')
        except IndexError:
            print("errorrr email")
            email = ""
            pass
        
    return email


def extract_phnum_from_text(text):
    # Get Phone Number

    phone_nums = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    number = ""
    if phone_nums:
        number = ''.join(phone_nums[0])
        if len(number) > 10:
            number = "+" + number
    return number

    

def extract_skills_from_text(text):

    nlp = spacy.load("en_core_web_lg")
    skill_pattern_path = "src/utils/skill_patterns.jsonl"

    ruler = nlp.add_pipe("entity_ruler")
    ruler.from_disk(skill_pattern_path)
    nlp.pipe_names
    print(ruler.labels)
    doc = nlp(text)
    myset = []
    subset = []
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            subset.append(ent.text)
    myset.append(subset)

    return subset

def extract_location_from_text(text):

    place_entity = locationtagger.find_locations(text=text)

    return place_entity.cities


def extract_skills(text):
    
    nlp = spacy.load('en_core_web_sm')
    nlp_text = nlp(text)

    noun_chunks = nlp_text.noun_chunks

    tokens = [token.text for token in nlp_text if not token.is_stop]

    data = pd.read_csv("src/utils/skills_t.csv")

    skills = list(data.columns.values)
    skillset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]



def parse_text(data):
    
    json = {
        "Name" : extract_names_from_text(data),
        "Email": extract_email_from_text(data),
        "Number": extract_phnum_from_text(data),
        "Locations": extract_location_from_text(data),
        "Skills": extract_skills(data)

    }

    return json

    