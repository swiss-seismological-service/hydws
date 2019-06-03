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

# XXX No seperate column name defined, use parent name.
# It should only be accessed on orm side through attribute name.
def _create_used(parent_prefix=None, global_column_prefix=None):
    @declared_attr
    def _used(cls):
        return Column('%s%sused' % (global_column_prefix, parent_prefix), Boolean, nullable=False,
                      default=False)

    return {'{}{}'.format(parent_prefix, 'used'): _used}


def _create_resourceidentifier_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    @declared_attr
    def _resourceid(cls):
        return Column('%sresourceid' % column_prefix, String)
    func_map = [('%sresourceid' % parent_prefix, _resourceid), ]

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_resourcelocator_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    @declared_attr
    def _resourcelocator(cls):
        return Column('%sresourcelocator' % column_prefix, String)
    func_map = [('%sresourcelocator' % parent_prefix, _resourcelocator), ]

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_creationinfo_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    @declared_attr
    def _author(cls):
        return Column('%sauthor' % column_prefix, String)
    func_map = [('%sauthor' % parent_prefix, _author), ]
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%sauthoruri_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    @declared_attr
    def _agencyid(cls):
        return Column('%sagencyid' % column_prefix, String)
    func_map.append(('%sagencyid' % parent_prefix, _agencyid))
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%sagencyuri_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    @declared_attr
    def _creationtime(cls):
        return Column('%screationtime' % column_prefix, DateTime)
    func_map.append(('%screationtime'% parent_prefix, _creationtime))

    @declared_attr
    def _version(cls):
        return Column('%sversion' % column_prefix, String)
    func_map.append(('%sversion' % parent_prefix, _version))

    @declared_attr
    def _copyrightowner(cls):
        return Column('%scopyrightowner' % column_prefix, String)
    func_map.append(('%scopyrightowner'% parent_prefix, _copyrightowner))
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%scopyrightowneruri_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    @declared_attr
    def _license(cls):
        return Column('%slicense' % column_prefix, String)
    func_map.append(('%slicense' % parent_prefix, _license))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_domtypeuri_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%suri_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=False).items())

    @declared_attr
    def _type(cls):
        return Column('%stype' % column_prefix, String)
    func_map.append(('%stype' % parent_prefix, _type))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_languagecodeuri_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%suri_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=False).items())

    @declared_attr
    def _code(cls):
        return Column('%scode' % column_prefix, String)
    func_map.append(('%scode' % parent_prefix, _code))

    @declared_attr
    def _language(cls):
        return Column('%slanguage' % column_prefix, String)
    func_map.append(('%slanguage' % parent_prefix, _language))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_countrycodeuri_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%suri_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=False).items())

    @declared_attr
    def _code(cls):
        return Column('%scode' % column_prefix, String)
    func_map.append(('%scode' % parent_prefix, _code))

    @declared_attr
    def _country(cls):
        return Column('%scountry' % column_prefix, String)
    func_map.append(('%scountry'  % parent_prefix, _country))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_author_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_person_map(
            parent_prefix='%sperson_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=False).items())

    func_map.extend(
        _create_personalaffiliatation_map(
            parent_prefix='%saffiliation_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_personalaffiliatation_map(
            parent_prefix='%salternateaffiliation_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%smbox_' % parent_prefix,
            global_column_prefix=global_column_prefix,# XXX don't use column prefix
            used=used).items())

    func_map.extend(
        _create_comment_map(
            parent_prefix='%scomment_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    @declared_attr
    def _positioninauthorlist(cls):
        # XXX(damb): Unfortunately, the constraint that this value must be
        # positive must be defined by means of __table_args__
        # (see: https://docs.sqlalchemy.org/en/13/core/constraints.html#
        #  setting-up-constraints-when-using-the-declarative-orm-extension)
        return Column('%spositioninauthorlist' % column_prefix, Integer)

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_person_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    @declared_attr
    def _name(cls):
        return Column('%sname' % column_prefix, String)
    func_map = [('%sname' % parent_prefix, _name)]

    @declared_attr
    def _givenname(cls):
        return Column('%sgivenname' % column_prefix, String)
    func_map.append(('%sgivenname' % parent_prefix, _givenname))

    @declared_attr
    def _familyname(cls):
        return Column('%sfamilyname' % column_prefix, String)
    func_map.append(('%sfamilyname' % parent_prefix, _familyname))

    @declared_attr
    def _title(cls):
        return Column('%stitle' % column_prefix, String)
    func_map.append(('%stitle' % parent_prefix, _title))

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%spersonid_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%salternatepersonid_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%smbox_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%sphone_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_resourcelocator_map(
            parent_prefix='%shomepage_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_resourcelocator_map(
            parent_prefix='%sworkplacehomepage_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_personalaffiliatation_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_institution_map(
            parent_prefix='%sinstitution_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    @declared_attr
    def _department(cls):
        return Column('%sdepartment' % column_prefix, String)
    func_map.append(('%sdepartment' % parent_prefix, _department))

    @declared_attr
    def _function(cls):
        return Column('%sfunction' % column_prefix, String)
    func_map.append(('%sfunction' % parent_prefix, _function))

    func_map.extend(
        _create_comment_map(
            parent_prefix='%scomment_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_comment_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    @declared_attr
    def _comment(cls):
        return Column('%scomment' % column_prefix, String)
    func_map = [('%scomment' % parent_prefix, _comment), ]

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%sid_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_creationinfo_map(
            parent_prefix='%screationinfo_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_institution_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    @declared_attr
    def _name(cls):
        return Column('%sname' % column_prefix, String)
    func_map = [('%sname' % parent_prefix, _name), ]

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%sidentifier_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%smbox_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%sphone_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_resourcelocator_map(
            parent_prefix='%shomepage_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    func_map.extend(
        _create_postaladdress_map(
            parent_prefix='%spostaladdress_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_postaladdress_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)
    @declared_attr
    def _streetaddress(cls):
        return Column('%sstreetaddress' % column_prefix, String)
    func_map = [('%sstreetaddress' % parent_prefix, _streetaddress), ]

    @declared_attr
    def _locality(cls):
        return Column('%slocality' % column_prefix, String)
    func_map.append(('%slocality' % parent_prefix, _locality))

    @declared_attr
    def _postalcode(cls):
        return Column('%spostalcode' % column_prefix, String)
    func_map.append(('%spostalcode' % parent_prefix, _postalcode))

    func_map.extend(
        _create_countrycodeuri_map(
            parent_prefix='%scountry_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def _create_literaturesource_map(parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):

    if not parent_prefix:
        parent_prefix = ''
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    func_map = []
    func_map.extend(
        _create_resourceidentifier_map(
            parent_prefix='%sidentifier_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    # QuakeML: DOMTypeURI
    func_map.extend(
        _create_domtypeuri_map(
            parent_prefix='%stype_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    # QuakeML: BibtexEntryType
    @declared_attr
    def _bibtextype(cls):
        return Column('%sbibtextype' % column_prefix, Enum(EBibtexEntryType))
    func_map.append(('%sbibtextype' % parent_prefix, _bibtextype))

    if used:
        func_map.extend(_create_used(
            parent_prefix='%sbibtextype_' % parent_prefix,
            global_column_prefix=global_column_prefix).items())

    # QuakeML: LanguageCodeURI
    func_map.extend(
        _create_languagecodeuri_map(
            parent_prefix='%stype_' % parent_prefix,
            global_column_prefix=global_column_prefix,
            used=used).items())

    # QuakeML: Author
    func_map.extend(
        _create_author_map(
            parent_prefix='%screator_' % parent_prefix,
            global_column_prefix=global_column_prefix,# XXX don't use column prefix
            used=used).items())

    @declared_attr
    def _title(cls):
        return Column('%stitle' % column_prefix, String)
    func_map.append(('%stitle' % parent_prefix, _title))

    @declared_attr
    def _author(cls):
        return Column('%sauthor' % column_prefix, String)
    func_map.append(('%sauthor' % parent_prefix, _author))

    @declared_attr
    def _editor(cls):
        return Column('%seditor' % column_prefix, String)
    func_map.append(('%seditor' % parent_prefix, _editor))

    @declared_attr
    def _bibliographiccitation(cls):
        return Column('%sbibliographiccitation' % column_prefix, String)
    func_map.append(('%sbibliographiccitation' % parent_prefix, _bibliographiccitation))

    @declared_attr
    def _date(cls):
        return Column('%sdate' % column_prefix, DateTime)
    func_map.append(('%sdate' % parent_prefix, _date))

    @declared_attr
    def _booktitle(cls):
        return Column('%sbooktitle' % column_prefix, String)
    func_map.append(('%sbooktitle' % parent_prefix, _booktitle))

    @declared_attr
    def _volume(cls):
        return Column('%svolume' % column_prefix, String)
    func_map.append(('%svolume' % parent_prefix, _volume))

    @declared_attr
    def _number(cls):
        return Column('%snumber' % column_prefix, String)
    func_map.append(('%snumber' % parent_prefix, _number))

    @declared_attr
    def _series(cls):
        return Column('%sseries' % column_prefix, String)
    func_map.append(('%sseries' % parent_prefix, _series))

    @declared_attr
    def _issue(cls):
        return Column('%sissue' % column_prefix, String)
    func_map.append(('%sissue' % parent_prefix, _issue))

    @declared_attr
    def _year(cls):
        return Column('%syear' % column_prefix, String)
    func_map.append(('%syear' % parent_prefix, _year))

    @declared_attr
    def _edition(cls):
        return Column('%sedition' % column_prefix, String)
    func_map.append(('%sedition' % parent_prefix, _edition))

    @declared_attr
    def _startpage(cls):
        return Column('%sstartpage' % column_prefix, String)
    func_map.append(('%sstartpage' % parent_prefix, _startpage))

    @declared_attr
    def _endpage(cls):
        return Column('%sendpage' % column_prefix, String)
    func_map.append(('%sendpage' % parent_prefix, _endpage))

    @declared_attr
    def _publisher(cls):
        return Column('%spublisher' % column_prefix, String)
    func_map.append(('%spublisher' % parent_prefix, _publisher))

    @declared_attr
    def _address(cls):
        return Column('%saddress' % column_prefix, String)
    func_map.append(('%saddress' % parent_prefix, _address))

    @declared_attr
    def _rights(cls):
        return Column('%srights' % column_prefix, String)
    func_map.append(('%srights' % parent_prefix, _rights))

    @declared_attr
    def _rightsholder(cls):
        return Column('%srightsholder' % column_prefix, String)
    func_map.append(('%srightsholder' % parent_prefix, _rightsholder))

    @declared_attr
    def _accessrights(cls):
        return Column('%saccessrights' % column_prefix, String)
    func_map.append(('%saccessrights' % parent_prefix, _accessrights))

    @declared_attr
    def _license(cls):
        return Column('%slicense' % column_prefix, String)
    func_map.append(('%slicense' % parent_prefix, _license))

    @declared_attr
    def _publicationstatus(cls):
        return Column('%spublicationstatus' % column_prefix, String)
    func_map.append(('%spublicationstatus' % parent_prefix, _publicationstatus))

    if used:
        func_map.extend(_create_used(parent_prefix=parent_prefix,
                        global_column_prefix=global_column_prefix).items())

    return {'{}'.format(attr_name): attr
            for attr_name, attr in func_map}


def CreationInfoMixin(name, parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`CreationInfo` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """
    if not parent_prefix:
        parent_prefix = ''

    return type(name, (object,),
                _create_creationinfo_map(parent_prefix=parent_prefix, global_column_prefix=global_column_prefix, used=used))


def LiteratureSourceMixin(name, parent_prefix=None, global_column_prefix=None, column_prefix=None, used=True):
    """
    `SQLAlchemy <https://www.sqlalchemy.org/>`_ mixin emulating type
    :code:`LiteratureSource` from `QuakeML <https://quake.ethz.ch/quakeml/>`_.
    """

    if not parent_prefix:
        parent_prefix = ''

    return type(name, (object,),
                _create_literaturesource_map(parent_prefix=parent_prefix, global_column_prefix=global_column_prefix, used=used))


def PublicIDMixin(name='', parent_prefix=None, column_prefix=None, global_column_prefix=None):
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
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

    @declared_attr
    def _publicid(cls):
        return Column('%spublicid' % column_prefix, String, nullable=False)

    return type(name, (object,), {'%spublicid' % parent_prefix: _publicid})


def EpochMixin(name, epoch_type=None, parent_prefix=None, column_prefix=None, global_column_prefix=None):
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
    if not column_prefix:
        column_prefix = parent_prefix
    
    if global_column_prefix:
        column_prefix = '%s%s' % (global_column_prefix, column_prefix)

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

    return type(name, (object,), __dict__(_func_map, parent_prefix))


UniqueEpochMixin = EpochMixin('Epoch', column_prefix='')
UniqueOpenEpochMixin = EpochMixin('Epoch', epoch_type='open',
                                  column_prefix='')


def QuantityMixin(name, quantity_type, column_prefix=None, global_column_prefix=None, value_nullable=True):
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
    if not global_column_prefix:
        global_column_prefix = ''
    if column_prefix is None:
        column_prefix = '{}{}_'.format(global_column_prefix, name)
    column_prefix = column_prefix.lower()

    # Name attribute differently to column key.
    attr_prefix = '{}_'.format(name).lower()

    def create_value(quantity_type, column_prefix):

        def _make_value(sql_type, column_prefix):

            @declared_attr
            def _value(cls):
                return Column('%svalue' % column_prefix, sql_type,
                              nullable=value_nullable)
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
