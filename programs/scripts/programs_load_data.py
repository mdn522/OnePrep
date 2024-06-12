from programs.models import Program


def run(*args):
    programs = [
        {
            'pk': 1,
            'defaults': {
                'name': 'SAT',
                'is_active': True,
            },
        },
        {
            'pk': 3,
            'defaults': {
                'name': 'PSAT/NMSQT & PSAT 10',
                'is_active': False,
            },
        },
        {
            'pk': 2,
            'defaults': {
                'name': 'PSAT 8/9',
                'is_active': False,
            },
        },
    ]
    # bulk create or update
    for program in programs:
        print('Loading Program:', program)
        pk = program.pop('pk')
        Program.objects.update_or_create(pk=pk, **program)

    print('Programs loaded')
