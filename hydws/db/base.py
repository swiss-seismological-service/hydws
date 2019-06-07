"""
.. module:: base
   :synopsis: HYDWS datamodel ORM entity de-/serialization facilities.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""


import datetime
import enum
import functools

from sqlalchemy import (Column, Boolean, Integer, Float, String, DateTime,
                        Enum)
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
# XXX(damb): Within the mixins below the QML type *ResourceReference* (i.e. an
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

# XXX No seperate column name defined, use parent name.
# It should only be accessed on orm side through attribute name.
def _create_used(parent_prefix=None):
    @declared_attr
    def _used(cls):
        return Column(f'{PREFIX}{parent_prefix}used', Boolean, nullable=False,
                      default=False)

    return {f'{parent_prefix}used': _used}


def _create_resourceidentifier_map(parent_prefix=None, column_prefix=None,
                                   used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    @declared_attr
    def _resourceid(cls):
        return Column(f'{column_prefix}resourceid', String)
    func_map = [(f'{parent_prefix}resourceid', _resourceid), ]

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_resourcelocator_map(parent_prefix=None, column_prefix=None,
                                used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    @declared_attr
    def _resourcelocator(cls):
        return Column(f'{column_prefix}resourcelocator', String)
    func_map = [(f'{parent_prefix}resourcelocator', _resourcelocator), ]

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_creationinfo_map(parent_prefix=None, column_prefix=None,
                             used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    @declared_attr
    def _author(cls):
        return Column(f'{column_prefix}author', String)
    func_map = [(f'{parent_prefix}author', _author), ]
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}authoruri_',
            used=used).items())

    @declared_attr
    def _agencyid(cls):
        return Column(f'{column_prefix}agencyid', String)
    func_map.append((f'{parent_prefix}agencyid', _agencyid))
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}agencyuri_',
            used=used).items())

    @declared_attr
    def _creationtime(cls):
        return Column(f'{column_prefix}creationtime', DateTime)
    func_map.append((f'{parent_prefix}creationtime', _creationtime))

    @declared_attr
    def _version(cls):
        return Column(f'{column_prefix}version', String)
    func_map.append((f'{parent_prefix}version', _version))

    @declared_attr
    def _copyrightowner(cls):
        return Column(f'{column_prefix}copyrightowner', String)
    func_map.append((f'{parent_prefix}copyrightowner', _copyrightowner))
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}copyrightowneruri_',
            used=used).items())

    @declared_attr
    def _license(cls):
        return Column(f'{column_prefix}license', String)
    func_map.append((f'{parent_prefix}license', _license))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_domtypeuri_map(parent_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}uri_',
            used=False).items())

    @declared_attr
    def _type(cls):
        return Column(f'{column_prefix}type', String)
    func_map.append((f'{parent_prefix}type', _type))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_languagecodeuri_map(parent_prefix=None, column_prefix=None,
                                used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}uri_',
            used=False).items())

    @declared_attr
    def _code(cls):
        return Column(f'{column_prefix}code', String)
    func_map.append((f'{parent_prefix}code', _code))

    @declared_attr
    def _language(cls):
        return Column(f'{column_prefix}language', String)
    func_map.append((f'{parent_prefix}language', _language))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_countrycodeuri_map(parent_prefix=None, column_prefix=None,
                               used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}uri_',
            used=False).items())

    @declared_attr
    def _code(cls):
        return Column(f'{column_prefix}code', String)
    func_map.append((f'{parent_prefix}code', _code))

    @declared_attr
    def _country(cls):
        return Column(f'{column_prefix}country', String)
    func_map.append((f'{parent_prefix}country' , _country))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_author_map(parent_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    func_map = []
    func_map.extend(
        _create_person_map(
            parent_prefix=f'{parent_prefix}person_',
            used=False).items())

    func_map.extend(
        _create_personalaffiliatation_map(
            parent_prefix=f'{parent_prefix}affiliation_',
            used=used).items())

    func_map.extend(
        _create_personalaffiliatation_map(
            parent_prefix=f'{parent_prefix}alternateaffiliation_',
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}mbox_',
            used=used).items())

    func_map.extend(
        _create_comment_map(
            parent_prefix=f'{parent_prefix}comment_',
            used=used).items())

    @declared_attr
    def _positioninauthorlist(cls):
        # XXX(damb): Unfortunately, the constraint that this value must be
        # positive must be defined by means of __table_args__
        # (see: https://docs.sqlalchemy.org/en/13/core/constraints.html#
        #  setting-up-constraints-when-using-the-declarative-orm-extension)
        return Column(f'{column_prefix}positioninauthorlist', Integer)

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_person_map(parent_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    @declared_attr
    def _name(cls):
        return Column(f'{column_prefix}name', String)
    func_map = [(f'{column_prefix}name', _name)]

    @declared_attr
    def _givenname(cls):
        return Column(f'{column_prefix}givenname', String)
    func_map.append((f'{parent_prefix}givenname', _givenname))

    @declared_attr
    def _familyname(cls):
        return Column(f'{column_prefix}familyname', String)
    func_map.append((f'{parent_prefix}familyname', _familyname))

    @declared_attr
    def _title(cls):
        return Column(f'{column_prefix}title', String)
    func_map.append((f'{parent_prefix}title', _title))

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}personid_',
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}alternatepersonid_',
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}mbox_',
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}phone_',
            used=used).items())

    func_map.extend(
        _create_resourcelocator_map(
            parent_prefix=f'{parent_prefix}homepage_',
            used=used).items())

    func_map.extend(
        _create_resourcelocator_map(
            parent_prefix=f'{parent_prefix}workplacehomepage_',
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_personalaffiliatation_map(parent_prefix=None, column_prefix=None,
                                      used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    func_map = []
    func_map.extend(
        _create_institution_map(
            parent_prefix=f'{parent_prefix}institution_',
            used=used).items())

    @declared_attr
    def _department(cls):
        return Column(f'{column_prefix}department', String)
    func_map.append((f'{parent_prefix}department', _department))

    @declared_attr
    def _function(cls):
        return Column(f'{column_prefix}function', String)
    func_map.append((f'{parent_prefix}function', _function))

    func_map.extend(
        _create_comment_map(
            parent_prefix=f'{parent_prefix}comment_',
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_comment_map(parent_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    @declared_attr
    def _comment(cls):
        return Column(f'{column_prefix}comment', String)
    func_map = [(f'{parent_prefix}comment', _comment), ]

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}id_',
            used=used).items())

    func_map.extend(
        _create_creationinfo_map(
            parent_prefix=f'{parent_prefix}creationinfo_',
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_institution_map(parent_prefix=None, column_prefix=None,
                            used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    @declared_attr
    def _name(cls):
        return Column(f'{column_prefix}name', String)
    func_map = [(f'{parent_prefix}name', _name), ]

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}identifier_',
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}mbox_',
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}phone_',
            used=used).items())

    func_map.extend(
        _create_resourcelocator_map(
            parent_prefix=f'{parent_prefix}homepage_',
            used=used).items())

    func_map.extend(
        _create_postaladdress_map(
            parent_prefix=f'{parent_prefix}postaladdress_',
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_postaladdress_map(parent_prefix=None, column_prefix=None,
                              used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'
    @declared_attr
    def _streetaddress(cls):
        return Column(f'{column_prefix}streetaddress', String)
    func_map = [(f'{parent_prefix}streetaddress', _streetaddress), ]

    @declared_attr
    def _locality(cls):
        return Column(f'{column_prefix}locality', String)
    func_map.append((f'{parent_prefix}locality', _locality))

    @declared_attr
    def _postalcode(cls):
        return Column(f'{column_prefix}postalcode', String)
    func_map.append((f'{parent_prefix}postalcode', _postalcode))

    func_map.extend(
        _create_countrycodeuri_map(
            parent_prefix=f'{parent_prefix}country_',
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def _create_literaturesource_map(parent_prefix=None, column_prefix=None,
                                 used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if PREFIX:
        column_prefix = f'{PREFIX}{column_prefix}'

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix=f'{parent_prefix}identifier_',
            used=used).items())

    # QuakeML: DOMTypeURI
    func_map.extend(
        _create_domtypeuri_map(
            parent_prefix=f'{parent_prefix}type_',
            used=used).items())

    # QuakeML: BibtexEntryType
    @declared_attr
    def _bibtextype(cls):
        return Column(f'{column_prefix}bibtextype', Enum(EBibtexEntryType))
    func_map.append((f'{parent_prefix}bibtextype', _bibtextype))

    if used:
        func_map.extend(_create_used(
            parent_prefix=f'{parent_prefix}bibtextype_').items())

    # QuakeML: LanguageCodeURI
    func_map.extend(
        _create_languagecodeuri_map(
            parent_prefix=f'{parent_prefix}type_',
            used=used).items())

    # QuakeML: Author
    func_map.extend(
        _create_author_map(
            parent_prefix=f'{parent_prefix}creator_',
            used=used).items())

    @declared_attr
    def _title(cls):
        return Column(f'{column_prefix}title', String)
    func_map.append((f'{parent_prefix}title', _title))

    @declared_attr
    def _author(cls):
        return Column(f'{column_prefix}author', String)
    func_map.append((f'{parent_prefix}author', _author))

    @declared_attr
    def _editor(cls):
        return Column(f'{column_prefix}editor', String)
    func_map.append((f'{parent_prefix}editor', _editor))

    @declared_attr
    def _bibliographiccitation(cls):
        return Column(f'{column_prefix}bibliographiccitation', String)
    func_map.append((f'{parent_prefix}bibliographiccitation',
                     _bibliographiccitation))

    @declared_attr
    def _date(cls):
        return Column(f'{column_prefix}date', DateTime)
    func_map.append((f'{parent_prefix}date', _date))

    @declared_attr
    def _booktitle(cls):
        return Column(f'{column_prefix}booktitle', String)
    func_map.append((f'{parent_prefix}booktitle', _booktitle))

    @declared_attr
    def _volume(cls):
        return Column(f'{column_prefix}volume', String)
    func_map.append((f'{parent_prefix}volume', _volume))

    @declared_attr
    def _number(cls):
        return Column(f'{column_prefix}number', String)
    func_map.append((f'{parent_prefix}number', _number))

    @declared_attr
    def _series(cls):
        return Column(f'{column_prefix}series', String)
    func_map.append((f'{parent_prefix}series', _series))

    @declared_attr
    def _issue(cls):
        return Column(f'{column_prefix}issue', String)
    func_map.append((f'{parent_prefix}issue', _issue))

    @declared_attr
    def _year(cls):
        return Column(f'{column_prefix}year', String)
    func_map.append((f'{parent_prefix}year', _year))

    @declared_attr
    def _edition(cls):
        return Column(f'{column_prefix}edition', String)
    func_map.append((f'{parent_prefix}edition', _edition))

    @declared_attr
    def _startpage(cls):
        return Column(f'{column_prefix}startpage', String)
    func_map.append((f'{parent_prefix}startpage', _startpage))

    @declared_attr
    def _endpage(cls):
        return Column(f'{column_prefix}endpage', String)
    func_map.append((f'{parent_prefix}endpage', _endpage))

    @declared_attr
    def _publisher(cls):
        return Column(f'{column_prefix}publisher', String)
    func_map.append((f'{parent_prefix}publisher', _publisher))

    @declared_attr
    def _address(cls):
        return Column(f'{column_prefix}address', String)
    func_map.append((f'{parent_prefix}address', _address))

    @declared_attr
    def _rights(cls):
        return Column(f'{column_prefix}rights', String)
    func_map.append((f'{parent_prefix}rights', _rights))

    @declared_attr
    def _rightsholder(cls):
        return Column(f'{column_prefix}rightsholder', String)
    func_map.append((f'{parent_prefix}rightsholder', _rightsholder))

    @declared_attr
    def _accessrights(cls):
        return Column(f'{column_prefix}accessrights', String)
    func_map.append((f'{parent_prefix}accessrights', _accessrights))

    @declared_attr
    def _license(cls):
        return Column(f'{column_prefix}license', String)
    func_map.append((f'{parent_prefix}license', _license))

    @declared_attr
    def _publicationstatus(cls):
        return Column(f'{column_prefix}publicationstatus', String)
    func_map.append((f'{parent_prefix}publicationstatus', _publicationstatus))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix).items())

    return {f'{attr_name}': attr
            for attr_name, attr in func_map}


def CreationInfoMixin(name, parent_prefix=None, column_prefix=None, used=True):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`CreationInfo` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """
    if not parent_prefix:
        parent_prefix = ''

    return type(name, (object,),
                _create_creationinfo_map(parent_prefix=parent_prefix, used=used))


def LiteratureSourceMixin(name, parent_prefix=None, column_prefix=None, used=True):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`LiteratureSource` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """

    if not parent_prefix:
        parent_prefix = ''

    return type(name, (object,),
                _create_literaturesource_map(parent_prefix=parent_prefix, used=used))


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
