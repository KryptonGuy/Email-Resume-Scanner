import spacy
from spacy.matcher import Matcher
import re
import locationtagger
import pandas as pd
from logger import getLogger
import traceback

logger = getLogger(__name__)

class TextParser:

    def __init__(self, text) -> None:
        self.text = text

    def extract_names_from_text(self):
        
        logger.info("Extracting name from text.")

        # Get Name
        try:
            nlp = spacy.load('en_core_web_sm')
        except Exception:
            logger.error(f"Error loading nlp en_core_web_sm module \n {traceback.format_exc()}")
            return ""

        # initialize matcher with a vocab
        matcher = Matcher(nlp.vocab)

        try:
            nlp_text = nlp(self.text)
        except Exception:
            logger.error(f"Unable to process text in spacy \n {traceback.format_exc()}")
            return ""

        # First name and Last name are always Proper Nouns
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        
        matcher.add('NAME', [pattern])

        matches = matcher(nlp_text)
        
        for _, start, end in matches:
            span = nlp_text[start:end]
            return span.text


    def extract_email_from_text(self):

        logger.info("Extracting email from text")

        emails = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", self.text)
        email = ""
        if emails:
            try:
                email = emails[0].split()[0].strip(';')
            except IndexError:
                logger.error(f"Unable to get email from {emails}")

        return email


    def extract_phnum_from_text(self):

        logger.info("Extracting PhNum from text")

        # Get Phone Number
        phone_nums = re.findall(re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'), self.text)

        if phone_nums:
            return phone_nums[0]

        else:
            return []


    def extract_location_from_text(self):

        logger.info("Extracting Location from text")

        place_entity = locationtagger.find_locations(text=self.text)

        return place_entity.cities


    def extract_skills(self):
        
        logger.info("Extracting Skills from text")

        # Load NLP Module
        try:
            nlp = spacy.load('en_core_web_sm')
        except Exception:
            logger.error(f"Error loading nlp en_core_web_sm module \n {traceback.format_exc()}")
            return ""

        try:
            nlp_text = nlp(self.text)
        except Exception:
            logger.error(f"Unable to process text in spacy \n {traceback.format_exc()}")
            return ""

        noun_chunks = nlp_text.noun_chunks

        tokens = [token.text for token in nlp_text if not token.is_stop]

        try:
            data = pd.read_csv("src/utils/skills.csv")
        except Exception:
            logger.error(f"Unable to read skills dataset \n {traceback.format_exc()}")
            return ""


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



    def get_parsed_json(self):
        
        json = {
            "Name" : self.extract_names_from_text(),
            "Email": self.extract_email_from_text(),
            "PhNum": self.extract_phnum_from_text(),
            "Locations": self.extract_location_from_text(),
            "Skills": self.extract_skills()

        }

        return json


    # //Deprecated//
    def extract_skills_from_text_dep(self):

        nlp = spacy.load("en_core_web_lg")
        skill_pattern_path = "src/utils/skill_patterns.jsonl"

        ruler = nlp.add_pipe("entity_ruler")
        ruler.from_disk(skill_pattern_path)
        nlp.pipe_names
        print(ruler.labels)
        doc = nlp(self.text)
        myset = []
        subset = []
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                subset.append(ent.text)
        myset.append(subset)

        return subset

    