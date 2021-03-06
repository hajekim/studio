import pandas as pd
import numpy as np
import random
import os
from sklearn.datasets import load_iris as sklearn_load_iris
import string

TESTDATA_RELATIVEPATH = '''/../sample_data'''

_PATH_PARQUET = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) +
                                TESTDATA_RELATIVEPATH)
_PATH_FORMAT_PARQUET = _PATH_PARQUET + '''/{}'''


def load_dataset(fname):
    return pd.read_parquet(_PATH_FORMAT_PARQUET.format(fname), engine='auto')


def save_dataset(table, fname):
    _make_dir(_PATH_PARQUET)
    pd.DataFrame(table).to_parquet(_PATH_FORMAT_PARQUET.format(fname),
                                   engine='auto', compression='snappy')


def load_iris():
    return load_dataset('iris')


def load_basic_test_data(data_size=20, seed=1):
    _columns = [
        {'name': 'grp', 'type': 'category', 'population': ['G', 'B']},
        {'name': 'd1', 'type': 'float', 'min_value':-1000.0,
         'max_value': 1000.0},
        {'name': 'd2', 'type': 'float', 'min_value':-1000.0,
         'max_value': 1000.0, 'n_null': 2},
        {'name': 'str1', 'type': 'string', 'min_length': 1, 'max_length': 3,
         'population': ['a', 'b']},
        {'name': 'str2', 'type': 'string', 'min_length': 5, 'max_length': 10,
         'population': (string.ascii_uppercase + string.ascii_lowercase +
                        string.punctuation),
         'n_null': 3},
        {'name': 'int1', 'type': 'int', 'min_value': 1, 'max_value': 1000},
        {'name': 'int2', 'type': 'int', 'min_value':-1000, 'max_value': 1000}
        ]

    return load_random_table(columns=_columns, seed=seed,
                             data_size=data_size)


def load_random_classification(data_size=200, seed=1, n_xcol=4, n_class=3):
    _columns = []
    for i in range(1, n_xcol + 1):
        _columns.append({
            'name': 'x{}'.format(i),
            'type': 'float',
            'min_value': 0.0,
            'max_value': 1.0
            })

    _columns.append({
            'name': 'y',
            'type': 'int',
            'min_value': 0,
            'max_value': n_class - 1
        })

    return load_random_table(columns=_columns, seed=seed,
                             data_size=data_size)


def load_random_regression(data_size=200, seed=1, n_xcol=4):
    _columns = []
    for i in range(1, n_xcol + 1):
        _columns.append({
            'name': 'x{}'.format(i),
            'type': 'float',
            'min_value': 0.0,
            'max_value': 1.0
            })

    _columns.append({
            'name': 'y',
            'type': 'float',
            'min_value': 0.0,
            'max_value': 1.0
        })

    return load_random_table(columns=_columns, seed=seed,
                             data_size=data_size)


def add_category_column(table, group_col_name, population, seed=None):
    table[group_col_name] = _get_category_column(data_size=len(table),
                                                 population=population,
                                                 seed=seed)
    return table


def load_random_table(columns, seed=None, data_size=20, add_index=True):

    npr = np.random.RandomState(seed)
    random.seed(seed)

    col_info = {}
    if add_index:
        col_info['index'] = np.arange(1, data_size + 1, step=1)

    for c in columns:

        n_null = 0 if 'n_null' not in c else c['n_null']
        i_nulls = random.sample(range(0, data_size), n_null)

        if c['type'] == 'int':
            new_col_data = npr.randint(
                low=c['min_value'], high=c['max_value'] + 1, size=data_size)
        elif c['type'] == 'float':
            new_col_data = (npr.random_sample(size=data_size) *
                            (c['max_value'] - c['min_value']) +
                            c['min_value'])
            for i in i_nulls:
                new_col_data[i] = np.nan
        elif c['type'] == 'category':
            new_col_data = _get_category_column(
                data_size=data_size,
                population=c['population'],
                seed=seed)
        elif c['type'] == 'string':
            new_col_data = [_get_randstring(c['population'],
                                            c['min_length'],
                                            c['max_length'])
                            for _ in range(0, data_size)]
            for i in i_nulls:
                new_col_data[i] = None
        else:
            new_col_data = [None for _ in range(0, data_size)]

        col_info[c['name']] = new_col_data

    data = pd.DataFrame(data=col_info)
    return data


def load_random_float_table(data_size=20, seed=None, n_col=4,
                            min_value=0.0, max_value=1.0, add_index=True):
    cols = []
    for i in range(1, n_col + 1):
        c = {'name': 'x{}'.format(i), 'type': 'float', 'min_value': min_value,
             'max_value': max_value}
        cols.append(c)
    return load_random_table(columns=cols, seed=seed, data_size=data_size,
                             add_index=add_index)


def _make_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def _load_iris_sklearn():
    raw_data = sklearn_load_iris()
    out_data = pd.DataFrame(data=raw_data.data,
                            columns=['sepal_length', 'sepal_width',
                                     'petal_length', 'petal_width'])
    out_data['species'] = [raw_data.target_names[x] for x in raw_data.target]
    return out_data


def _get_randstring(population, min_length, max_length):
    return ''.join(random.choices(population,
                                  k=random.randint(min_length, max_length)))


def _get_category_column(data_size, population, seed=None):
    random.seed(seed)
    pop_len = len(population)
    if pop_len > data_size:
        raise RuntimeError(
            '''The data size must be larger than '''
            '''each category population size.''')
    temp_category_coldata = (population +
                             random.choices(
                                 population=population,
                                 k=(data_size - pop_len)))
    random.shuffle(temp_category_coldata)
    return temp_category_coldata
