import pandas as pd
import numpy as np

import glob
import json

from page_parser import parse_individual_tab_mod
from utilities import *

if __name__ == '__main__':
    with open('students.json', 'w') as f: # add date!
        f.write('[')
        try:
            for page in glob.iglob('pages' + '/**/*.html', recursive=True):
                if not 'index.html' in page:
                    try:
                        page = parse_individual_tab_mod(page)
                        f.write(json.dumps(page)[1:-1])
                        f.write(',\n')
                    except IndexError:
                        pass
        finally:
            f.write(']')
