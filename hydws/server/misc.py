"""
HYDWS server specific general purpose utilities.
"""

import base64
import datetime
import functools
import re
import sys
import traceback

import marshmallow as ma

from flask import make_response as _make_response

from hydws import __version__
from hydws.server.errors import FDSNHTTPError

dateutil_available = False
try:
    from dateutil import parser
    dateutil_available = True
except ImportError:
    dateutil_available = False


# from marshmallow (originally from Django)
_iso8601_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    # tzinfo must not be available
    r'(?P<tzinfo>Z|(?![+-]\d{2}(?::?\d{2})?))?$'
)


def from_fdsnws_datetime(datestring, use_dateutil=True):
    """
    Parse a datestring from a string specified by the FDSNWS datetime
    specification.

    :param str datestring: String to be parsed
    :param bool use_dateutil: Make use of the :code:`dateutil` package if set
        to :code:`True`
    :returns: Datetime
    :rtype: :py:class:`datetime.datetime`

    See: http://www.fdsn.org/webservices/FDSN-WS-Specifications-1.1.pdf
    """
    IGNORE_TZ = True

    if len(datestring) == 10:
        # only YYYY-mm-dd is defined
        return datetime.datetime.combine(ma.utils.from_iso_date(datestring,
                                         use_dateutil), datetime.time())
    else:
        # from marshmallow
        if not _iso8601_re.match(datestring):
            raise ValueError('Not a valid ISO8601-formatted string.')
        # Use dateutil's parser if possible
        if dateutil_available and use_dateutil:
            return parser.parse(datestring, ignoretz=IGNORE_TZ)
        else:
            # Strip off microseconds and timezone info.
            return datetime.datetime.strptime(datestring[:19],
                                              '%Y-%m-%dT%H:%M:%S')


def fdsnws_isoformat(dt, localtime=False, *args, **kwargs):
    """
    Convert a :py:class:`datetime.datetime` object to a ISO8601 conform string.

    :param datetime.datetime dt: Datetime object to be converted
    :param bool localtime: The parameter is ignored
    :returns: ISO8601 conform datetime string
    :rtype: str
    """
    # ignores localtime parameter
    return dt.isoformat(*args, **kwargs)


def with_exception_handling(func, service_version):
    """
    Method decorator providing a generic exception handling. A well-formatted
    FDSN exception is raised. The exception itself is logged.
    """
    @functools.wraps(func)
    def decorator(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except FDSNHTTPError as err:
            raise err
        except Exception as err:
            # NOTE(damb): Prevents displaying the full stack trace. Just log
            # it.
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.logger.critical('Local Exception: %s' % type(err))
            self.logger.critical(
                'Traceback information: ' + repr(traceback.format_exception(
                    exc_type, exc_value, exc_traceback)))
            raise FDSNHTTPError.create(500, service_version=service_version)

    return decorator


def with_fdsnws_exception_handling(service_version):
    """
    Wrapper of :py:func:`with_exception_handling`.
    """
    return functools.partial(with_exception_handling,
                             service_version=service_version)


def decode_publicid(s):
    """
    Decode a base64 encoded public identifier.

    :param str s: Base64 encoded public identifier
    :returns: Decoded string
    :rtype: str

    :raises: :py:class:`hydws.errors.FDSNHTTPError`
    """
    try:
        return base64.b64decode(s).decode("utf-8")
    except Exception:
        raise FDSNHTTPError.create(400, service_version=__version__)


def make_response(obj, mimetype):
    """
    Return response for :code:`output` and code:`mimetype`.

    :param obj: Object the response is created from
    :param str mimetype: Response mimetype

    :returns: Flask response
    :rtype: :py:class:`werkzeug.wrappers.Response`
    """
    response = _make_response(obj)
    response.headers['Content-Type'] = mimetype
    return response


class DynamicQuery(object):
    """

    Dynamic filtering and of query.

    Example:
     dyn_query = DynamicQuery(query, orm.BoreholeSection)
     dyn_query.filter_query([('m_starttime', 'eq', datetime(...))])

    """

    def __init__(self, query):
        self.query = query

    def operator_attr(self, column, op):
        """
        Returns method associated with an comparison operator.
        If op, op_ or __op__ does not exist, Exception returned.

        :returns type: str.

        """
        try:
            return list(filter(
                lambda e: hasattr(column, e % op),
                    ['%s', '%s_', '__%s__']))[0] % op
        except IndexError:
            raise Exception('Invalid filter operator: %s' % op)

    def filter_query(self, orm_class, query_params, filter_condition,
                     key_suffix="_value"):
        """
        Update self.query based on filter_condition.
        :param filter_condition: list, ie: [(key,operator,value)]
            operator examples:
                eq for ==
                lt for <
                ge for >=
                in for in_
                like for like

            value can be list or a string.
            key must belong in self.orm_class.

        """

        for f in filter_condition:
            try:
                key_basename, op, param_name = f
            except ValueError:
                raise Exception('Invalid filter input: %s' % f)
            if key_suffix:
                key = "{}{}".format(key_basename, key_suffix)
            else:
                key = key_basename
            #put in try statement?
            param_value = query_params.get(param_name)
            if not param_value:
                continue
            # todo: check column type against value type
            # and if they don't match then error?
            try:
                column = getattr(orm_class, key)
            except AttributeError:
                raise Exception('Invalid filter column: %s' % key)
            
            if op == 'in':
                if isinstance(value, list):
                    filt = column.in_(param_value)
                else:
                    filt = column.in_(param_value.split(','))
            else:
                attr = self.operator_attr(column, op)
                #if param_value == 'null':
                #    param_value = None
                filt = getattr(column, attr)(param_value)
            self.query = self.query.filter(filt)


