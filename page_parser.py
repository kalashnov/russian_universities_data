from bs4 import BeautifulSoup
import glob
import json
import itertools
import js2py
from collections import defaultdict
import config

IDENTIFYING_EXAMS = ['рус', 'мат', 'ино', 'физ', 'хим', 'общ', 'ист']
IDENTIFYING_EXAMS = ['рус']

class Student(object):
    def __init__(self, fio, score_rus=None):
        self.fio = fio
        self.score_rus = score_rus

class Application(object):
    def __init__(self, student, university, application_type, status):
        self.student = student
        self.university = university
        self.application_type = application_type
        self.status = status


def reconstruct_field(js, obfuscation=False):
    if not isinstance(js, str):
        return js
    if js.isdigit():
        return int(js)
    elif 'Enc' in js and obfuscation:
        return js2py.eval_js('function Enc(_0xbf5dx2){return(_0xbf5dx2^27)};' + js)
    else:
        return js


def html_table_parse(table):
    rows = table.find_all('tr')
    titles = [r.string for r in rows.pop(0).find_all('th')]
    for r in rows:
        retval = {
            title.strip()[:3].lower(): entry.string if entry.string is not None else list(entry.strings)
            for title, entry in zip(titles, r.find_all('td'))
        }
        # execute
        yield retval


def parse_individual_tab(file):
    print('Processing individual tab', file)
    try:
        page = open(file, 'r')
        soup = BeautifulSoup(page, 'html.parser')
        obfuscation = soup.find(text='var _0x9a08=["write"];function Enc(_0xbf5dx2){document[_0x9a08[0]](_0xbf5dx2^27)}') is not None
        historical = soup.find(text='Это справочная таблица за 2018 год, актуальная информация доступна на сайте admlist.ru') is not None
        tables = soup.find_all('table')
        if len(tables) <= 1:
            yield dict(file=file)
        else:
            yield from (
                    dict(
                        {k: reconstruct_field(v, obfuscation=obfuscation) for k, v in row.items()},
                        program=soup.h2.get_text(), obfuscation=obfuscation, historical=historical,
                        file=file
                    )
                    for row in html_table_parse(tables[-1])
                )
    except Exception as e:
        yield dict(file=file, error_repr=repr(e), error_str=str(e), error_message=e.message)

# Yields single generator for single html-file with tuples ('key', 'value').
# For successful try keys include: 'кцп', 'зая', 'люд', 'атт', 'ок', 'бви', 'цел', 'кво', 'program', 'obfuscation', 'historical', 'file'. 
def parse_program_tab(file):
    print('Processing program tab', file)
    try:
        page = open(file, 'r')
        soup = BeautifulSoup(page, 'html.parser')
        obfuscation = soup.find(text='var _0x9a08=["write"];function Enc(_0xbf5dx2){document[_0x9a08[0]](_0xbf5dx2^27)}') is not None
        historical = soup.find(text='Это справочная таблица за 2018 год, актуальная информация доступна на сайте admlist.ru') is not None
        tables = soup.find_all('table')
        if len(tables) <= 1:
            yield dict(file=file)
        else:
            program_table = next(html_table_parse(tables[0]))
            yield from dict(
                program_table,
                program=soup.h2.get_text(), obfuscation=obfuscation, historical=historical, file=file
            ).items()
    except Exception as e:
        yield dict(file=file, error_repr=repr(e), error_str=str(e), error_message=e.message)

    
if __name__ == '__main__': # ok, for now csv. then mongo/Hadoop/Greenplum then
    results = []
    students = defaultdict(dict)
    for file in glob.iglob('pages' + '/**/*.html', recursive=True):
        new_entries = parse_page_to_csv(file)
        results.append(dict(entry, date=file.split('/')[1]) for entry in new_entries)
    all_results = itertools.chain(*results)
    json.dump(list(all_results), open('test_string.json', 'w'), ensure_ascii=False, indent=4)
    # for result in all_results:
    #     if 'фио' not in result:
    #         print('skipping') #aaand skip all doc???
    #     if result['фио'] in students and all(
    #             result[exam] != students[result['фио']][exam]
    #         for exam in IDENTIFYING_EXAMS
    #     ):
    #         result['фио'] = result['фио'] + ' 2'
    #     students[result['фио']].update(result)
    #
    # json.dump(students, 'test_students.csv')