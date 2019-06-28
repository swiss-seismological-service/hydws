"""
.. module:: orm
   :synopsis: HYDWS datamodel ORM representation.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select


from hydws.db.base import (ORMBase, RealQuantityMixin, LiteratureSource, CreationInfo,
                           TimeQuantityMixin, EpochMixin, PublicIDMixin)
from hydws.server import settings



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

class Borehole( RealQuantityMixin('longitude',
                                 value_nullable=False),
               RealQuantityMixin('latitude',
                                 value_nullable=False),
               RealQuantityMixin('depth'),
               RealQuantityMixin('bedrockdepth'),
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
    _sections = relationship("BoreholeSection", back_populates="_borehole",
                             cascade='all, delete-orphan', lazy='noload',
                             order_by='BoreholeSection.topdepth_value')

    _literaturesource_oid = Column(Integer,
                                   ForeignKey('literaturesource._oid'))
    _literaturesource = relationship("LiteratureSource", uselist=False,
                                     foreign_keys=[_literaturesource_oid])

    _creationinfo_oid = Column(Integer, ForeignKey('creationinfo._oid'))
    _creationinfo = relationship("CreationInfo", uselist=False,
                                 foreign_keys=[_creationinfo_oid])


class BoreholeSection(EpochMixin('Epoch', epoch_type='open'),
                      RealQuantityMixin('toplongitude'),
                      RealQuantityMixin('toplatitude'),
                      RealQuantityMixin('topdepth'),
                      RealQuantityMixin('bottomlongitude'),
                      RealQuantityMixin('bottomlatitude'),
                      RealQuantityMixin('bottomdepth'),
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
                               lazy='noload',
                               order_by='HydraulicSample.datetime_value')


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
    Represents an hydraulics sample. The definition is based on `QuakeML
    <https://quake.ethz.ch/quakeml/QuakeML2.0/Hydraulic>`_.

    .. note::

        *Quantities* are implemented as `QuakeML
        <https://quake.ethz.ch/quakeml>`_ quantities.
    """
    fluidcomposition = Column(f'{PREFIX}fluidcomposition', String)

    _section = relationship("BoreholeSection", back_populates="_hydraulics")

    boreholesection_oid = Column(f'{PREFIX}boreholesection_oid',
                                 Integer, ForeignKey('boreholesection._oid'))
