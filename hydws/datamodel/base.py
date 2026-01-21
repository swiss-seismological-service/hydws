import enum
import functools
import uuid
from datetime import UTC, datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, Float, Integer,
                        String)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base

from config import get_settings

settings = get_settings()


class Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    _oid = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
        autoincrement=True)


ORMBase = declarative_base(cls=Base)


class CreationInfoMixin(object):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`CreationInfo` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """
    creationinfo_author = Column(String)
    creationinfo_authoruri_resourceid = Column(String)
    creationinfo_authoruri_used = Column(Boolean)
    creationinfo_agencyid = Column(String)
    creationinfo_agencyuri_resourceid = Column(String)
    creationinfo_agencyuri_used = Column(Boolean)
    creationinfo_creationtime = \
        Column(DateTime,
               default=lambda: datetime.now(UTC).replace(tzinfo=None))
    creationinfo_version = Column(String)
    creationinfo_copyrightowner = Column(String)
    creationinfo_copyrightowneruri_resourceid = Column(String)
    creationinfo_copyrightowneruri_used = Column(Boolean)
    creationinfo_license = Column(String)


def PublicIDMixin(name=''):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin providing a general
    purpose :code:`publicID` attribute.

    .. note::

        The attribute :code:`publicID` is inherited from `QuakeML
        <https://quake.ethz.ch/quakeml/>`_.
    """
    @declared_attr
    def _publicid(cls):
        return Column(
            'publicid',
            UUID(as_uuid=True),
            nullable=False,
            unique=True,
            default=uuid.uuid4)

    return type(name, (object,), {'publicid': _publicid})


def EpochMixin(name, epoch_type=None):
    """
    Mixin factory for common :code:`Epoch` types.

    Epoch types provide the fields `starttime` and `endtime`.

    :param str name: Name of the class returned
    :param epoch_type: Type of the epoch to be returned. Valid values
        are :code:`None` or :code:`default`, :code:`open` and :code:`finite`.
    :type epoch_type: str or None
    """

    class Boundary(enum.Enum):
        LEFT = enum.auto()
        RIGHT = enum.auto()

    def create_datetime(boundary, **kwargs):

        def _make_datetime(boundary, **kwargs):

            if boundary is Boundary.LEFT:
                name = 'starttime'
            elif boundary is Boundary.RIGHT:
                name = 'endtime'
            else:
                raise ValueError(f'Invalid boundery: {boundary!r}.')

            @declared_attr
            def _datetime(cls):
                return Column(f'{name}', DateTime,
                              **kwargs)

            return _datetime

        return _make_datetime(boundary, **kwargs)

    if epoch_type is None or epoch_type == 'default':
        _func_map = (('starttime', create_datetime(Boundary.LEFT,
                                                   nullable=False)),
                     ('endtime', create_datetime(Boundary.RIGHT)))
    elif epoch_type == 'open':
        _func_map = (('starttime', create_datetime(Boundary.LEFT)),
                     ('endtime', create_datetime(Boundary.RIGHT)))
    elif epoch_type == 'finite':
        _func_map = (('starttime', create_datetime(Boundary.LEFT,
                                                   nullable=False)),
                     ('endtime', create_datetime(Boundary.RIGHT,
                                                 nullable=False)))
    else:
        raise ValueError(f'Invalid epoch_type: {epoch_type!r}.')

    def __dict__(func_map):
        return {f'{attr_name}': attr
                for attr_name, attr in func_map}

    return type(name, (object,), __dict__(_func_map))


UniqueEpochMixin = EpochMixin('Epoch')
UniqueOpenEpochMixin = EpochMixin('Epoch', epoch_type='open')


def QuantityMixin(name, quantity_type,
                  value_nullable=True, primary_key=False, index=False):
    """
    Mixin factory for common :code:`Quantity` types from
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    Quantity types provide the fields:
        - `value`
        - `uncertainty`
        - `loweruncertainty`
        - `upperuncertainty`
        - `confidencelevel`.

    :param str name: Name of the class returned
    :param str quantity_type: Type of the quantity to be returned. Valid values
        are :code:`int`, :code:`real` or rather :code:`float` and :code:`time`.
    """

    column_prefix = f'{name}_'
    column_prefix = column_prefix.lower()

    # Name attribute differently to column key.
    attr_prefix = f'{name}_'.lower()

    def create_value(quantity_type, column_prefix, primary_key):

        def _make_value(sql_type, column_prefix, primary_key):

            @declared_attr
            def _value(cls):
                return Column(f'{column_prefix}value', sql_type,
                              nullable=value_nullable, primary_key=primary_key,
                              index=index)
            return _value

        if 'int' == quantity_type:
            return _make_value(Integer, column_prefix, primary_key)
        elif quantity_type in ('real', 'float'):
            return _make_value(Float, column_prefix, primary_key)
        elif 'time' == quantity_type:
            return _make_value(DateTime, column_prefix, primary_key)

        raise ValueError(f'Invalid quantity_type: {quantity_type}')

    @declared_attr
    def _uncertainty(cls):
        return Column(f'{column_prefix}uncertainty', Float)

    @declared_attr
    def _lower_uncertainty(cls):
        return Column(f'{column_prefix}loweruncertainty', Float)

    @declared_attr
    def _upper_uncertainty(cls):
        return Column(f'{column_prefix}upperuncertainty', Float)

    @declared_attr
    def _confidence_level(cls):
        return Column(f'{column_prefix}confidencelevel', Float)

    _func_map = (('value',
                  create_value(quantity_type, column_prefix, primary_key)),
                 ('uncertainty', _uncertainty),
                 ('loweruncertainty', _lower_uncertainty),
                 ('upperuncertainty', _upper_uncertainty),
                 ('confidencelevel', _confidence_level))

    def __dict__(func_map, attr_prefix):

        return {f'{attr_prefix}{attr_name}': attr
                for attr_name, attr in func_map}

    return type(name, (object,), __dict__(_func_map, attr_prefix))


FloatQuantityMixin = functools.partial(QuantityMixin,
                                       quantity_type='float')
RealQuantityMixin = FloatQuantityMixin
IntegerQuantityMixin = functools.partial(QuantityMixin,
                                         quantity_type='int')
TimeQuantityMixin = functools.partial(QuantityMixin,
                                      quantity_type='time')
