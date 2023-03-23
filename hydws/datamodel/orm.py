"""
.. module:: orm
   :synopsis: HYDWS datamodel ORM representation.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from hydws.datamodel.base import (CreationInfoMixin, EpochMixin, ORMBase,
                                  PublicIDMixin, RealQuantityMixin,
                                  TimeQuantityMixin)


class Borehole(RealQuantityMixin('longitude',
                                 value_nullable=False),
               RealQuantityMixin('latitude',
                                 value_nullable=False),
               RealQuantityMixin('altitude',
                                 value_nullable=False),
               RealQuantityMixin('bedrockaltitude'),
               RealQuantityMixin('measureddepth'),
               PublicIDMixin(),
               CreationInfoMixin,
               ORMBase):
    """
    ORM representation of a borehole.
    """

    description = Column('description', String)
    name = Column('name', String)
    location_name = Column('location_name', String)
    institution = Column('institition', String)

    _sections = relationship("BoreholeSection",
                             back_populates="_borehole",
                             cascade='all, delete-orphan',
                             passive_deletes=True,
                             lazy='noload',
                             order_by='BoreholeSection.topaltitude_value')

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

    name = Column('name', String)
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


class HydraulicSample(TimeQuantityMixin('datetime', value_nullable=False),
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
