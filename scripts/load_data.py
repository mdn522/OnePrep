from utils.scraper.loaders.collegeboard_bluebook import CollegeBoardBlueBookLoader
from utils.scraper.loaders.collegeboard_question_bank import CollegeBoardQuestionBankLoader
from utils.scraper.loaders.satmocks import SATMocksLoader


def run(*args):
    # loader = CollegeBoardQuestionBankLoader()
    # loader = CollegeBoardBlueBookLoader()

    loader = SATMocksLoader()
    loader.load()
