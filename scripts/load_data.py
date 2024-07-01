from utils.scraper.loaders.collegeboard_bluebook import CollegeBoardBlueBookLoader
from utils.scraper.loaders.collegeboard_question_bank import CollegeBoardQuestionBankLoader

def run(*args):
    loader = CollegeBoardQuestionBankLoader()
    loader.load()
