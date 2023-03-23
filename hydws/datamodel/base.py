import enum
import functools

from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Integer,
                        String, create_engine)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import backref, relationship, sessionmaker
from sqlalchemy.schema import MetaData

from config.config import get_settings


def postgresql_url():
    settings = get_settings()
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{settings.DB_USER}:"
        f"{settings.DB_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:"
        f"{settings.PGPORT}/{settings.DB_NAME}")
    return SQLALCHEMY_DATABASE_URL


settings = get_settings()
SQLALCHEMY_DATABASE_URL = postgresql_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)


class Base(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    _oid = Column(Integer, primary_key=True, nullable=False)


ORMBase = declarative_base(cls=Base)


def init_db():
    """
    Initializes the Database.
    All DB modules need to be imported when calling this function.
    """
    ORMBase.metadata.create_all(engine)


def drop_db():
    """Drops all database Tables but leaves the DB itself in place"""
    m = MetaData()
    m.reflect(engine)
    m.drop_all(engine)


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

    resourceid = Column('resourceid', String)


class ResourceLocator(ORMBase):

    resourcelocator = Column('resourcelocator', String)


class CreationInfo(ORMBase):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`CreationInfo` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """
    creationtime = Column('creationtime', DateTime)
    version = Column('version', String)
    copyrightowner = Column('copyrightowner', String)
    license = Column('license', String)
    author = Column('author', String)
    agencyid = Column('agencyid', String)
    agencyid = Column('agencyid', String)

    _authoruri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _authoruri = relationship(
        "ResourceIdentifier", foreign_keys=[_authoruri_oid])

    _agencyuri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _agencyuri = relationship(
        "ResourceIdentifier", foreign_keys=[_agencyuri_oid])

    _copyrightowneruri_oid = Column(Integer,
                                    ForeignKey('resourceidentifier._oid'))
    _copyrightowneruri = relationship(
        "ResourceIdentifier", foreign_keys=[_copyrightowneruri_oid])


class DomTypeURI(ORMBase):

    type = Column('type', String)

    _uri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _uri = relationship(
        "ResourceIdentifier",
        backref=backref("_domtypeuri", uselist=False),
        foreign_keys=[_uri_oid])


class LanguageCodeURI(ORMBase):

    language = Column('language', String)
    code = Column('code', String)

    _uri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _uri = relationship(
        "ResourceIdentifier",
        backref=backref("_languagecodeuri", uselist=False),
        foreign_keys=[_uri_oid])


class CountryCodeURI(ORMBase):

    _postaladdress_oid = Column(Integer, ForeignKey('postaladdress._oid'))
    code = Column('code', String)
    country = Column('country', String)

    _uri_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _uri = relationship(
        "ResourceIdentifier",
        backref=backref(" _countrycodeuri", uselist=False),
        foreign_keys=[_uri_oid])


class Author(ORMBase):
    positioninauthorlist = Column('positioninauthorlist', Integer)

    _person_oid = Column(Integer, ForeignKey('person._oid'))
    _person = relationship(
        "Person",
        backref=backref("_author", uselist=False),
        foreign_keys=[_person_oid])

    _affiliation_oid = Column(Integer, ForeignKey('personalaffiliation._oid'))
    _affiliation = relationship(
        "PersonalAffiliation",
        backref=backref("_author_primaryaffiliation", uselist=False),
        foreign_keys=[_affiliation_oid])

    _alternateaffiliation_oid = Column(
        Integer, ForeignKey('personalaffiliation._oid'))
    _alternateaffiliation = relationship(
        "PersonalAffiliation",
        backref=backref("_author_alternateaffiliation", uselist=False),
        foreign_keys=[_alternateaffiliation_oid])

    _mbox_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _mbox = relationship(
        "ResourceIdentifier",
        backref=backref("_author_mbox", uselist=False),
        foreign_keys=[_mbox_oid])

    _comment_oid = Column(Integer, ForeignKey('comment._oid'))
    _comment = relationship(
        "Comment",
        backref=backref("_author_comment", uselist=False),
        foreign_keys=[_comment_oid])


class Person(ORMBase):

    name = Column('name', String)
    givenname = Column('givenname', String)
    familyname = Column('familyname', String)
    title = Column('title', String)

    _alternatepersonid_oid = Column(
        Integer, ForeignKey('resourceidentifier._oid'))
    _alternatepersonid = relationship(
        "ResourceIdentifier",
        backref=backref("person_alternate", uselist=False),
        foreign_keys=[_alternatepersonid_oid])

    _personid_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _personid = relationship(
        "ResourceIdentifier",
        backref=backref("_person_primary", uselist=False),
        foreign_keys=[_personid_oid])

    _mbox_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _mbox = relationship(
        "ResourceIdentifier",
        backref=backref("_person_mbox", uselist=False),
        foreign_keys=[_mbox_oid])

    _phone_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _phone = relationship(
        "ResourceIdentifier",
        backref=backref("_person_phone", uselist=False),
        foreign_keys=[_phone_oid])

    _homepage_oid = Column(Integer, ForeignKey('resourcelocator._oid'))
    _homepage = relationship(
        "ResourceLocator",
        backref=backref("_person_homepage", uselist=False),
        foreign_keys=[_homepage_oid])

    _workplacehomepage_oid = Column(
        Integer, ForeignKey('resourcelocator._oid'))
    _workplacehomepage = relationship(
        "ResourceLocator",
        backref=backref("_person_workplacehomepage", uselist=False),
        foreign_keys=[_workplacehomepage_oid])


class PersonalAffiliation(ORMBase):

    department = Column('department', String)
    function = Column('function', String)

    _institution_oid = Column(Integer, ForeignKey('institution._oid'))
    _institution = relationship(
        "Institution",
        backref=backref("_personalaffiliation1", uselist=False),
        foreign_keys=[_institution_oid])

    _comment_oid = Column(Integer, ForeignKey('comment._oid'))
    _comment = relationship(
        "Comment",
        backref=backref("_personalaffliation", uselist=False),
        foreign_keys=[_comment_oid])


class Comment(ORMBase):

    comment = Column('comment', String)

    _id_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _id = relationship(
        "ResourceIdentifier", foreign_keys=[_id_oid])

    _creationinfo_oid = Column(Integer, ForeignKey('creationinfo._oid'))
    _creationinfo = relationship(
        "CreationInfo",
        backref=backref("_comment", uselist=False),
        foreign_keys=[_creationinfo_oid])


class Institution(ORMBase):

    name = Column('name', String)

    _identifier_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _identifier = relationship(
        "ResourceIdentifier",
        backref=backref("_institution", uselist=False),
        foreign_keys=[_identifier_oid])

    _phone_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _phone = relationship(
        "ResourceIdentifier",
        backref=backref("_institution_phone", uselist=False),
        foreign_keys=[_phone_oid])

    _homepage_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _homepage = relationship(
        "ResourceIdentifier",
        backref=backref("_institution_homepage", uselist=False),
        foreign_keys=[_homepage_oid])

    _postaladdress_oid = Column(Integer,
                                ForeignKey('resourceidentifier._oid'))
    _postaladdress = relationship(
        "ResourceIdentifier",
        backref=backref("_institution_postaladdress", uselist=False),
        foreign_keys=[_postaladdress_oid])

    _mbox_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _mbox = relationship(
        "ResourceIdentifier",
        backref=backref("_institution_mbox", uselist=False),
        foreign_keys=[_mbox_oid])


class PostalAddress(ORMBase):

    streetaddress = Column('streetaddress', String)
    locality = Column('locality', String)
    postalcode = Column('postalcode', String)

    _country_oid = Column(Integer, ForeignKey('countrycodeuri._oid'))
    _country = relationship(
        "CountryCodeURI",
        backref=backref("_postaladdress", uselist=False),
        foreign_keys=[_country_oid])


class Creator(ORMBase):

    _person_oid = Column(Integer, ForeignKey('person._oid'))
    _person = relationship(
        "Person",
        backref=backref("_creator", uselist=False),
        foreign_keys=[_person_oid])

    _affiliation_oid = Column(Integer, ForeignKey('personalaffiliation._oid'))
    _affiliation = relationship(
        "PersonalAffiliation",
        backref=backref("_creator_primaryaffiliation", uselist=False),
        foreign_keys=[_affiliation_oid])

    _alternateaffiliation_oid = Column(Integer,
                                       ForeignKey('personalaffiliation._oid'))
    _alternateaffiliation = relationship(
        "PersonalAffiliation",
        backref=backref("_creator_alternateaffiliation", uselist=False),
        foreign_keys=[_alternateaffiliation_oid])

    _mbox_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _mbox = relationship(
        "ResourceIdentifier",
        backref=backref("_creator_mbox", uselist=False),
        foreign_keys=[_mbox_oid])

    _comment_oid = Column(Integer, ForeignKey('comment._oid'))
    _comment = relationship(
        "Comment",
        backref=backref("_creator", uselist=False),
        foreign_keys=[_comment_oid])


class LiteratureSource(ORMBase):

    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`LiteratureSource` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """

    _identifier_oid = Column(Integer, ForeignKey('resourceidentifier._oid'))
    _identifier = relationship(
        "ResourceIdentifier",
        backref=backref("_literaturesource", uselist=False),
        foreign_keys=[_identifier_oid])

    _creator_oid = Column(Integer, ForeignKey('author._oid'))
    _creator = relationship(
        "Author",
        backref=backref("_literaturesource", uselist=False),
        foreign_keys=[_creator_oid])

    _type_oid = Column(Integer, ForeignKey('languagecodeuri._oid'))
    _type = relationship(
        "LanguageCodeURI",
        backref=backref("_literaturesource", uselist=False),
        foreign_keys=[_type_oid])

    bibtextype = Column('bibtextype', Enum(EBibtexEntryType))
    title = Column('title', String)
    author = Column('author', String)
    editor = Column('editor', String)
    bibliographiccitation = Column('bibliographiccitation', String)
    date = Column('date', DateTime)
    booktitle = Column('booktitle', String)
    volume = Column('volume', String)
    number = Column('number', String)
    series = Column('series', String)
    issue = Column('issue', String)
    year = Column('year', String)
    edition = Column('edition', String)
    startpage = Column('startpage', String)
    endpage = Column('endpage', String)
    publisher = Column('publisher', String)
    address = Column('address', String)
    rights = Column('rights', String)
    rightsholder = Column('rightsholder', String)
    accessrights = Column('accessrights', String)
    license = Column('license', String)
    publicationstatus = Column('publicationstatus', String)


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
        return Column('publicid', String, nullable=False)

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
                  value_nullable=True, index=False):
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

    def create_value(quantity_type):

        def _make_value(sql_type):

            @declared_attr
            def _value(cls):
                return Column('value', sql_type,
                              nullable=value_nullable)
            return _value

        if 'int' == quantity_type:
            return _make_value(Integer)
        elif quantity_type in ('real', 'float'):
            return _make_value(Float)
        elif 'time' == quantity_type:
            return _make_value(DateTime)

        raise ValueError(f'Invalid quantity_type: {quantity_type}')

    @declared_attr
    def _uncertainty(cls):
        return Column('uncertainty', Float)

    @declared_attr
    def _lower_uncertainty(cls):
        return Column('loweruncertainty', Float)

    @declared_attr
    def _upper_uncertainty(cls):
        return Column('upperuncertainty', Float)

    @declared_attr
    def _confidence_level(cls):
        return Column('confidencelevel', Float)

    _func_map = (('value', create_value(quantity_type)),
                 ('uncertainty', _uncertainty),
                 ('loweruncertainty', _lower_uncertainty),
                 ('upperuncertainty', _upper_uncertainty),
                 ('confidencelevel', _confidence_level))

    def __dict__(func_map):

        return {f'{attr_name}': attr
                for attr_name, attr in func_map}

    return type(name, (object,), __dict__(_func_map))


FloatQuantityMixin = functools.partial(QuantityMixin,
                                       quantity_type='float')
RealQuantityMixin = FloatQuantityMixin
IntegerQuantityMixin = functools.partial(QuantityMixin,
                                         quantity_type='int')
TimeQuantityMixin = functools.partial(QuantityMixin,
                                      quantity_type='time',
                                      index=False)
