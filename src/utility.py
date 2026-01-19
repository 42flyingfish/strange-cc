from itertools import count
from typing import NewType

Identifier = NewType('Identifier', str)

# Nasty Global for use below
counter = count()


def make_temporary(prefix='tmp') -> Identifier:
    # this is supposed to generate an identifier to be
    # unquie. In practice, it probably isn't
    return Identifier(f'{prefix}.{next(counter)}')
