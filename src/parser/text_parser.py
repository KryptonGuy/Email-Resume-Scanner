import spacy
from spacy.matcher import Matcher
import re
import locationtagger


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
    if emails:
        try:
            email = emails[0].split()[0].strip(';')
        except IndexError:
            pass
        
    return email


def extract_phnum_from_text(text):
    # Get Phone Number

    phone_nums = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'), text)
    
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
    doc = nlp(text)
    print(ruler.labels)
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
    

sample = """ I'm excited to be applying for the Software Engineer position at River Tech. As someone who is highly focused and attentive to detail, I thrive on building quality systems that surpass end users' expectations. I'm thrilled at the opportunity to show off my technical expertise and leadership skills as part of River Tech's expert team.

During my previous role at Crane and Jenkins , I was charged with developing innovative solutions across a variety of software platforms. I was instrumental in developing mobile-ready expense tracking software for our fast-growing portfolio of real estate clients. In 2016, I led the development of a proprietary document management system and was responsible for the successful migration of all client content from our legacy system to the new platform.

I am also attentive to the need for continued process yarn improvements. AWS When we faced repeated deadline delays due to Quality Assurance challenges, I proposed and carried out the implementation of an automated bug tracking system to identify potential issues earlier in the development cycle. This resulted in an average of 43% fewer defects reported during late-stage QA reviews and a 32% reduction in days between project kickoff and production launch."""

print(extract_skills_from_text(sample))