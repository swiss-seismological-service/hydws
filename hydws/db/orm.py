"""
.. module:: orm
   :synopsis: HYDWS datamodel ORM representation.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship, class_mapper

from hydws.db.base import (ORMBase, RealQuantityMixin,
                           TimeQuantityMixin, EpochMixin, PublicIDMixin)
from hydws.server import settings


def clone(obj, with_foreignkeys=False):
    """
    Clone a `SQLAlchemy <https://www.sqlalchemy.org/>`_ mapping object omitting
    the object's primary key.

    :param obj: SQLAlchemy mapping object to be cloned.
    :param bool with_foreignkeys: Include foreign keys while copying

    :returns: Cloned SQLAlchemy mapping object.
    """
    mapper = class_mapper(type(obj))
    new = type(obj)()

    pk_keys = set([c.key for c in mapper.primary_key])
    rel_keys = set([c.key for c in mapper.relationships])
    omit = pk_keys | rel_keys

    if not with_foreignkeys:
        fk_keys = set([c.key for c in mapper.columns if c.foreign_keys])
        omit = omit | fk_keys

    for attr in [p.key for p in mapper.iterate_properties
                 if p.key not in omit]:
        try:
            value = getattr(obj, attr)
            setattr(new, attr, value)
        except AttributeError:
            pass

    return new


# XXX(damb): The implementation of the entities below is based on the QuakeML
# and the SC3 DB model naming conventions. As a consequence,
# sub-(sub-(...)types (e.g.  CreationInfo, LiteratureSource, Comment, etc. )
# are implemented as *flat* mixins instead of moving them to separate tables.
# Note, that this fact inherently leads to huge tables containing lots of
# columns.

# XXX(sarsonl): Do we want to restrict nullable values on the db level,
# or just schema.

try:
    PREFIX = settings.HYDWS_PREFIX
except AttributeError:
    PREFIX = ''

class User(ORMBase):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Borehole(RealQuantityMixin('longitude',
                                 value_nullable=False),
               RealQuantityMixin('latitude',
                                 value_nullable=False),
               RealQuantityMixin('altitude',
                                 value_nullable=False),
               RealQuantityMixin('bedrockaltitude'),
               RealQuantityMixin('measureddepth'),
               PublicIDMixin(),
               ORMBase):
    """
    ORM representation of a borehole. The attributes are in accordance with
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """

    description = Column(f'{PREFIX}description', String)
    name = Column(f'{PREFIX}name', String)
    _sections = relationship("BoreholeSection", back_populates="_borehole",
                             cascade='all, delete-orphan', lazy='noload',
                             order_by='BoreholeSection.topaltitude_value')

    _literaturesource_oid = Column(Integer,
                                   ForeignKey('literaturesource._oid'))
    _literaturesource = relationship("LiteratureSource", uselist=False,
                                     foreign_keys=[_literaturesource_oid])

    _creationinfo_oid = Column(Integer, ForeignKey('creationinfo._oid'))
    _creationinfo = relationship("CreationInfo", uselist=False,
                                 foreign_keys=[_creationinfo_oid])

    def snapshot(self, section_filter_cond=None, sample_filter_cond=None):
        """
        Create a snapshot of the injection well. If available a snapshot
        implies snapshotting the well's sections.

        :param section_filter_cond: Callable applied on well sections when
            creating the snapshot
        :type section_filter_cond: callable or None
        :param sample_filter_cond: Callable applied on hydraulic samples when
            creating the snapshot
        :type sample_filter_cond: callable or None

        :returns: Snapshot of the injection well
        :rtype: :py:class:`InjectionWell`
        """
        snap = type(self)()
        snap.publicid = self.publicid

        if self._sections:
            snap._sections = [s.snapshot(filter_cond=sample_filter_cond)
                              for s in list(filter(section_filter_cond,
                                                   self._sections))]
        return snap

    def merge(self, other, merge_undefined=True):
        """
        Merge this injection well with another injection well.

        :param other: Injection well to be merged
        :type other: :py:class:`InjectionWell`
        :param bool merge_undefined: Merge :code:`other` into the injection
            well if the well is undefined (i.e. if the :code:`publicid` is not
            specified). Note, that the well's sections are removed and
            substituted by the sections of :code:`other`.
        """
        assert isinstance(other, type(self)), \
            "other is not of type InjectionWell."

        def section_lookup_by_publicid(publicid):
            for k, v in enumerate(self._sections):
                if v.publicid == publicid:
                    return self[k]
            return None

        if self.publicid == other.publicid:

            MUTABLE_ATTRS = ['_creationinfo', '_creationinfo_oid',
                             '_literaturesource', '_literaturesource_oid']
            for attr in MUTABLE_ATTRS:
                value = getattr(other, attr)
                setattr(self, attr, value)
            for sec in other._sections:
                _sec = section_lookup_by_publicid(sec.publicid)
                if _sec is None:
                    self._sections.append(sec.copy())
                else:
                    _sec.merge(sec)
        elif merge_undefined and not self.publicid:
            self.publicid = other.publicid
            self._sections = []
            for sec in other._sections:
                self._sections.append(sec)

    def __iter__(self):
        for s in self._sections:
            yield s

    def __getitem__(self, item):
        return self._sections[item] if self._sections else None

    def __repr__(self):
        return ("<{}(publicid={!r}, longitude={}, latitude={}, "
                "altitude={}, measureddepth={})>").format(
                    type(self).__name__,
                    self.publicid, self.longitude_value, self.latitude_value,
                    self.altitude_value, self.measureddepth_value)


class BoreholeSection(EpochMixin('Epoch', epoch_type='open'),
                      RealQuantityMixin('toplongitude'),
                      RealQuantityMixin('toplatitude'),
                      RealQuantityMixin('topaltitude'),
                      RealQuantityMixin('bottomlongitude'),
                      RealQuantityMixin('bottomlatitude'),
                      RealQuantityMixin('bottomaltitude'),
                      RealQuantityMixin('topmeasureddepth'),
                      RealQuantityMixin('bottommeasureddepth'),
                      RealQuantityMixin('holediameter'),
                      RealQuantityMixin('casingdiameter'),
                      PublicIDMixin(),
                      ORMBase):
    """
    ORM representation of a borehole. The attributes are in accordance with
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    topclosed = Column(f'{PREFIX}topclosed', Boolean, nullable=False)
    bottomclosed = Column(f'{PREFIX}bottomclosed', Boolean, nullable=False)
    sectiontype = Column(f'{PREFIX}sectiontype', String)
    casingtype = Column(f'{PREFIX}casingtype', String)
    description = Column(f'{PREFIX}description', String)

    borehole_oid = Column(f'{PREFIX}borehole_oid', Integer,
                          ForeignKey('borehole._oid'))

    _borehole = relationship("Borehole", back_populates="_sections")

    _hydraulics = relationship("HydraulicSample", back_populates="_section",
                               lazy='noload', uselist=True,
                               order_by='HydraulicSample.datetime_value',
                               cascade='save-update, delete, delete-orphan')

    def snapshot(self, filter_cond=None):
        """
        Create a snapshot of the well section. If available, a snapshot
        includes hydraulics.

        .. note::

            Snapshotting a well containing an injectionplan is currently not
            implemented.

        :param filter_cond: Callable applied on hydraulic samples when creating
            the snapshot
        :type filter_cond: callable or None

        :returns: Snapshot of the well section
        :rtype: :py:class:`WellSection`
        """
        snap = clone(self, with_foreignkeys=False)

        if self._hydraulics:
            snap._hydraulics = self.hyd_snapshot(
                filter_cond=filter_cond)

        return snap

    def copy(self):
        """
        Alias for :py:meth:`snapshot` without filtering conditions.
        """
        return self.snapshot()

    def merge(self, other):
        """
        Merge this well section with another well section.

        :param other: Well section to be merged
        :type other: :py:class:`WellSection`
        """
        assert isinstance(other, type(self)) or other is None, \
            "other is not of type WellSection."

        if other and self.publicid == other.publicid:

            MUTABLE_ATTRS = ['endtime']

            # update mutable attributes
            for attr in MUTABLE_ATTRS:
                value = getattr(other, attr)
                setattr(self, attr, value)

            if self._hydraulics:
                self.hyd_merge(other._hydraulics)
            elif other._hydraulics:
                self._hydraulics = other.hyd_snapshot()

    def hyd_snapshot(self, filter_cond=None):
        """
        Snapshot hydraulics.

        :param filter_cond: Filter conditions applied to samples when
            performing the snapshot.
        :type filter_cond: callable or None

        :returns: Snapshot of hydraulics
        :rtype: :py:class:`Hydraulics`
        """
        assert callable(filter_cond) or filter_cond is None, \
            f"Invalid filter_cond: {filter_cond!r}"

        if filter_cond is None:
            def no_filter(s):
                return True

            filter_cond = no_filter

        snap = type(self._hydraulics)()
        snap._hydraulics = [s.copy() for s in self._hydraulics
                            if filter_cond(s)]

        return snap._hydraulics

    def hyd_reduce(self, filter_cond=None):
        """
        Remove samples from the hydraulic time series.

        :param filter_cond: Callable applied to hydraulic samples when removing
            events. Events matching the condition are removed. If
            :code:`filter_cond` is :code:`None` all samples are removed.
        :type filter_cond: callable or None
        """
        try:
            self._hydraulics = list(
                filter(lambda e: not filter_cond(e), self._hydraulics))
        except TypeError:
            if filter_cond is None:
                self._hydraulics = []
            else:
                raise

    def hyd_merge(self, other):
        """
        Merge samples from :code:`other` into the hydraulics. The merging
        strategy applied is a *delete by time* strategy i.e. samples
        overlapping with respect to the :code:`datetime_value` attribute value
        are overwritten with by samples from :code:`other`.

        :param other: list of HydraulicSample to be merged
        :type other: :py:class: list
        """
        assert isinstance(other, type(self._hydraulics)) or other is None, \
            "other is not a list of hydraulic samples"
        if other:
            first_sample = min(e.datetime_value for e in other)
            last_sample = max(e.datetime_value for e in other)

            def filter_by_overlapping_datetime(s):
                return (s.datetime_value >= first_sample and
                        s.datetime_value <= last_sample)

            self.hyd_reduce(filter_cond=filter_by_overlapping_datetime)
            # merge
            for s in other:
                self._hydraulics.append(s.copy())

class HydraulicSample(TimeQuantityMixin('datetime', value_nullable=False,
                                        index=True),
                      RealQuantityMixin('bottomtemperature'),
                      RealQuantityMixin('bottomflow'),
                      RealQuantityMixin('bottompressure'),
                      RealQuantityMixin('toptemperature'),
                      RealQuantityMixin('topflow'),
                      RealQuantityMixin('toppressure'),
                      RealQuantityMixin('fluiddensity'),
                      RealQuantityMixin('fluidviscosity'),
                      RealQuantityMixin('fluidph'),
                      ORMBase):
    """
    Represents an hydraulics sample. The definition is based on `QuakeML
    <https://quake.ethz.ch/quakeml/QuakeML2.0/Hydraulic>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    __mapper_args__ = {'confirm_deleted_rows': False}
    fluidcomposition = Column(f'{PREFIX}fluidcomposition', String)

    _section = relationship("BoreholeSection", back_populates="_hydraulics",
                            uselist=False)

    boreholesection_oid = Column(f'{PREFIX}boreholesection_oid',
                                 Integer, ForeignKey('boreholesection._oid'))

    def copy(self, with_foreignkeys=False):
        """
        Copy a seismic event omitting primary keys.

        :param bool with_foreignkeys: Include foreign keys while copying

        :returns: Copy of hydraulic sample
        :rtype: :py:class:`HydraulicSample`
        """
        return clone(self, with_foreignkeys=with_foreignkeys)

    def __eq__(self, other):
        if isinstance(other, HydraulicSample):
            mapper = class_mapper(type(self))

            pk_keys = set([c.key for c in mapper.primary_key])
            rel_keys = set([c.key for c in mapper.relationships])
            fk_keys = set([c.key for c in mapper.columns if c.foreign_keys])

            omit = pk_keys | rel_keys | fk_keys

            return all(getattr(self, attr) == getattr(other, attr)
                       for attr in [p.key for p in mapper.iterate_properties
                                    if p.key not in omit])

        raise ValueError

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<{}(datetime={})>".format(type(self).__name__,
                                          self.datetime_value.isoformat())

    # TODO(damb)
    # https://docs.python.org/3/reference/datamodel.html#object.__hash__
    # recommends to mix together the hash values of the components of the
    # object that also play a role in comparison of objects by packing them
    # into a tuple and hashing the tuple
    def __hash__(self):
        return id(self)
