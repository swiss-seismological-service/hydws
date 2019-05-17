"""
HYDWS datamodel ORM representation.
"""

from operator import itemgetter
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func


from hydws.db.base import (ORMBase, CreationInfoMixin, RealQuantityMixin,
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
    _sections = relationship("BoreholeSection", back_populates="_borehole",
                             order_by="BoreholeSection.m_topdepth_value",
                             cascade='all, delete-orphan')

    @hybrid_property
    def m_longitude(self):
        # min topdepth defines top-section
        return min([s for s in self._sections],
                   key=lambda x: x.m_topdepth_value).m_toplongitude_value

    @hybrid_property
    def m_latitude(self):
        # min topdepth defines top-section
        return min([s for s in self._sections],
                   key=lambda x: x.m_topdepth_value).m_toplatitude_value

    @hybrid_property
    def m_depth(self):
        # max bottomdepth defines bottom-section
        return max([s.m_bottomdepth_value for s in self._sections])

    @hybrid_property
    def m_injectionpoint(self):
        """
        Injection point of the borehole. It is defined by the uppermost
        section's bottom with casing and an open bottom.

        .. note::

            The implementation requires boreholes to be linear.
        """
        isection = min([s for s in self._sections
                       if s.m_casingdiameter_value and not s._bottomclosed],
                       key=lambda x: x.m_bottomdepth_value, default=None)

        if not isection:
            raise ValueError('Cased borehole has a closed bottom.')

        return (isection.bottomlongitude_value,
                isection.bottomlatitude_value,
                isection.bottomdepth_value)


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
    _borehole = relationship("Borehole", back_populates="_sections")

    _hydraulics = relationship("HydraulicSample", back_populates="_section",
                               order_by="HydraulicSample.m_datetime_value")


class HydraulicSample(TimeQuantityMixin('m_datetime'),
                      RealQuantityMixin('m_bottomtemperature'),
                      RealQuantityMixin('m_bottomflow'),
                      RealQuantityMixin('m_bottompressure'),
                      RealQuantityMixin('m_toptemperature'),
                      RealQuantityMixin('m_topflow'),
                      RealQuantityMixin('m_toppressure'),
                      RealQuantityMixin('m_fluiddensity'),
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
    _section = relationship("BoreholeSection", back_populates="_hydraulics")
