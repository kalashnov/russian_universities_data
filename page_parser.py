from bs4 import BeautifulSoup
import glob
import json
import re
import itertools
import js2py
from collections import defaultdict
import config

from joblib import Memory
location = './cachedir'
memory = Memory(location, verbose=0)

need_full_names = ['экз', 'егэ', 'ака', 'арх', 'тво', 'ви ', 'фк', 'тв.', 'рис', 'вну', 'про', 'диз', 'вит', 'доп', 'вст', 
                   'жив', 'муз', 'ржк', 'соб', 'спе', 'тат', 'тк', 'тку', 'эип', 'эко', 'эле', 'воз', 'гид', 'дош', 'осн', 'пед', 'пси', 'эк.']

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


def reconstruct_field(js, obfuscation=None): # works long!
    if not isinstance(js, str):
        return js
    if js.isdigit():
        return int(js)
    elif 'Enc' in js and obfuscation:
        return js2py.eval_js(';'.join([obfuscation, js]))
    else:
        return str(js)


def html_table_parse(table): # refactor -- move to pd.from_html
    rows = table.find_all('tr')
    titles_parsed = [(r.string or '').strip().lower() for r in rows.pop(0).find_all('th')]
    titles = [title if (title[:3] in need_full_names) else title[:3] for title in titles_parsed]
    for r in rows:
        retval = dict(
            (title, entry.string) if 'дви' not in title else ('дви', entry.string)
            for title, entry in zip(titles, r.find_all('td'))
        )
        # execute
        yield retval

        
def format_program_dict(dictionary: dict):
    for key in dictionary:
        if isinstance(dictionary[key], str):
            dictionary[key] = dictionary[key].strip()
            if dictionary[key].isdigit():
                dictionary[key] = int(dictionary[key])
    return dictionary

@memory.cache
def parse_individual_tab(file):
    page = open(file, 'r')
    soup = BeautifulSoup(page, 'html.parser')
    obfuscation = soup.find(text=re.compile(".*function Enc.*"))
    if obfuscation is not None:
        obfuscation = re.sub(r'document\[.*\]', 'return', obfuscation)
    
    historical = soup.find(text='Это справочная таблица за 2018 год, актуальная информация доступна на сайте admlist.ru') is not None
    tables = soup.find_all('table')
    if len(tables) <= 1:
        return [dict(file=file)]
    else:
        return [
                dict(
                    {k: reconstruct_field(v, obfuscation=obfuscation) for k, v in row.items()},
                    program=str(soup.h2.get_text()), obfuscation=obfuscation, historical=historical, file=file
                )
                for row in html_table_parse(tables[-1])
        ]
def parse_individual_tab_mod(file):
    page = open(file, 'r')
    soup = BeautifulSoup(page, 'html.parser')
    obfuscation = soup.find(text=re.compile(".*function Enc.*"))
    if obfuscation is not None:
        obfuscation = re.sub(r'document\[.*\]', 'return', obfuscation)
    
    historical = soup.find(text='Это справочная таблица за 2018 год, актуальная информация доступна на сайте admlist.ru') is not None
    tables = soup.find_all('table')
    if len(tables) <= 1:
        return [dict(file=file)]
    else:
        return [
                dict(
                    {k: reconstruct_field(v, obfuscation=obfuscation) for k, v in row.items()},
                    program=str(soup.h2.get_text()), obfuscation=obfuscation, historical=historical, date=file[6:14],
                    year=file[6:10], month=file[10:12], day=file[12:14], file=file
                )
                for row in html_table_parse(tables[-1])
        ]

#     except Exception as e:
#         yield dict(file=file, error_repr=repr(e), error_str=str(e), error_message=getattr(e, 'message', None))
# Yields single generator for single html-file with tuples ('key', 'value').
# For successful try keys include: 'кцп', 'зая', 'люд', 'атт', 'ок', 'бви', 'цел', 'кво', 'program', 'obfuscation', 'historical', 'file'. 
def parse_program_tab(file):
    print('Processing program tab', file)
    page = open(file, 'r')
    soup = BeautifulSoup(page, 'html.parser')
    obfuscation = soup.find(text=re.compile(".*function Enc.*"))
    if obfuscation is not None:
        obfuscation = re.sub(r'document\[.*\]', 'return', obfuscation)

    historical = soup.find(text='Это справочная таблица за 2018 год, актуальная информация доступна на сайте admlist.ru') is not None
    tables = soup.find_all('table')
    program_table = next(html_table_parse(tables[0]))
    return format_program_dict(dict(
        program_table,
        program=soup.h2.get_text(), obfuscation=obfuscation, historical=historical, file=file
    ))
