"""
HYDWS datamodel ORM entity de-/serialization facilities.
"""
import logging

import datetime

from marshmallow import Schema, fields, post_dump
from marshmallow.utils import get_value


_ATTR_PREFIX = 'm_'

# XXX(damb): Currently, there are no validation facilities implemented.


class QuakeMLQuantityField(fields.Field):
    """
    `QuakeML <https://quake.ethz.ch/quakeml/>`_ quantity field type
    implementation.

    The field creates a nested dict consisting of a base value and
    a number of uncertainty measures which are composed from the flat
    structure that is stored in the object.
    """
    _CHECK_ATTRIBUTE = False  # We generate the attribute dynamically
    ATTRS = ('value', 'uncertainty', 'loweruncertainty', 'upperuncertainty',
             'confidencelevel')
    logger = logging.getLogger('hydws.server.v1.resource')
    def _serialize(self, value, attr, obj, **kwargs):
        retval = {}
        for _attr in self.ATTRS:
            key = f"{attr}_{_attr}".lower()
            value = get_value(obj, key, default=None)
            
            if isinstance(value, datetime.datetime):
                retval[_attr] = value.isoformat()
            elif value is not None:
                retval[_attr] = value

        return retval or None


class SchemaBase(Schema):
    """
    Schema base class for object de-/serialization.
    """

    def get_attribute(self, obj, key, default):
        """
        Custom accessor method extracting values from objects applying the
        :code:`m_` prefix to attribute keys.
        """
        #print(key, _ATTR_PREFIX)
        #if key.startswith(_ATTR_PREFIX):
        #    key = _ATTR_PREFIX + key.lower()

        return get_value(obj, key, default)

    @post_dump
    def remove_empty(self, data):
        """
        Filter out fields with empty (e.g. :code:`None`, :code:`[], etc.)
        values.
        """
        return {k: v for k, v in data.items() if v}


class HydraulicSampleSchema(SchemaBase):
    """
    Schema implementation of an hydraulic data sample.
    """
    datetime = QuakeMLQuantityField()
    downtemperature = QuakeMLQuantityField()
    downflow = QuakeMLQuantityField()
    downpressure = QuakeMLQuantityField()
    toptemperature = QuakeMLQuantityField()
    topflow = QuakeMLQuantityField()
    toppressure = QuakeMLQuantityField()
    fuiddensity = QuakeMLQuantityField()
    fluidviscosity = QuakeMLQuantityField()
    fluidph = QuakeMLQuantityField()
    fluidcomposition = fields.String()


class SectionSchema(SchemaBase):
    """
    Schema implementation of a borehole section.
    """
    publicid = fields.String()
    starttime = fields.DateTime(format='iso')
    endtime = fields.DateTime(format='iso')
    toplongitude = QuakeMLQuantityField()
    toplatitude = QuakeMLQuantityField()
    topdepth = QuakeMLQuantityField()
    bottomlongitude = QuakeMLQuantityField()
    bottomlatitude = QuakeMLQuantityField()
    bottomdepth = QuakeMLQuantityField()
    holediameter = QuakeMLQuantityField()
    casingdiameter = QuakeMLQuantityField()

    topclosed = fields.Boolean()
    bottomclosed = fields.Boolean()
    sectiontype = fields.String()
    casingtype = fields.String()
    description = fields.String()


class SectionHydraulicSampleSchema(SectionSchema, SchemaBase):

    hydraulics = fields.Nested(HydraulicSampleSchema, many=True,
                               attribute='_hydraulics')


class BoreholeSchema(SchemaBase):
    """
    Schema implementation of a borehole.
    """
    # TODO(damb): Provide a hierarchical implementation of sub_types; create
    # them dynamically (see: e.g. QuakeMLQuantityField)
    publicid = fields.String()
    longitude = QuakeMLQuantityField()
    latitude = QuakeMLQuantityField()
    depth = QuakeMLQuantityField()
    bedrockdepth = QuakeMLQuantityField()

    literature_source = LiteratureSource()

class BoreholeSectionSchema(BoreholeSchema, SchemaBase):
    sections = fields.Nested(SectionSchema, many=True,
                             attribute='_sections')

class BoreholeSectionHydraulicSampleSchema(BoreholeSchema, SchemaBase):
    sections = fields.Nested(SectionHydraulicSampleSchema, many=True,
                             attribute='_sections')
