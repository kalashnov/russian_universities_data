import pandas as pd
import numpy as np

import glob
import json

from page_parser import parse_individual_tab
from page_parser import parse_program_tab
from utilities import *

def create_program_tab(program_tab, gen_individual_tab):
    program = {}
    individual_df = pd.DataFrame(gen_individual_tab)
    program['program'] = program_tab.pop('program')
    if program_tab['historical']:
        program['year'] = 2018
    else:
        program['year'] = int(program_tab['file'].split('/')[1][:4])
    program['observation_date'] = pd.to_datetime(
        program_tab['file'].split('/')[1], format='%Y%m%d'
    ).strftime('%Y-%m-%d')
    if 'атт' in individual_df:
        filt = ~individual_df['тип'].str.contains('Целевое')
        individual_df = individual_df.loc[filt]
        if np.sum(filt) == 0:
            raise IndexError
        orig = individual_df['атт'].str.lower().str.contains('ориг')
        bvi = individual_df['тип'].str.lower().str.contains('бви')
        orig_not_bvi = orig & ~bvi
        program['n_exams'] = len(find_exams_colnames(individual_df))
        n_sum_fields = find_sum_colname_max(individual_df)
        program['n_sum_fields'] = len(n_sum_fields)
        program['mean_sum'] = float(np.mean(individual_df.loc[orig & ~bvi, n_sum_fields[-1]]))
        program['mean_sum_all'] = float(np.mean(individual_df.loc[ ~bvi, n_sum_fields[-1]]))
        program.update(create_exams_dict(individual_df, orig & ~bvi))
        program['атт_check'] = int(np.sum(orig))
        program['бви_check'] = int(np.sum(bvi))
        
    program.update(program_tab)
    
    return program

def parse_page(page):
    return create_program_tab(
        parse_program_tab(page),
        parse_individual_tab(page)
    )
    

if __name__ == '__main__':
    with open('output.json', 'w') as f: # add date!
        f.write('[')
        try:
            for page in glob.iglob('pages' + '/**/*.html', recursive=True):
                if not 'index.html' in page:
                    try:
                        page = parse_page(page)
                        f.write(json.dumps(page))
                        f.write(',\n')
                    except IndexError:
                        pass
        finally:
            f.write(']')
