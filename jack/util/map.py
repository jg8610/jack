# -*- coding: utf-8 -*-

import pprint

import numpy as np

from jack.util.random import DefaultRandomState
from jack.util.vocab import Vocab

rs = DefaultRandomState(1337)


# sym (e.g. token, token id or class label)
# seq (e.g. sequence of tokens)
# seqs (sequence of sequences)
# corpus (sequence of sequence of sequences)
#   e.g. hypotheses (sequence of sequences)
#        premises (sequence of sequences)
#        support (sequence of sequence of sequences)
#        labels (sequence of symbols)
# corpus = [hypotheses, premises, support, labels]


def lower(xs):
    """returns lowercase for sequence of strings"""
    return [x.lower() for x in xs]


def get_list_shape(xs):
    if isinstance(xs, int):
        shape = []
    else:
        shape = [len(xs)]
        for i, x in enumerate(xs):
            if isinstance(x, list):
                if len(shape) == 1:
                    shape.append(0)
                shape[1] = max(len(x), shape[1])
                for j, y in enumerate(x):
                    if isinstance(y, list):
                        if len(shape) == 2:
                            shape.append(0)
                        shape[2] = max(len(y), shape[2])
    return shape


def get_entry_dims(corpus):
    """
    get number of dimensions for each entry; needed for placeholder generation
    """
    # todo: implement recursive form; now only OK for 'regular' (=most common type of) data structures
    if isinstance(corpus, dict):
        keys = list(corpus.keys())
        dims = {key: 0 for key in keys}
    else:
        keys = range(len(corpus))
        dims = [0 for _ in range(len(corpus))]  # scalars have dim 0 (but tensor version will have shape length 1)
    for key in keys:
        entry = corpus[key]
        try:
            while hasattr(entry, '__len__'):
                dims[key] += 1
                entry = entry[0]  # will fail if entry is dict
        except:
            dims[key] = None
    return dims


def numpify(xs, pad=0, keys=None, dtypes=None):
    """Converts a dict or list of Python data into a dict of numpy arrays."""
    is_dict = isinstance(xs, dict)
    xs_np = {} if is_dict else [0] * len(xs)
    xs_iter = xs.items() if is_dict else enumerate(xs)

    for i, (key, x) in enumerate(xs_iter):
        if keys is None or key in keys:
            shape = get_list_shape(x)
            dtype = dtypes[i] if dtypes is not None else np.int64
            x_np = np.full(shape, pad, dtype)

            nb_dims = len(shape)

            if nb_dims == 0:
                x_np = x

            else:
                def f(tensor, values):
                    t_shp = tensor.shape
                    if len(t_shp) > 1:
                        for _i, _values in enumerate(values):
                            f(tensor[_i], _values)
                    else:
                        tensor[0:len(values)] = [v for v in values]

                f(x_np, x)

            xs_np[key] = x_np
        else:
            xs_np[key] = x
    return xs_np


if __name__ == '__main__':
    import doctest

    print(doctest.testmod())
