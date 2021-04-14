import numpy as np
import pandas as pd


exams_names_dict = {'мат': 'maths', 'р': 'rus', 'м': 'maths', 'о': 'social_studies', 'рус': 'rus', 'физ': 'physics', 
              'хим': 'chemistry', 'ист': 'history', 'общ': 'social_studies',
              'инф': 'informatics', 'био': 'biology', 'гео': 'geography', 
              'анг': 'english', 'нем': 'german', 'фра': 'french', 
              'исп': 'spanish', 'кит': 'chinese', 'лит': 'literature', 'ино': 'foreign_language'}

        
def create_exams_dict(df: pd.DataFrame, indicator: iter):
    exams_names = list(find_exams_colnames(df))
    mean_scores = np.mean(df.loc[indicator, exams_names]).values
    return dict(zip(exams_names, mean_scores))


def find_exams_colnames(df: pd.DataFrame):
    """
    Finds colname for column wich maximum value is between 10 and 100.
    """
    tempdf = df.drop(columns = ['№', '№*', '№**'])
    types_filter = [np.issubdtype(dtype, np.number) for dtype in tempdf.dtypes]
    max_10_100 = (tempdf.loc[:, types_filter].max() <= 100) & (tempdf.loc[:, types_filter].max() > 10)
    return max_10_100.index[max_10_100]
        

def find_sum_colname_max(df: pd.DataFrame):
    """
    Finds colname for column wich maximum value exceeds 100.
    """
    tempdf = df.drop(columns = ['№', '№*', '№**'])
    types_filter = [np.issubdtype(dtype, np.number) for dtype in tempdf.dtypes]
    max_exceeds_100 = tempdf.loc[:, types_filter].max() > 100
    return max_exceeds_100.index[max_exceeds_100]
