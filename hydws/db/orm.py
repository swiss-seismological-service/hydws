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

KEY_PREFIX = 'm_'

# XXX(damb): The implementation of the entities below is based on the QuakeML
# and the SC3 DB model naming conventions. As a consequence,
# sub-(sub-(...)types (e.g.  CreationInfo, LiteratureSource, Comment, etc. )
# are implemented as *flat* mixins instead of moving them to separate tables.
# Note, that this fact inherently leads to huge tables containing lots of
# columns.


class Borehole(CreationInfoMixin('CreationInfo',
                                 column_prefix='creationinfo_',
                                 key_prefix=KEY_PREFIX),
               LiteratureSourceMixin('LiteratureSource',
                                     column_prefix='literaturesource_',
                                     key_prefix=KEY_PREFIX),
               RealQuantityMixin('longitude', key_prefix=KEY_PREFIX),
               RealQuantityMixin('latitude', key_prefix=KEY_PREFIX),
               RealQuantityMixin('depth', key_prefix=KEY_PREFIX),
               RealQuantityMixin('bedrockdepth', key_prefix=KEY_PREFIX),
               PublicIDMixin(column_prefix=KEY_PREFIX),
               ORMBase):
    """
    ORM representation of a borehole. The attributes are in accordance with
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    _sections = relationship("BoreholeSection", back_populates="_borehole",
                             cascade='all, delete-orphan')



class BoreholeSection(EpochMixin('Epoch', epoch_type='open',
                                 column_prefix='m_'),
                      RealQuantityMixin('toplongitude', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('toplatitude', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('topdepth', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('bottomlongitude', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('bottomlatitude', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('bottomdepth', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('holediameter', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('casingdiameter', key_prefix=KEY_PREFIX),
                      PublicIDMixin(column_prefix=KEY_PREFIX),
                      ORMBase):
    """
    ORM representation of a borehole. The attributes are in accordance with
    `QuakeML <https://quake.ethz.ch/quakeml/>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    topclosed = Column('{}topclosed'.format(KEY_PREFIX), Boolean)
    bottomclosed = Column('{}bottomclosed'.format(KEY_PREFIX), Boolean)
    sectiontype = Column('{}sectiontype'.format(KEY_PREFIX), String)
    casingtype = Column('{}casingtype'.format(KEY_PREFIX), String)
    description = Column('{}description'.format(KEY_PREFIX), String)

    borehole_oid = Column('{}borehole_oid'.format(KEY_PREFIX), Integer, ForeignKey('borehole._oid'))
    _borehole = relationship("Borehole", back_populates="_sections")

    _hydraulics = relationship("HydraulicSample", back_populates="_section")


class HydraulicSample(TimeQuantityMixin('datetime', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('bottomtemperature', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('bottomflow', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('bottompressure', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('toptemperature', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('topflow', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('toppressure', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('fluiddensity', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('fluidviscosity', key_prefix=KEY_PREFIX),
                      RealQuantityMixin('fluidph', key_prefix=KEY_PREFIX),
                      PublicIDMixin(column_prefix=KEY_PREFIX),
                      ORMBase):
    """
    Represents an hydraulics sample. The definition is based on `QuakeML
    <https://quake.ethz.ch/quakeml/QuakeML2.0/Hydraulic>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    fluidcomposition = Column('{}fluidcomposition'.format(KEY_PREFIX), String)

    boreholesection_oid = Column('boreholesection_oid'.format(KEY_PREFIX), Integer, ForeignKey('boreholesection._oid'))
    _section = relationship("BoreholeSection", back_populates="_hydraulics")
