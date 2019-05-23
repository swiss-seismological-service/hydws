"""
General purpose datamodel ORM facilities.
"""
import datetime
import enum
import functools

from sqlalchemy import (Column, Boolean, Integer, Float, String, DateTime,
                        Enum)
from sqlalchemy.ext.declarative import declared_attr, declarative_base


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


def _create_used(column_prefix=None, key_prefix=None):
    @declared_attr
    def _used(cls):
        #if not column_prefix:
        #    column_prefix = ''
        #if key_prefix:
        #    column_prefix = '{}{}'.format(key_prefix, column_prefix)

        return Column('%s%sused' % (key_prefix, column_prefix), Boolean, nullable=False,
                      default=False)

    return {'{}{}'.format(column_prefix, 'used'): _used}


def _create_resourceidentifier_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix
    
    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    @declared_attr
    def _resourceid(cls):
        return Column('%sresourceid' % column_prefix, String)
    func_map = [('resourceid', _resourceid), ]

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_resourcelocator_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    @declared_attr
    def _resourcelocator(cls):
        return Column('%sresourcelocator' % column_prefix, String)
    func_map = [('resourcelocator', _resourcelocator), ]

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_creationinfo_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    @declared_attr
    def _author(cls):
        return Column('%sauthor' % column_prefix, String)
    func_map = [('author', _author), ]
    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%sauthoruri_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    @declared_attr
    def _agencyid(cls):
        return Column('%sagencyid' % column_prefix, String)
    func_map.append(('agencyid', _agencyid))
    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%sagencyuri_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    @declared_attr
    def _creationtime(cls):
        return Column('%screationtime' % column_prefix, DateTime,
                      default=datetime.datetime.utcnow())
    func_map.append(('creationtime', _creationtime))

    @declared_attr
    def _version(cls):
        return Column('%sversion' % column_prefix, String)
    func_map.append(('version', _version))

    @declared_attr
    def _copyrightowner(cls):
        return Column('%scopyrightowner' % column_prefix, String)
    func_map.append(('copyrightowner', _copyrightowner))
    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%scopyrightowneruri_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    @declared_attr
    def _license(cls):
        return Column('%slicense' % column_prefix, String)
    func_map.append(('license', _license))

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_domtypeuri_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%suri_' % attr_prefix, key_prefix=key_prefix,
            used=False).items())

    @declared_attr
    def _type(cls):
        return Column('%stype' % column_prefix, String)
    func_map.append(('type', _type))

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_languagecodeuri_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%suri_' % attr_prefix, key_prefix=key_prefix,
            used=False).items())

    @declared_attr
    def _code(cls):
        return Column('%scode' % column_prefix, String)
    func_map.append(('code', _code))

    @declared_attr
    def _language(cls):
        return Column('%slanguage' % column_prefix, String)
    func_map.append(('language', _language))

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_countrycodeuri_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%suri_' % attr_prefix, key_prefix=key_prefix,
            used=False).items())

    @declared_attr
    def _code(cls):
        return Column('%scode' % column_prefix, String)
    func_map.append(('code', _code))

    @declared_attr
    def _country(cls):
        return Column('%scountry' % column_prefix, String)
    func_map.append(('country', _country))

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_author_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_person_map(
            column_prefix='%sperson_' % attr_prefix, key_prefix=key_prefix,
            used=False).items())

    func_map.extend(
        _create_personalaffiliatation_map(
            column_prefix='%saffiliation_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_personalaffiliatation_map(
            column_prefix='%salternateaffiliation_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%smbox_' % attr_prefix, key_prefix=key_prefix,# XXX don't use column prefix
            used=used).items())

    func_map.extend(
        _create_comment_map(
            column_prefix='%scomment_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    @declared_attr
    def _positioninauthorlist(cls):
        # XXX(damb): Unfortunately, the constraint that this value must be
        # positive must be defined by means of __table_args__
        # (see: https://docs.sqlalchemy.org/en/13/core/constraints.html#
        #  setting-up-constraints-when-using-the-declarative-orm-extension)
        return Column('%spositioninauthorlist' % column_prefix, Integer)

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_person_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    @declared_attr
    def _name(cls):
        return Column('%sname' % column_prefix, String)
    func_map = [('name', _name), ]

    @declared_attr
    def _givenname(cls):
        return Column('%sgivenname' % column_prefix, String)
    func_map.append(('givenname', _givenname))

    @declared_attr
    def _familyname(cls):
        return Column('%sfamilyname' % column_prefix, String)
    func_map.append(('familyname', _familyname))

    @declared_attr
    def _title(cls):
        return Column('%stitle' % column_prefix, String)
    func_map.append(('title', _title))

    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%spersonid_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%salternatepersonid_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%smbox_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%sphone_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_resourcelocator_map(
            column_prefix='%shomepage_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_resourcelocator_map(
            column_prefix='%sworkplacehomepage_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_personalaffiliatation_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_institution_map(
            column_prefix='%sinstutution_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    @declared_attr
    def _department(cls):
        return Column('%sdepartment' % column_prefix, String)
    func_map.append(('department', _department))

    @declared_attr
    def _function(cls):
        return Column('%sfunction' % column_prefix, String)
    func_map.append(('function', _function))

    func_map.extend(
        _create_comment_map(
            column_prefix='%scomment_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_comment_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    @declared_attr
    def _comment(cls):
        return Column('%scomment' % column_prefix, String)
    func_map = [('comment', _comment), ]

    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%sid_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_creationinfo_map(
            column_prefix='%screationinfo_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_institution_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    @declared_attr
    def _name(cls):
        return Column('%sname' % column_prefix, String)
    func_map = [('name', _name), ]

    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%sidentifier_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%smbox_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%sphone_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_resourcelocator_map(
            column_prefix='%shomepage_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    func_map.extend(
        _create_postaladdress_map(
            column_prefix='%spostaladdress_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_postaladdress_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)
    @declared_attr
    def _streetaddress(cls):
        return Column('%sstreetaddress' % column_prefix, String)
    func_map = [('streetaddress', _streetaddress), ]

    @declared_attr
    def _locality(cls):
        return Column('%slocality' % column_prefix, String)
    func_map.append(('locality', _locality))

    @declared_attr
    def _postalcode(cls):
        return Column('%spostalcode' % column_prefix, String)
    func_map.append(('postalcode', _postalcode))

    func_map.extend(
        _create_countrycodeuri_map(
            column_prefix='%scountry_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())

    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def _create_literaturesource_map(column_prefix=None, key_prefix=None, used=True):

    if not column_prefix:
        column_prefix = ''
    attr_prefix = column_prefix

    if key_prefix:
        column_prefix = '%s%s' % (key_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            column_prefix='%sidentifier_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    # QuakeML: DOMTypeURI
    func_map.extend(
        _create_domtypeuri_map(
            column_prefix='%stype_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    # QuakeML: BibtexEntryType
    @declared_attr
    def _bibtextype(cls):
        return Column('%sbibtextype' % column_prefix, Enum(EBibtexEntryType))
    func_map.append(('bibtextype', _bibtextype))

    if used:
        func_map.extend(_create_used(
            column_prefix='%sbibtextype_' % attr_prefix, key_prefix=key_prefix).items())

    # QuakeML: LanguageCodeURI
    func_map.extend(
        _create_languagecodeuri_map(
            column_prefix='%stype_' % attr_prefix, key_prefix=key_prefix,
            used=used).items())

    # QuakeML: Author
    func_map.extend(
        _create_author_map(
            column_prefix='%screator_' % attr_prefix, key_prefix=key_prefix,# XXX don't use column prefix
            used=used).items())

    @declared_attr
    def _title(cls):
        return Column('%stitle' % column_prefix, String)
    func_map.append(('title', _title))

    @declared_attr
    def _author(cls):
        return Column('%sauthor' % column_prefix, String)
    func_map.append(('author', _author))

    @declared_attr
    def _editor(cls):
        return Column('%seditor' % column_prefix, String)
    func_map.append(('editor', _editor))

    @declared_attr
    def _bibliographiccitation(cls):
        return Column('%sbibliographiccitation' % column_prefix, String)
    func_map.append(('bibliographiccitation', _bibliographiccitation))

    @declared_attr
    def _date(cls):
        return Column('%sdate' % column_prefix, DateTime)
    func_map.append(('date', _date))

    @declared_attr
    def _booktitle(cls):
        return Column('%sbooktitle' % column_prefix, String)
    func_map.append(('booktitle', _booktitle))

    @declared_attr
    def _volume(cls):
        return Column('%svolume' % column_prefix, String)
    func_map.append(('volume', _volume))

    @declared_attr
    def _number(cls):
        return Column('%snumber' % column_prefix, String)
    func_map.append(('number', _number))

    @declared_attr
    def _series(cls):
        return Column('%sseries' % column_prefix, String)
    func_map.append(('series', _series))

    @declared_attr
    def _issue(cls):
        return Column('%sissue' % column_prefix, String)
    func_map.append(('issue', _issue))

    @declared_attr
    def _year(cls):
        return Column('%syear' % column_prefix, String)
    func_map.append(('year', _year))

    @declared_attr
    def _edition(cls):
        return Column('%sedition' % column_prefix, String)
    func_map.append(('edition', _edition))

    @declared_attr
    def _startpage(cls):
        return Column('%sstartpage' % column_prefix, String)
    func_map.append(('startpage', _startpage))

    @declared_attr
    def _endpage(cls):
        return Column('%sendpage' % column_prefix, String)
    func_map.append(('endpage', _endpage))

    @declared_attr
    def _publisher(cls):
        return Column('%spublisher' % column_prefix, String)
    func_map.append(('publisher', _publisher))

    @declared_attr
    def _address(cls):
        return Column('%saddress' % column_prefix, String)
    func_map.append(('address', _address))

    @declared_attr
    def _rights(cls):
        return Column('%srights' % column_prefix, String)
    func_map.append(('rights', _rights))

    @declared_attr
    def _rightsholder(cls):
        return Column('%srightsholder' % column_prefix, String)
    func_map.append(('rightsholder', _rightsholder))

    @declared_attr
    def _accessrights(cls):
        return Column('%saccessrights' % column_prefix, String)
    func_map.append(('accessrights', _accessrights))

    @declared_attr
    def _license(cls):
        return Column('%slicense' % column_prefix, String)
    func_map.append(('license', _license))

    @declared_attr
    def _publicationstatus(cls):
        return Column('%spublicationstatus' % column_prefix, String)
    func_map.append(('publicationstatus', _publicationstatus))

    if used:
        func_map.extend(_create_used(column_prefix=attr_prefix, key_prefix=key_prefix).items())
    print(['{}{}'.format(attr_prefix, attr_name)
            for attr_name, attr in func_map])
    return {'{}{}'.format(attr_prefix, attr_name): attr
            for attr_name, attr in func_map}


def CreationInfoMixin(name, column_prefix=None, key_prefix=None, used=True):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`CreationInfo` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """
    if not column_prefix:
        column_prefix = '%s_' % name


    return type(name, (object,),
                _create_creationinfo_map(column_prefix, key_prefix, used))


def LiteratureSourceMixin(name, column_prefix=None, key_prefix=None, used=True):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`LiteratureSource` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """
    if not column_prefix:
        column_prefix = '%s_' % name


    return type(name, (object,),
                _create_literaturesource_map(column_prefix, key_prefix, used))


def PublicIDMixin(name='', column_prefix=None):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin providing a general
    purpose :code:`publicID` attribute.

    .. note::

        The attribute :code:`publicID` is inherited from `QuakeML
        <https://quake.ethz.ch/quakeml/>`_.
    """
    if not column_prefix:
        column_prefix = '%s_' % name

    @declared_attr
    def _publicid(cls):
        return Column('%spublicid' % column_prefix, String)

    return type(name, (object,), {'%spublicid' % column_prefix: _publicid})


def EpochMixin(name, epoch_type=None, column_prefix=None):
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
    if column_prefix is None:
        column_prefix = '%s_' % name

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
                raise ValueError('Invalid boundery: {!r}.'.format(boundery))

            @declared_attr
            def _datetime(cls):
                return Column('%s%s' % (column_prefix, name), DateTime,
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
        raise ValueError('Invalid epoch_type: {!r}.'.format(epoch_type))

    def __dict__(func_map, attr_prefix):
        return {'{}{}'.format(attr_prefix, attr_name): attr
                for attr_name, attr in func_map}

    return type(name, (object,), __dict__(_func_map, column_prefix))


UniqueEpochMixin = EpochMixin('Epoch', column_prefix='')
UniqueOpenEpochMixin = EpochMixin('Epoch', epoch_type='open',
                                  column_prefix='')


def QuantityMixin(name, quantity_type, column_prefix=None, key_prefix=None):
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
    if not key_prefix:
        key_prefix = ''
    if column_prefix is None:
        column_prefix = '{}{}_'.format(key_prefix, name)
    column_prefix = column_prefix.lower()

    # Name attribute differently to column key.
    attr_prefix = '{}_'.format(name).lower()

    def create_value(quantity_type, column_prefix):

        def _make_value(sql_type, column_prefix):

            @declared_attr
            def _value(cls):
                #return {'%svalue' % name: Column('%svalue' % column_prefix, sql_type,
                #              nullable=False)}
                return Column('%svalue' % column_prefix, sql_type,
                              nullable=False)
            return _value

        if 'int' == quantity_type:
            return _make_value(Integer, column_prefix)
        elif quantity_type in ('real', 'float'):
            return _make_value(Float, column_prefix)
        elif 'time' == quantity_type:
            return _make_value(DateTime, column_prefix)

        raise ValueError('Invalid quantity_type: {}'.format(quantity_type))

    @declared_attr
    def _uncertainty(cls):
        return Column('%suncertainty' % column_prefix, Float)

    @declared_attr
    def _lower_uncertainty(cls):
        return Column('%sloweruncertainty' % column_prefix, Float)

    @declared_attr
    def _upper_uncertainty(cls):
        return Column('%supperuncertainty' % column_prefix, Float)

    @declared_attr
    def _confidence_level(cls):
        return Column('%sconfidencelevel' % column_prefix, Float)

    _func_map = (('value', create_value(quantity_type, column_prefix)),
                 ('uncertainty', _uncertainty),
                 ('loweruncertainty', _lower_uncertainty),
                 ('upperuncertainty', _upper_uncertainty),
                 ('confidencelevel', _confidence_level))

    def __dict__(func_map, attr_prefix):

        return {'{}{}'.format(attr_prefix, attr_name): attr
                for attr_name, attr in func_map}

    return type(name, (object,), __dict__(_func_map, attr_prefix))


FloatQuantityMixin = functools.partial(QuantityMixin,
                                       quantity_type='float')
RealQuantityMixin = FloatQuantityMixin
IntegerQuantityMixin = functools.partial(QuantityMixin,
                                         quantity_type='int')
TimeQuantityMixin = functools.partial(QuantityMixin,
                                      quantity_type='time')
