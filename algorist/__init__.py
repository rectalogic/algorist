# flake8: noqa

import logging

from .contextfree import Context
from .random import coinflip, prnd, rnd
from .rules import rule

logging.basicConfig(level=logging.INFO)
