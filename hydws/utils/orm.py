"""
HYDWS datamodel ORM representation.
"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from hydws.utils.base import (ORMBase, CreationInfoMixin, RealQuantityMixin,
                              TimeQuantityMixin, EpochMixin,
                              LiteratureSourceMixin, PublicIDMixin)

# XXX(damb): The implementation of the entities below is based on the QuakeML
# and the SC3 DB model naming conventions. As a consequence,
# sub-(sub-(...)types (e.g.  CreationInfo, LiteratureSource, Comment, etc. )
# are implemented as *flat* mixins instead of moving them to separate tables.
# Note, that this fact inherently leads to huge tables containing lots of
# columns.


class Borehole(CreationInfoMixin('CreationInfo',
                                 column_prefix='m_creationinfo_'),
               LiteratureSourceMixin('LiteratureSource',
                                     column_prefix='m_literaturesource_'),
               RealQuantityMixin('m_longitude'),
               RealQuantityMixin('m_latitude'),
               RealQuantityMixin('m_depth'),
               RealQuantityMixin('m_bedrockdepth'),
               PublicIDMixin(column_prefix='m_'),
               ORMBase):
    """
    ORM representation of a borehole. The attributes are in accordance with
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    sections = relationship("BoreholeSection", back_populates="borehole")


class BoreholeSection(EpochMixin('Epoch', epoch_type='open',
                                 column_prefix='m_'),
                      RealQuantityMixin('m_toplongitude'),
                      RealQuantityMixin('m_toplatitude'),
                      RealQuantityMixin('m_topdepth'),
                      RealQuantityMixin('m_bottomlongitude'),
                      RealQuantityMixin('m_bottomlatitude'),
                      RealQuantityMixin('m_bottomdepth'),
                      RealQuantityMixin('m_holediameter'),
                      RealQuantityMixin('m_casingdiameter'),
                      PublicIDMixin(column_prefix='m_'),
                      ORMBase):
    """
    ORM representation of a borehole. The attributes are in accordance with
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    m_topclosed = Column(Boolean)
    m_bottomclosed = Column(Boolean)
    m_sectiontype = Column(String)
    m_casingtype = Column(String)
    m_description = Column(String)

    m_borehole_oid = Column(Integer, ForeignKey('borehole._oid'))
    borehole = relationship("Borehole", back_populates="sections")

    hydraulics = relationship("HydraulicSample", back_populates="")


class HydraulicSample(TimeQuantityMixin('m_datetime'),
                      RealQuantityMixin('m_downtemperature'),
                      RealQuantityMixin('m_downflow'),
                      RealQuantityMixin('m_downpressure'),
                      RealQuantityMixin('m_toptemperature'),
                      RealQuantityMixin('m_topflow'),
                      RealQuantityMixin('m_toppressure'),
                      RealQuantityMixin('m_fuiddensity'),
                      RealQuantityMixin('m_fluidviscosity'),
                      RealQuantityMixin('m_fluidph'),
                      PublicIDMixin(column_prefix='m_'),
                      ORMBase):
    """
    Represents an hydraulics sample. The definition is based on `QuakeML
    <https://quake.ethz.ch/quakeml/QuakeML2.0/Hydraulic>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    m_fluidcomposition = Column(String)

    m_boreholesection_oid = Column(Integer, ForeignKey('boreholesection._oid'))
    boreholesection = relationship("BoreholeSection",
                                   back_populates="hydraulics")
