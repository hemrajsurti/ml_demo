import base64
import pickle
def ascii_pickle(python_object):
    u"""Converts an arbitrary Python object to an ASCII-only string to be
    written to the database.  Unfortunately, even protocol 0 of Python's
    ``pickle`` module may emit non-ASCII characters, see
    <http://bugs.python.org/issue2980>.  However, this is dangerous since the
    database expects Unicode strings and can't decode such octet strings.
    Therefore, this routine does another encoding step using base64.  This
    makes debugging slightly more difficult, but there we go.

    :Parameters:
      - `python_object`: the object instance to be pickled

    :type python_object: object

    :Return:
      the ASCII-only string representing the object instance

    :rtype: str
    """
    # FixMe: Maybe instead of base64 another encoder should be used that keeps
    # the string largely readable.
    return base64.b64encode(pickle.dumps(python_object, protocol=2))


def ascii_unpickle(string):
    u"""This is the inverse function of `ascii_pickle`.

    :Parameters:
      - `string`: the ASCII-only database string to be unpickled

    :type string: str

    :Return:
      the original Python object instance that was represented by the string

    :rtype: object
    """
    return pickle.loads(base64.b64decode(string))