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

PREFIX = 'm_'

# XXX(damb): The implementation of the entities below is based on the QuakeML
# and the SC3 DB model naming conventions. As a consequence,
# sub-(sub-(...)types (e.g.  CreationInfo, LiteratureSource, Comment, etc. )
# are implemented as *flat* mixins instead of moving them to separate tables.
# Note, that this fact inherently leads to huge tables containing lots of
# columns.



class Borehole(CreationInfoMixin('CreationInfo',
                                 parent_prefix='creationinfo_',
                                 global_column_prefix=PREFIX,
                                 used=False),
               LiteratureSourceMixin('LiteratureSource',
                                     parent_prefix='literaturesource_',
                                     global_column_prefix=PREFIX,
                                     used=False),
               RealQuantityMixin('longitude', global_column_prefix=PREFIX, value_nullable=False),
               RealQuantityMixin('latitude', global_column_prefix=PREFIX, value_nullable=False),
               RealQuantityMixin('depth', global_column_prefix=PREFIX),
               RealQuantityMixin('bedrockdepth', global_column_prefix=PREFIX),
               RealQuantityMixin('measureddepth', global_column_prefix=PREFIX),
               PublicIDMixin(global_column_prefix=PREFIX),
               ORMBase):
    """
    ORM representation of a borehole. The attributes are in accordance with
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    _sections = relationship("BoreholeSection", back_populates="_borehole",
                             cascade='all, delete-orphan', lazy='noload', order_by='BoreholeSection.topdepth_value')



class BoreholeSection(EpochMixin('Epoch', epoch_type='open',
                                 column_prefix='m_'),
                      RealQuantityMixin('toplongitude', global_column_prefix=PREFIX),
                      RealQuantityMixin('toplatitude', global_column_prefix=PREFIX),
                      RealQuantityMixin('topdepth', global_column_prefix=PREFIX),
                      RealQuantityMixin('bottomlongitude', global_column_prefix=PREFIX),
                      RealQuantityMixin('bottomlatitude', global_column_prefix=PREFIX),
                      RealQuantityMixin('bottomdepth', global_column_prefix=PREFIX),
                      RealQuantityMixin('holediameter', global_column_prefix=PREFIX),
                      RealQuantityMixin('casingdiameter', global_column_prefix=PREFIX),
                      PublicIDMixin(global_column_prefix=PREFIX),
                      ORMBase):
    """
    ORM representation of a borehole. The attributes are in accordance with
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    topclosed = Column('{}topclosed'.format(PREFIX), Boolean, nullable=False)
    bottomclosed = Column('{}bottomclosed'.format(PREFIX), Boolean, nullable=False)
    sectiontype = Column('{}sectiontype'.format(PREFIX), String)
    casingtype = Column('{}casingtype'.format(PREFIX), String)
    description = Column('{}description'.format(PREFIX), String)

    borehole_oid = Column('{}borehole_oid'.format(PREFIX), Integer,
                          ForeignKey('borehole._oid'))

    _borehole = relationship("Borehole", back_populates="_sections")

    _hydraulics = relationship("HydraulicSample", back_populates="_section",
                               lazy='noload',
                               order_by='HydraulicSample.datetime_value')


class HydraulicSample(TimeQuantityMixin('datetime', global_column_prefix=PREFIX, value_nullable=False),
                      RealQuantityMixin('bottomtemperature', global_column_prefix=PREFIX),
                      RealQuantityMixin('bottomflow', global_column_prefix=PREFIX),
                      RealQuantityMixin('bottompressure', global_column_prefix=PREFIX),
                      RealQuantityMixin('toptemperature', global_column_prefix=PREFIX),
                      RealQuantityMixin('topflow', global_column_prefix=PREFIX),
                      RealQuantityMixin('toppressure', global_column_prefix=PREFIX),
                      RealQuantityMixin('fluiddensity', global_column_prefix=PREFIX),
                      RealQuantityMixin('fluidviscosity', global_column_prefix=PREFIX),
                      RealQuantityMixin('fluidph', global_column_prefix=PREFIX),
                      PublicIDMixin(global_column_prefix=PREFIX),
                      ORMBase):
    """
    Represents an hydraulics sample. The definition is based on `QuakeML
    <https://quake.ethz.ch/quakeml/QuakeML2.0/Hydraulic>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    fluidcomposition = Column('{}fluidcomposition'.format(PREFIX), String)

    _section = relationship("BoreholeSection", back_populates="_hydraulics")

    boreholesection_oid = Column('{}boreholesection_oid'.format(PREFIX),
                                 Integer, ForeignKey('boreholesection._oid'))
