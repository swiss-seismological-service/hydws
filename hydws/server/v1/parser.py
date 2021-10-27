"""
.. module:: parser
   :synopsis: HYDWS parser related facilities.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""
import datetime
import functools

from marshmallow import (Schema, fields, pre_load, validates_schema,
                         validate, ValidationError)

from hydws.server import settings
from hydws.server.misc import from_fdsnws_datetime, fdsnws_isoformat

Format = functools.partial(
    fields.String,
    missing=settings.HYDWS_DEFAULT_OFORMAT,
    validate=validate.OneOf(settings.HYDWS_OFORMATS))


LevelSection = functools.partial(
    fields.String,
    missing=settings.HYDWS_DEFAULT_LEVEL,
    validate=validate.OneOf(settings.HYDWS_SECTION_LEVELS))

LevelHydraulic = functools.partial(
    fields.String,
    missing=settings.HYDWS_DEFAULT_LEVEL,
    validate=validate.OneOf(settings.HYDWS_HYDRAULIC_LEVELS))

NoData = functools.partial(
    fields.Int,
    as_string=True,
    missing=settings.FDSN_DEFAULT_NO_CONTENT_ERROR_CODE,
    validate=validate.OneOf(settings.FDSN_NO_CONTENT_CODES))


class FDSNWSDateTime(fields.DateTime):
    """
    The class extends marshmallow standard :code:`DateTime` with a FDSNWS
    *datetime* format.

    The FDSNWS *datetime* format is described in the `FDSN Web Service
    Specifications
    <http://www.fdsn.org/webservices/FDSN-WS-Specifications-1.1.pdf>`_.
    """

    SERIALIZATION_FUNCS = fields.DateTime.SERIALIZATION_FUNCS.copy()

    DESERIALIZATION_FUNCS = fields.DateTime.DESERIALIZATION_FUNCS.copy()

    SERIALIZATION_FUNCS['fdsnws'] = fdsnws_isoformat
    DESERIALIZATION_FUNCS['fdsnws'] = from_fdsnws_datetime


class GeneralSchema(Schema):
    """
    Common HYDWS parser schema
    """
    LOGGER = 'hydws.server.v1.parserschema'

    nodata = NoData()
    format = Format()

    class Meta:
        strict = True
        ordered = True

class TimeConstraintsSchemaMixin(Schema):
    """
    Schema for time related query parameters.
    """

    starttime = FDSNWSDateTime(format='fdsnws')
    start = fields.Str(load_only=True)

    endtime = FDSNWSDateTime(format='fdsnws', allow_none=True)
    end = fields.Str(load_only=True)

    @pre_load
    def merge_keys(self, data):
        """
        Merge alternative field parameter values.

        .. note::

            The default :py:mod:`webargs` parser does not provide this feature
            by default such that :code:`load_only` field parameters are
            separated handled.
        """
        _mappings = [
            ('start', 'starttime'),
            ('end', 'endtime')]

        for alt_key, key in _mappings:
            if alt_key in data and key not in data:
                data[key] = data[alt_key]
                data.pop(alt_key)

        return data

    @validates_schema
    def validate_temporal_constraints(self, data):
        """
        Validation of temporal constraints.
        """
        starttime = data.get('starttime')
        endtime = data.get('endtime')
        now = datetime.datetime.utcnow()

        if not endtime:
            endtime = now
        elif endtime > now:
            endtime = now
            # XXX(damb): Silently correct the endtime if in future
            data['endtime'] = None

        if starttime:
            if starttime > now:
                raise ValidationError('starttime in future')
            elif starttime >= endtime:
                raise ValidationError(
                    'endtime must be greater than starttime')


class LocationConstraintsSchemaMixin(Schema):
    """
    Query parameters for boreholes, location specific.
    """
    minlatitude = fields.Float()
    maxlatitude = fields.Float()
    minlongitude = fields.Float()
    maxlongitude = fields.Float()
    # do validations on what is accepted as lat and lon

    @validates_schema
    def validate_lat_long_constraints(self, data):
        """
        Validation of latitude and longitude constraints.
        """
        maxlatitude = data.get('maxlatitude')
        minlatitude = data.get('minlatitude')
        maxlongitude = data.get('maxlongitude')
        minlongitude = data.get('minlongitude')

        if maxlatitude and maxlatitude > 90.0:
            raise ValidationError('maxlatitude greater than 90 degrees')
        if minlatitude and minlatitude < -90.0:
            raise ValidationError('minlatitude less than -90 degrees')
        if maxlongitude and maxlongitude > 180.0:
            raise ValidationError('maxlongitude greater than 180 degrees')
        if minlongitude and minlongitude > -180.0:
            raise ValidationError('minlongitude greater than -180 degrees')

        if maxlatitude and minlatitude and maxlatitude < minlatitude:
            raise ValidationError('maxlatitude must be greater than'
                                  'minlatitude')

        if maxlongitude and minlongitude and maxlongitude < minlongitude:
            raise ValidationError('maxlongitude must be greater than'
                                  'minlongitude')


class SectionSchemaMixin(TimeConstraintsSchemaMixin, Schema):
    """
    Query parameters for section data.
    """
    maxcasingdiameter = fields.Float()
    mincasingdiameter = fields.Float()
    maxholediameter = fields.Float()
    minholediameter = fields.Float()
    maxtopaltitude = fields.Float()
    mintopaltitude = fields.Float()
    maxbottomaltitude = fields.Float()
    minbottomaltitude = fields.Float()
    topclosed = fields.Boolean()
    bottomclosed = fields.Boolean()
    casingtype = fields.String()
    sectiontype = fields.String()


class HydraulicsSchemaMixin(TimeConstraintsSchemaMixin, Schema):
    """
    Query parameters for hydraulics data.
    """
    minbottomflow = fields.Float()
    maxbottomflow = fields.Float()
    mintopflow = fields.Float()
    maxtopflow = fields.Float()
    minbottompressure = fields.Float()
    maxbottompressure = fields.Float()
    mintoppressure = fields.Float()
    maxtoppressure = fields.Float()
    mintoptemperature = fields.Float()
    maxtoptemperature = fields.Float()
    minbottomtemperature = fields.Float()
    maxbottomtemperature = fields.Float()
    minfluiddensity = fields.Float()
    maxfluiddensity = fields.Float()
    minfluidviscosity = fields.Float()
    maxfluidviscosity = fields.Float()
    minfluidph = fields.Float()
    maxfluidph = fields.Float()
    limit = fields.Integer()
    offset = fields.Integer()


class BoreholeHydraulicSampleListResourceSchema(HydraulicsSchemaMixin,
                                                SectionSchemaMixin,
                                                GeneralSchema):
    """
    Hydraulic params are not allowed if section in
    (borehole, section), and section params are not allowed
    if level = borehole

    :raises: ValidationError.
    """
    level = LevelHydraulic()

    @validates_schema
    def validate_level_query_params(self, data):
        """If the hydraulic data is not included in the response,
        raise ValidationError on hydraulic level query parameters.
        """
        if data.get('level') in ('borehole', 'section'):
            hydraulic_params = HydraulicsSchemaMixin(
                exclude=['starttime', 'endtime']).dump(data)
            if hydraulic_params:
                raise ValidationError(
                    'Hydraulic query parameters not allowed: {}'.
                    format(hydraulic_params))

        if data.get('level') == 'borehole':
            section_params = SectionSchemaMixin().dump(data)
            if section_params:
                raise ValidationError(
                    'Section query parameters not allowed: {}'.
                    format(section_params))


class BoreholeListResourceSchema(TimeConstraintsSchemaMixin,
                                 LocationConstraintsSchemaMixin,
                                 GeneralSchema):

    """
    Handle optional query parameters for call returning borehole
    data for geographical area optionally including section data.
    """
    level = LevelSection()


class SectionHydraulicSampleListResourceSchema(HydraulicsSchemaMixin,
                                               GeneralSchema):
    """
    Handle optional query parameters for call returning hydraulics
    data for specified borehole id and section id.
    """
    pass

class NewUserResourceSchema(GeneralSchema):
    """
    Handle arguments sent for a new user request
    """
    username = fields.String(required=True)
    password = fields.String(required=True)
