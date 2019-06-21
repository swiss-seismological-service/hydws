"""
.. module:: base
   :synopsis: HYDWS datamodel ORM entity de-/serialization facilities.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""


import datetime
import enum
import functools

from sqlalchemy.orm import relationship
from sqlalchemy import (Column, Boolean, Integer, Float, String, DateTime,
                        Enum)
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from hydws.server import settings

try:
    PREFIX = settings.HYDWS_PREFIX
except AttributeError:
    PREFIX = None


class Base(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    _oid = Column(Integer, primary_key=True)


ORMBase = declarative_base(cls=Base)


# ----------------------------------------------------------------------------
# XXX(damb): Within the mixins below the QML type *ResourceReference* (i.e. a
# URI) is implemented as sqlalchemy.String

class AutoName(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


class EBibtexEntryType(AutoName):

    ARTICLE = enum.auto()
    BOOK = enum.auto()
    BOOKLET = enum.auto()
    CONFERENCE = enum.auto()
    INBOOK = enum.auto()
    INCOLLECTION = enum.auto()
    INPROCEEDINGS = enum.auto()
    MANUAL = enum.auto()
    MASTERTHESIS = enum.auto()
    MISC = enum.auto()
    PHDTHESIS = enum.auto()
    PROCEEDINGS = enum.auto()
    TECHREPORT = enum.auto()
    UNPUBLISHED = enum.auto()


class ResourceIdentifier(ORMBase):

    resourceid = Column(f'{PREFIX}resourceid', String)


class ResourceLocator(ORMBase):

    resourcelocator = Column(f'{PREFIX}resourcelocator', String)


class CreationInfo(ORMBase):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`CreationInfo` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """
    creationtime = Column(f'{PREFIX}creationtime', DateTime)
    version = Column(f'{PREFIX}version', String)
    copyrightowner = Column(f'{PREFIX}copyrightowner', String)
    license = Column(f'{PREFIX}license', String)
    author = Column(f'{PREFIX}author', String)
    agencyid = Column(f'{PREFIX}agencyid', String)
    agencyid = Column(f'{PREFIX}agencyid', String)

    _authoruri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _authoruri = relationship("ResourceIdentifier",
                              foreign_keys=[_authoruri_oid])

    _agencyuri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _agencyuri = relationship("ResourceIdentifier",
                              foreign_keys=[_agencyuri_oid])

    _copyrightowneruri_oid = Column(Integer,
                                    ForeignKey('resourceidentifier._oid'))
    _copyrightowneruri = relationship("ResourceIdentifier",
                                      foreign_keys=[_copyrightowneruri_oid])


class DomTypeURI(ORMBase):

    type = Column(f'{PREFIX}type', String)

    _uri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _uri = relationship("ResourceIdentifier", foreign_keys=[_uri_oid])


class LanguageCodeURI(ORMBase):

    language = Column(f'{PREFIX}language', String)
    code = Column(f'{PREFIX}code', String)

    _uri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _uri = relationship("ResourceIdentifier", foreign_keys=[_uri_oid])


class CountryCodeURI(ORMBase):

    _postaladdress_oid = Column(Integer, ForeignKey('postaladdress._oid'))
    code = Column(f'{PREFIX}code', String)
    country = Column(f'{PREFIX}country', String)

    _uri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _uri = relationship("ResourceIdentifier", foreign_keys=[_uri_oid])


class Author(ORMBase):

    # XXX(damb): Unfortunately, the constraint that this value must be
    # positive must be defined by means of __table_args__
    # (see: https://docs.sqlalchemy.org/en/13/core/constraints.html#
    #  setting-up-constraints-when-using-the-declarative-orm-extension)
    positioninauthorlist = Column(f'{PREFIX}positioninauthorlist', Integer)

    
    _person_oid = Column(Integer, ForeignKey('person._oid'))
    _person = relationship("Person", foreign_keys=[_person_oid])

    _affiliation_oid = Column(Integer, ForeignKey('personalaffiliation._oid'))
    _affiliation = relationship(
        "PersonalAffiliation", foreign_keys=[_affiliation_oid])

    _alternateaffiliation_oid = Column(
        Integer, ForeignKey('personalaffiliation._oid'))
    _alternateaffiliation = relationship(
        "PersonalAffiliation", foreign_keys=[_alternateaffiliation_oid])

    _mbox_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _mbox = relationship("ResourceIdentifier", foreign_keys=[_mbox_oid])

    _comment_oid = Column(Integer, ForeignKey('comment._oid'))
    _comment = relationship("Comment", foreign_keys=[_comment_oid])


class Person(ORMBase):

    name = Column(f'{PREFIX}name', String)
    givenname = Column(f'{PREFIX}givenname', String)
    familyname = Column(f'{PREFIX}familyname', String)
    title = Column(f'{PREFIX}title', String)

    _alternatepersonid_oid = Column(
        Integer, ForeignKey('resourceidentifier._oid'))
    _alternatepersonid = relationship(
        "ResourceIdentifier", foreign_keys=[_alternatepersonid_oid])

    _personid_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _personid = relationship(
        "ResourceIdentifier", foreign_keys=[_personid_oid])

    _mbox_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _mbox = relationship("ResourceIdentifier", foreign_keys=[_mbox_oid])

    _phone_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _phone = relationship("ResourceIdentifier", foreign_keys=[_phone_oid])

    _homepage_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _homepage = relationship(
        "ResourceIdentifier", foreign_keys=[_homepage_oid])

    _workplacehomepage_oid = Column(
        Integer, ForeignKey('resourceidentifier._oid'))
    _workplacehomepage = relationship(
        "ResourceIdentifier", foreign_keys=[_workplacehomepage_oid])


class PersonalAffiliation(ORMBase):

    department = Column(f'{PREFIX}department', String)
    function = Column(f'{PREFIX}function', String)

    _institution_oid = Column(Integer, ForeignKey('institution._oid'))
    _institution = relationship(
        "Institution", foreign_keys=[_institution_oid])

    _comment_oid = Column(Integer, ForeignKey('comment._oid'))
    _comment= relationship("Comment", foreign_keys=[_comment_oid])


class Comment(ORMBase):

    comment = Column(f'{PREFIX}comment', String)

    _id_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _id = relationship("ResourceIdentifier",  foreign_keys=[_id_oid])

    _creationinfo_oid = Column(Integer, ForeignKey('creationinfo._oid'))
    _creationinfo = relationship(
        "CreationInfo", foreign_keys=[_creationinfo_oid])


class Institution(ORMBase):

    name = Column(f'{PREFIX}name', String)

    _identifier_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _identifier = relationship("ResourceIdentifier", foreign_keys=[_identifier_oid])

    _phone_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _phone = relationship("ResourceIdentifier", foreign_keys=[_phone_oid])

    _homepage_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _homepage = relationship("ResourceIdentifier", foreign_keys=[_homepage_oid])

    _postaladdress_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _postaladdress = relationship("ResourceIdentifier", foreign_keys=[_postaladdress_oid])

    _mbox_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _mbox = relationship("ResourceIdentifier", foreign_keys=[_mbox_oid])


class PostalAddress(ORMBase):

    streetaddress = Column(f'{PREFIX}streetaddress', String)
    locality = Column(f'{PREFIX}locality', String)
    postalcode = Column(f'{PREFIX}postalcode', String)

    _country_oid = Column(Integer, ForeignKey('countrycodeuri._oid'))
    _country= relationship("CountryCodeURI", foreign_keys=[_country_oid])


class Creator(ORMBase):

    _person_oid = Column(Integer, ForeignKey('person._oid'))
    _person = relationship("Person", foreign_keys=[_person_oid])

    _affiliation_oid = Column(Integer, ForeignKey('personalaffiliation._oid'))
    _affiliation = relationship("PersonalAffiliation", foreign_keys=[_affiliation_oid])

    _alternateaffiliation_oid = Column(Integer, ForeignKey('personalaffiliation._oid'))
    _alternateaffiliation = relationship("PersonalAffiliation", foreign_keys=[_alternateaffiliation_oid])

    _mbox_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _mbox = relationship("ResourceIdentifier", foreign_keys=[_mbox_oid])

    _comment_oid = Column(Integer, ForeignKey('comment._oid'))
    _comment = relationship("Comment", foreign_keys=[_comment_oid])


class LiteratureSource(ORMBase):

    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`LiteratureSource` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """

    _identifier_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _identifier = relationship("ResourceIdentifier", foreign_keys=[_identifier_oid])

    _creator_oid = Column(Integer, ForeignKey('author._oid'))
    _creator = relationship("Author", foreign_keys=[_creator_oid])

    _type_oid = Column(Integer, ForeignKey('languagecodeuri._oid'))
    _type = relationship("LanguageCodeURI", foreign_keys=[_type_oid])

    bibtextype = Column(f'{PREFIX}bibtextype', Enum(EBibtexEntryType))
    title = Column(f'{PREFIX}title', String)
    author = Column(f'{PREFIX}author', String)
    editor = Column(f'{PREFIX}editor', String)
    bibliographiccitation = Column(f'{PREFIX}bibliographiccitation', String)
    date = Column(f'{PREFIX}date', DateTime)
    booktitle = Column(f'{PREFIX}booktitle', String)
    volume = Column(f'{PREFIX}volume', String)
    number = Column(f'{PREFIX}number', String)
    series = Column(f'{PREFIX}series', String)
    issue = Column(f'{PREFIX}issue', String)
    year = Column(f'{PREFIX}year', String)
    edition = Column(f'{PREFIX}edition', String)
    startpage = Column(f'{PREFIX}startpage', String)
    endpage = Column(f'{PREFIX}endpage', String)
    publisher = Column(f'{PREFIX}publisher', String)
    address = Column(f'{PREFIX}address', String)
    rights = Column(f'{PREFIX}rights', String)
    rightsholder = Column(f'{PREFIX}rightsholder', String)
    accessrights =  Column(f'{PREFIX}accessrights', String)
    license = Column(f'{PREFIX}license', String)
    publicationstatus = Column(f'{PREFIX}publicationstatus', String)


def PublicIDMixin(name='', parent_prefix=None, column_prefix=None):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin providing a general
    purpose :code:`publicID` attribute.

    .. note::

        The attribute :code:`publicID` is inherited from `QuakeML
        <https://quake.ethz.ch/quakeml/>`_.
    """
    if not parent_prefix:
        parent_prefix = name
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    @declared_attr
    def _publicid(cls):
        return Column(f'{column_prefix}publicid', String, nullable=False)

    return type(name, (object,), {f'{parent_prefix}publicid': _publicid})

def EpochMixin(name, epoch_type=None, parent_prefix=None):
    """
    Mixin factory for common :code:`Epoch` types from
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    Epoch types provide the fields `starttime` and `endtime`. Note, that a
    `column_prefix` may be prepended.

    :param str name: Name of the class returned
    :param epoch_type: Type of the epoch to be returned. Valid values
        are :code:`None` or :code:`default`, :code:`open` and :code:`finite`.
    :type epoch_type: str or None
    :param column_prefix: Prefix used for DB columns. If :code:`None`, then
        :code:`name` with an appended underscore :code:`_` is used. Capital
        letters are converted to lowercase.
    :type column_prefix: str or None

    The usage of :py:func:`EpochMixin` is illustrated bellow:

    .. code::

        import datetime

        # define a ORM mapping using the "Epoch" mixin factory
        class MyObject(EpochMixin('epoch'), ORMBase):

            def __repr__(self):
                return \
                    '<MyObject(epoch_starttime={}, epoch_endtime={})>'.format(
                        self.epoch_starttime, self.epoch_endtime)


        # create instance of "MyObject"
        my_obj = MyObject(epoch_starttime=datetime.datetime.utcnow())

    """
    if not parent_prefix:
        parent_prefix = ''
    column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    column_prefix = column_prefix.lower()

    class Boundery(enum.Enum):
        LEFT = enum.auto()
        RIGHT = enum.auto()

    def create_datetime(boundery, column_prefix, **kwargs):

        def _make_datetime(boundery, **kwargs):

            if boundery is Boundery.LEFT:
                name = 'starttime'
            elif boundery is Boundery.RIGHT:
                name = 'endtime'
            else:
                raise ValueError(f'Invalid boundery: {boundery!r}.')

            @declared_attr
            def _datetime(cls):
                return Column(f'{column_prefix}{name}', DateTime,
                              **kwargs)

            return _datetime

        return _make_datetime(boundery, **kwargs)

    if epoch_type is None or epoch_type == 'default':
        _func_map = (('starttime', create_datetime(Boundery.LEFT,
                                                   column_prefix,
                                                   nullable=False)),
                     ('endtime', create_datetime(Boundery.RIGHT,
                                                 column_prefix)))
    elif epoch_type == 'open':
        _func_map = (('starttime', create_datetime(Boundery.LEFT,
                                                   column_prefix)),
                     ('endtime', create_datetime(Boundery.RIGHT,
                                                 column_prefix)))
    elif epoch_type == 'finite':
        _func_map = (('starttime', create_datetime(Boundery.LEFT,
                                                   column_prefix,
                                                   nullable=False)),
                     ('endtime', create_datetime(Boundery.RIGHT,
                                                 column_prefix,
                                                 nullable=False)))
    else:
        raise ValueError(f'Invalid epoch_type: {epoch_type!r}.')

    def __dict__(func_map, attr_prefix):
        return {f'{attr_prefix}{attr_name}': attr
                for attr_name, attr in func_map}

    return type(name, (object,), __dict__(_func_map, parent_prefix))


UniqueEpochMixin = EpochMixin('Epoch')
UniqueOpenEpochMixin = EpochMixin('Epoch', epoch_type='open')


def QuantityMixin(name, quantity_type, column_prefix=None, value_nullable=True):
    """
    Mixin factory for common :code:`Quantity` types from
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    Quantity types provide the fields:
        - `value`
        - `uncertainty`
        - `loweruncertainty`
        - `upperuncertainty`
        - `confidencelevel`.

    Note, that a `column_prefix` may be prepended.

    :param str name: Name of the class returned
    :param str quantity_type: Type of the quantity to be returned. Valid values
        are :code:`int`, :code:`real` or rather :code:`float` and :code:`time`.
    :param column_prefix: Prefix used for DB columns. If :code:`None`, then
        :code:`name` with an appended underscore :code:`_` is used. Capital
        Letters are converted to lowercase.
    :type column_prefix: str or None

    The usage of :py:func:`QuantityMixin` is illustrated bellow:

    .. code::

        # define a ORM mapping using the Quantity mixin factory
        class FooBar(QuantityMixin('foo', 'int'),
                     QuantityMixin('bar', 'real'),
                     ORMBase):

            def __repr__(self):
                return '<FooBar (foo_value=%d, bar_value=%f)>' % (
                    self.foo_value, self.bar_value)


        # create instance of "FooBar"
        foobar = FooBar(foo_value=1, bar_value=2)

    """

    if column_prefix is None:
        column_prefix = f'{name}_'
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'
    column_prefix = column_prefix.lower()

    # Name attribute differently to column key.
    attr_prefix = f'{name}_'.lower()

    def create_value(quantity_type, column_prefix):

        def _make_value(sql_type, column_prefix):

            @declared_attr
            def _value(cls):
                return Column(f'{column_prefix}value', sql_type,
                              nullable=value_nullable)
            return _value

        if 'int' == quantity_type:
            return _make_value(Integer, column_prefix)
        elif quantity_type in ('real', 'float'):
            return _make_value(Float, column_prefix)
        elif 'time' == quantity_type:
            return _make_value(DateTime, column_prefix)

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

    _func_map = (('value', create_value(quantity_type, column_prefix)),
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
