from collections import OrderedDict

from utils.scraper.loaders.collegeboard_bluebook import CollegeBoardBlueBookLoader
from utils.scraper.loaders.collegeboard_question_bank import CollegeBoardQuestionBankLoader
from utils.scraper.loaders.princeton_review import PrincetonReviewLoader
from utils.scraper.loaders.satmocks import SATMocksLoader


loaders = OrderedDict([
    ('collegeboard_question_bank', CollegeBoardQuestionBankLoader()),
    ('collegeboard_bluebook', CollegeBoardBlueBookLoader()),
    ('princeton_review', PrincetonReviewLoader()),
    ('sat_mocks', SATMocksLoader()),
])


def run(*args):
    # loaders = [
    #     CollegeBoardQuestionBankLoader(),
    #     CollegeBoardBlueBookLoader(),
    #     PrincetonReviewLoader(),
    #     SATMocksLoader(),
    # ]

    if not args:
        print(f'Usage: python manage.py runscript load_data --script-args <loader> [<loader> ...]')
        print(f'Available loaders: {", ".join(loaders.keys())}')
        return

    for arg in args:
        if arg == 'all':
            for loader in loaders.values():
                loader.load()
            break

        if arg in loaders:
            loaders[arg].load()
        else:
            print(f'Loader "{arg}" not found.')
            print(f'Available loaders: {", ".join(loaders.keys())}')
