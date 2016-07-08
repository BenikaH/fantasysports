"""Function to cache data"""
import cPickle as pickle
import os
import hashlib
import re
import conf


def cache_disk(cache_folder=conf.cache_path, cache_comment=None):
    """ Handles caching of return value of functions
    Just decorate your function with this decorator"""
    def wrapper(f):
        def inner_function(*args, **kwargs):

            # calculate a cache key based on the decorated method signature
            m = hashlib.md5()
            margs = [x.__repr__() for x in args]
            # Filter function names and memory locations that are passed
            #     along with self objects e.g. self.compute(blah)
            margs = [re.sub('(\dx[\w\d]{6,}>)', '', x) for x in margs]
            mkwargs = [x.__repr__() for x in kwargs.values()]
            map(m.update, margs + mkwargs)
            m.update(f.__name__)
            m.update(f.__class__.__name__)
            key = m.hexdigest()
            if not os.path.exists(cache_folder):
                print '[cache] creating directory %s' % cache_folder
                os.makedirs(cache_folder)

            filepath = os.path.join(cache_folder, key if cache_comment is None
                                    else '%s_%s' % (cache_comment, key))
            # verify that the cached object exists and is less than $seconds
            # old
            if os.path.exists(filepath):
                # print '[cache] loading cached result: %s' % os.path.abspath(filepath)
                result = pickle.load(open(filepath, "rb"))

            # call the decorated function...
            else:
                print '[cache] creating cache: %s' % os.path.abspath(filepath)
                result = f(*args, **kwargs)
                pickle.dump(result, open(filepath, "wb"))

            return result
        return inner_function
    return wrapper
