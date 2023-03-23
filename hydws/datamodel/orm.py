"""
.. module:: orm
   :synopsis: HYDWS datamodel ORM representation.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from hydws.datamodel.base import (EpochMixin, ORMBase, PublicIDMixin,
                                  RealQuantityMixin, TimeQuantityMixin)


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
    ORM representation of a borehole.
    """

    description = Column('description', String)
    name = Column('name', String)

    _sections = relationship("BoreholeSection",
                             back_populates="_borehole",
                             cascade='all, delete-orphan',
                             passive_deletes=True,
                             lazy='noload',
                             order_by='BoreholeSection.topaltitude_value')

    _literaturesource_oid = Column(Integer,
                                   ForeignKey('literaturesource._oid'))
    _literaturesource = relationship("LiteratureSource",
                                     foreign_keys=[_literaturesource_oid])

    _creationinfo_oid = Column(Integer, ForeignKey('creationinfo._oid'))
    _creationinfo = relationship("CreationInfo",
                                 foreign_keys=[_creationinfo_oid])

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


class BoreholeSection(EpochMixin('Epoch', epoch_type='finite'),
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
    ORM representation of a borehole.
    """

    topclosed = Column('topclosed', Boolean)
    bottomclosed = Column('bottomclosed', Boolean)
    sectiontype = Column('sectiontype', String)
    casingtype = Column('casingtype', String)
    description = Column('description', String)

    borehole_oid = Column('borehole_oid',
                          Integer,
                          ForeignKey('borehole._oid', ondelete="CASCADE"))

    _borehole = relationship("Borehole", back_populates="_sections")

    _hydraulics = relationship("HydraulicSample",
                               back_populates="_section",
                               lazy='noload',
                               order_by='HydraulicSample.datetime_value',
                               cascade='all, delete-orphan',
                               passive_deletes=True)


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
    Represents an hydraulics sample.
    """

    __mapper_args__ = {'confirm_deleted_rows': False}
    fluidcomposition = Column('fluidcomposition', String)

    boreholesection_oid = Column(
        'boreholesection_oid',
        Integer,
        ForeignKey('boreholesection._oid', ondelete="CASCADE"))
    _section = relationship("BoreholeSection", back_populates="_hydraulics")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<{}(datetime={})>".format(type(self).__name__,
                                          self.datetime_value.isoformat())

    def __hash__(self):
        return id(self)
