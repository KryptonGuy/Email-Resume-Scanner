from pyresparser import ResumeParser


def parse_resume_file(file_path):
    file_path = "resume.pdf"
    data = ResumeParser(file_path).get_extracted_data()

    return data
    
