__author__ = 'alenush'

import pandas
import random
import itertools

RIGHT_DICTIONARY = {}

def take(n, iterable):
    """Return first n items of the iterable as a list"""
    return list(itertools.islice(iterable, n))

def random_match_exercise(number=10, write_in_file=None):
    """
    Exercise of type Match the word from right with left column
    Function takes right collocations and randomize them
    :return: rows like: coll1, coll2_wrong, coll2_right
    """
    elements = take(number, RIGHT_DICTIONARY.items())
    right_col = [paar[1] for paar in elements]
    if write_in_file != None:
        with open(write_in_file, 'w', encoding='utf-8') as exercise_file:
            for key, value in elements:
                exercise_file.write('{}, {}, {}\n'.format(key, random.choice(right_col), value))
    else:
        for key, value in elements:
                print(key, random.choice(right_col), value)


def open_collocation_file():
    df_collocations = pandas.read_csv('AcademicCollocationList.csv')
    begin_col = df_collocations[['Component I']]
    end_col = df_collocations[['Component II']]
    for begin, end in zip(begin_col.values, end_col.values):
        RIGHT_DICTIONARY[begin[0]] = end[0]


if __name__ == '__main__':
    collocation_list = open_collocation_file()
    random_match_exercise(write_in_file='match_exercise.txt')