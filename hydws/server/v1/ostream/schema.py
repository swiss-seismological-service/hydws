"""
.. module:: schema
   :synopsis: HYDWS datamodel ORM entity de-/serialization facilities.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""
import datetime
import logging
from functools import partial
from marshmallow import (Schema, fields, post_dump, pre_load,
    validate, validates_schema, post_load)
from hydws.db.orm import Borehole, BoreholeSection, HydraulicSample


VALIDATE_LATITUDE = validate.Range(min=-90., max=90.)
VALIDATE_LONGITUDE = validate.Range(min=-180., max=180.)
VALIDATE_POSITIVE = validate.Range(min=0.)
VALIDATE_CONFIDENCE_LEVEL = validate.Range(min=0., max=100.)
VALIDATE_KELVIN = validate.Range(min=0.)
VALIDATE_PH = validate.Range(min=0., max=14)

Datetime = partial(fields.DateTime, format='iso')
DatetimeRequired = partial(Datetime, required=True)
Degree = partial(fields.Float)
FloatPositive = partial(fields.Float, validate=VALIDATE_POSITIVE)
Latitude = partial(Degree, validate=VALIDATE_LATITUDE)
RequiredLatitude = partial(Latitude, required=True)
Longitude = partial(Degree, validate=VALIDATE_LONGITUDE)
RequiredLongitude = partial(Longitude, required=True)
ConfidenceLevel = partial(fields.Float, validate=VALIDATE_CONFIDENCE_LEVEL)
Temperature = partial(fields.Float, validate=VALIDATE_KELVIN)
FluidPh = partial(fields.Float, validate=VALIDATE_PH)

class SchemaBase(Schema):
    """
    Schema base class for object de-/serialization.
    """
    @classmethod
    def remove_empty(self, data):
        """
        Filter out fields with empty (e.g. :code:`None`, :code:`[], etc.)
        values.
        """
        return {k: v for k, v in data.items() if v or isinstance(v, (int, float))}

    @classmethod
    def _flatten_dict(cls, data, sep='_'):
        """
        Flatten a a nested dict :code:`dict` using :code:`sep` as key
        separator.
        """
        retval = {}
        for k, v in data.items():
            if isinstance(v, dict):
                for sub_k, sub_v in cls._flatten_dict(v, sep).items():
                    retval[k + sep + sub_k] = sub_v
            else:
                retval[k] = v

        return retval

    @classmethod
    def _nest_dict(cls, data, sep='_'):
        """
        Nest a dictionary by splitting the key on a delimiter.
        """
        retval = {}
        for k, v in data.items():
            t = retval
            prev = None
            for part in k.split(sep):
                if prev is not None:
                    t = t.setdefault(prev, {})
                prev = part
            else:
                t.setdefault(prev, v)

        return retval

    @post_dump
    def postdump(self, data):
        filtered_data = self.remove_empty(data)
        nested_data = self._nest_dict(filtered_data, sep='_')
        return nested_data

    @pre_load
    def preload(self, data):
        flattened_data = self._flatten_dict( data, sep='_')
        return flattened_data


class CreationInfoSchema(SchemaBase):
    """
    Schema implementation of literature source and creation info
    defined levels.
    """
    creationinfo_author = fields.String()
    creationinfo_authoruri_resourceid = fields.String()
    creationinfo_agencyid = fields.String()
    creationinfo_agencyuri_resourceid = fields.String()
    creationinfo_creationtime = fields.String()
    creationinfo_version = fields.String()
    creationinfo_copyrightowner = fields.String()
    creationinfo_copyrightowneruri_resourceid = fields.String()
    creationinfo_license = fields.String()


class LSCreatorPersonSchema(SchemaBase):
    """
    Schema implementation of literature source and creation info
    defined levels.
    """
    literaturesource_creator_person_name = fields.String()
    literaturesource_creator_person_givenname = fields.String()
    literaturesource_creator_person_familyname = fields.String()
    literaturesource_creator_person_title = fields.String()
    literaturesource_creator_person_personid_resourceid = fields.String()
    literaturesource_creator_person_alternatepersonid_resourceid = fields.String()
    literaturesource_creator_person_mbox_resourceid = fields.String()
    literaturesource_creator_person_phone_resourceid = fields.String()
    literaturesource_creator_person_homepage_resourcelocator = fields.String()
    literaturesource_creator_person_workplacehomepage_resourcelocator = fields.String()


class LSCreatorAffiliationSchema(SchemaBase):
    """
    Schema implementation of literature source and creation info
    defined levels.
    """
    literaturesource_creator_affiliation_institution_name = fields.String()
    literaturesource_creator_affiliation_institution_identifier_resourceid = fields.String()
    literaturesource_creator_affiliation_institution_mbox_resourceid = fields.String()
    literaturesource_creator_affiliation_institution_phone_resourceid = fields.String()
    literaturesource_creator_affiliation_institution_homepage_resourcelocator = fields.String()
    literaturesource_creator_affiliation_institution_postaladdress_streetaddress = fields.String()
    literaturesource_creator_affiliation_institution_postaladdress_locality = fields.String()
    literaturesource_creator_affiliation_institution_postaladdress_postalcode = fields.String()
    literaturesource_creator_affiliation_institution_postaladdress_country_uri_resourceid = fields.String()
    literaturesource_creator_affiliation_institution_postaladdress_country_code = fields.String()
    literaturesource_creator_affiliation_institution_postaladdress_country_country = fields.String()
    literaturesource_creator_affiliation_department = fields.String()
    literaturesource_creator_affiliation_function = fields.String()

    literaturesource_creator_affiliation_comment_comment = fields.String()
    literaturesource_creator_affiliation_comment_id_resourceid = fields.String()
    literaturesource_creator_affiliation_comment_creationinfo_author = fields.String()
    literaturesource_creator_affiliation_comment_creationinfo_authoruri_resourceid = fields.String()
    literaturesource_creator_affiliation_comment_creationinfo_agencyid = fields.String()
    literaturesource_creator_affiliation_comment_creationinfo_agencyuri_resourceid = fields.String()
    literaturesource_creator_affiliation_comment_creationinfo_creationtime = fields.String()
    literaturesource_creator_affiliation_comment_creationinfo_version = fields.String()
    literaturesource_creator_affiliation_comment_creationinfo_copyrightowner = fields.String()
    literaturesource_creator_affiliation_comment_creationinfo_copyrightowneruri_resourceid = fields.String()
    literaturesource_creator_affiliation_comment_creationinfo_license = fields.String()


class LSCreatorAlternateAffiliationSchema(SchemaBase):
    """
    Schema implementation of literature source and creation info
    defined levels.
    """
    literaturesource_creator_alternateaffiliation_institution_name = fields.String()
    literaturesource_creator_alternateaffiliation_institution_identifier_resourceid = fields.String()
    literaturesource_creator_alternateaffiliation_institution_mbox_resourceid = fields.String()
    literaturesource_creator_alternateaffiliation_institution_phone_resourceid = fields.String()
    literaturesource_creator_alternateaffiliation_institution_homepage_resourcelocator = fields.String()
    literaturesource_creator_alternateaffiliation_institution_postaladdress_streetaddress = fields.String()
    literaturesource_creator_alternateaffiliation_institution_postaladdress_locality = fields.String()
    literaturesource_creator_alternateaffiliation_institution_postaladdress_postalcode = fields.String()
    literaturesource_creator_alternateaffiliation_institution_postaladdress_country_uri_resourceid = fields.String()
    literaturesource_creator_alternateaffiliation_institution_postaladdress_country_code = fields.String()
    literaturesource_creator_alternateaffiliation_institution_postaladdress_country_country = fields.String()

    literaturesource_creator_alternateaffiliation_department = fields.String()
    literaturesource_creator_alternateaffiliation_function = fields.String()
    literaturesource_creator_alternateaffiliation_comment_comment = fields.String()
    literaturesource_creator_alternateaffiliation_comment_id_resourceid = fields.String()
    literaturesource_creator_alternateaffiliation_comment_creationinfo_author = fields.String()
    literaturesource_creator_alternateaffiliation_comment_creationinfo_authoruri_resourceid = fields.String()
    literaturesource_creator_alternateaffiliation_comment_creationinfo_agencyid = fields.String()
    literaturesource_creator_alternateaffiliation_comment_creationinfo_agencyuri_resourceid = fields.String()
    literaturesource_creator_alternateaffiliation_comment_creationinfo_creationtime = fields.String()
    literaturesource_creator_alternateaffiliation_comment_creationinfo_version = fields.String()
    literaturesource_creator_alternateaffiliation_comment_creationinfo_copyrightowner = fields.String()
    literaturesource_creator_alternateaffiliation_comment_creationinfo_copyrightowneruri_resourceid = fields.String()
    literaturesource_creator_alternateaffiliation_comment_creationinfo_license = fields.String()


class LSCreatorSchema(SchemaBase):
    """
    Schema implementation of literature source and creation info
    defined levels.
    """
    literaturesource_creator_mbox_resourceid = fields.String()
    literaturesource_creator_comment_comment = fields.String()
    literaturesource_creator_comment_id_resourceid = fields.String()
    literaturesource_creator_comment_creationinfo_author = fields.String()
    literaturesource_creator_comment_creationinfo_authoruri_resourceid = fields.String()
    literaturesource_creator_comment_creationinfo_agencyid = fields.String()
    literaturesource_creator_comment_creationinfo_agencyuri_resourceid = fields.String()
    literaturesource_creator_comment_creationinfo_creationtime = fields.String()
    literaturesource_creator_comment_creationinfo_version = fields.String()
    literaturesource_creator_comment_creationinfo_copyrightowner = fields.String()
    literaturesource_creator_comment_creationinfo_copyrightowneruri_resourceid = fields.String()
    literaturesource_creator_comment_creationinfo_license = fields.String()


class LiteratureSourceCreationInfoSchema(
        LSCreatorSchema,
        LSCreatorAlternateAffiliationSchema,
        LSCreatorAffiliationSchema,
        LSCreatorPersonSchema,
        CreationInfoSchema, SchemaBase):
    """
    Schema implementation of literature source and creation info
    defined levels.
    """
    literaturesource_identifier_resourceid = fields.String()
    literaturesource_type_uri_resourceid = fields.String()
    literaturesource_type_type = fields.String()
    literaturesource_bibtextype = fields.String()
    literaturesource_type_code = fields.String()
    literaturesource_type_language = fields.String()
    literaturesource_title = fields.String()
    literaturesource_author = fields.String()
    literaturesource_editor = fields.String()
    literaturesource_bibliographiccitation = fields.String()
    literaturesource_date = fields.String()
    literaturesource_booktitle = fields.String()
    literaturesource_volume = fields.String()
    literaturesource_number = fields.String()
    literaturesource_series = fields.String()
    literaturesource_issue = fields.String()
    literaturesource_year = fields.String()
    literaturesource_edition = fields.String()
    literaturesource_startpage = fields.String()
    literaturesource_endpage = fields.String()
    literaturesource_publisher = fields.String()
    literaturesource_address = fields.String()
    literaturesource_rights = fields.String()
    literaturesource_rightsholder = fields.String()
    literaturesource_accessrights = fields.String()
    literaturesource_license = fields.String()
    literaturesource_publicationstatus = fields.String()


class HydraulicSampleSchema(SchemaBase):
    """
    Schema implementation of an hydraulic data sample.
    """
    datetime_value = DatetimeRequired()
    datetime_uncertainty = FloatPositive()
    datetime_loweruncertainty = FloatPositive()
    datetime_upperuncertainty = FloatPositive()
    datetime_confidencelevel = ConfidenceLevel()

    toptemperature_value = Temperature()
    toptemperature_uncertainty = FloatPositive()
    toptemperature_loweruncertainty = FloatPositive()
    toptemperature_upperuncertainty = FloatPositive()
    toptemperature_confidencelevel = ConfidenceLevel()

    bottomtemperature_value = Temperature()
    bottomtemperature_uncertainty = FloatPositive()
    bottomtemperature_loweruncertainty = FloatPositive()
    bottomtemperature_upperuncertainty = FloatPositive()
    bottomtemperature_confidencelevel = ConfidenceLevel()

    topflow_value = fields.Float()
    topflow_uncertainty = FloatPositive()
    topflow_loweruncertainty = FloatPositive()
    topflow_upperuncertainty = FloatPositive()
    topflow_confidencelevel = ConfidenceLevel()

    bottomflow_value = fields.Float()
    bottomflow_uncertainty = FloatPositive()
    bottomflow_loweruncertainty = FloatPositive()
    bottomflow_upperuncertainty = FloatPositive()
    bottomflow_confidencelevel = ConfidenceLevel()

    toppressure_value = FloatPositive()
    toppressure_uncertainty = FloatPositive()
    toppressure_loweruncertainty = FloatPositive()
    toppressure_upperuncertainty = FloatPositive()
    toppressure_confidencelevel = ConfidenceLevel()

    bottompressure_value = FloatPositive()
    bottompressure_uncertainty = FloatPositive()
    bottompressure_loweruncertainty = FloatPositive()
    bottompressure_upperuncertainty = FloatPositive()
    bottompressure_confidencelevel = ConfidenceLevel()

    fluiddensity_value = FloatPositive()
    fluiddensity_uncertainty = FloatPositive()
    fluiddensity_loweruncertainty = FloatPositive()
    fluiddensity_upperuncertainty = FloatPositive()
    fluiddensity_confidencelevel = ConfidenceLevel()

    fluidviscosity_value = FloatPositive()
    fluidviscosity_uncertainty = FloatPositive()
    fluidviscosity_loweruncertainty = FloatPositive()
    fluidviscosity_upperuncertainty = FloatPositive()
    fluidviscosity_confidencelevel = ConfidenceLevel()

    fluidph_value = FluidPh()
    fluidph_uncertainty = FloatPositive()
    fluidph_loweruncertainty = FloatPositive()
    fluidph_upperuncertainty = FloatPositive()
    fluidph_confidencelevel = ConfidenceLevel()

    fluidcomposition = fields.String()
    @post_load
    def make_hydraulics(self, data):
        return HydraulicSample(**data)

class SectionSchema(SchemaBase):
    """
    Schema implementation of a borehole section.
    """
    publicid = fields.String(required=True)
    starttime = DatetimeRequired()
    endtime = Datetime()

    toplongitude_value = Longitude()
    toplongitude_uncertainty = FloatPositive()
    toplongitude_loweruncertainty = FloatPositive()
    toplongitude_upperuncertainty = FloatPositive()
    toplongitude_confidencelevel = ConfidenceLevel()

    bottomlongitude_value = Longitude()
    bottomlongitude_uncertainty = FloatPositive()
    bottomlongitude_loweruncertainty = FloatPositive()
    bottomlongitude_upperuncertainty = FloatPositive()
    bottomlongitude_confidencelevel = ConfidenceLevel()

    toplatitude_value = Latitude()
    toplatitude_uncertainty = FloatPositive()
    toplatitude_loweruncertainty = FloatPositive()
    toplatitude_upperuncertainty = FloatPositive()
    toplatitude_confidencelevel = ConfidenceLevel()

    bottomlatitude_value = Latitude()
    bottomlatitude_uncertainty = FloatPositive()
    bottomlatitude_loweruncertainty = FloatPositive()
    bottomlatitude_upperuncertainty = FloatPositive()
    bottomlatitude_confidencelevel = ConfidenceLevel()

    topdepth_value = FloatPositive()
    topdepth_uncertainty = FloatPositive()
    topdepth_loweruncertainty = FloatPositive()
    topdepth_upperuncertainty = FloatPositive()
    topdepth_confidencelevel = ConfidenceLevel()

    bottomdepth_value = FloatPositive()
    bottomdepth_uncertainty = FloatPositive()
    bottomdepth_loweruncertainty = FloatPositive()
    bottomdepth_upperuncertainty = FloatPositive()
    bottomdepth_confidencelevel = ConfidenceLevel()


    holediameter_value = FloatPositive()
    holediameter_uncertainty = FloatPositive()
    holediameter_loweruncertainty = FloatPositive()
    holediameter_upperuncertainty = FloatPositive()
    holediameter_confidencelevel = ConfidenceLevel()


    casingdiameter_value = FloatPositive()
    casingdiameter_uncertainty = FloatPositive()
    casingdiameter_loweruncertainty = FloatPositive()
    casingdiameter_upperuncertainty = FloatPositive()
    casingdiameter_confidencelevel = ConfidenceLevel()

    topclosed = fields.Boolean(required=True)
    bottomclosed = fields.Boolean(required=True)
    sectiontype = fields.String()
    casingtype = fields.String()
    description = fields.String()

    hydraulics = fields.Nested(HydraulicSampleSchema, many=True,
                               attribute='_hydraulics')

    @validates_schema
    def validate_temporal_constraints(self, data):
        """Validation of temporal constraints."""
        starttime = data.get('starttime')
        endtime = data.get('endtime')
        now = datetime.datetime.utcnow()

        if starttime and endtime and starttime >= endtime:
                raise ValidationError(
                    'endtime must be greater than starttime')
    @post_load
    def make_section(self, data):
        return BoreholeSection(**data)

class BoreholeSchema(LiteratureSourceCreationInfoSchema,
                     SchemaBase):
    """Schema implementation of a borehole."""
    publicid = fields.String()

    longitude_value = RequiredLongitude()
    longitude_uncertainty = FloatPositive()
    longitude_loweruncertainty = FloatPositive()
    longitude_upperuncertainty = FloatPositive()
    longitude_confidencelevel = ConfidenceLevel()

    latitude_value = RequiredLatitude()
    latitude_uncertainty = FloatPositive()
    latitude_loweruncertainty = FloatPositive()
    latitude_upperuncertainty = FloatPositive()
    latitude_confidencelevel = ConfidenceLevel()

    depth_value = FloatPositive()
    depth_uncertainty = FloatPositive()
    depth_loweruncertainty = FloatPositive()
    depth_upperuncertainty = FloatPositive()
    depth_confidencelevel = ConfidenceLevel()

    bedrockdepth_value = FloatPositive()
    bedrockdepth_uncertainty = FloatPositive()
    bedrockdepth_loweruncertainty = FloatPositive()
    bedrockdepth_upperuncertainty = FloatPositive()
    bedrockdepth_confidencelevel = ConfidenceLevel()

    measureddepth_value = FloatPositive()
    measureddepth_uncertainty = FloatPositive()
    measureddepth_loweruncertainty = FloatPositive()
    measureddepth_upperuncertainty = FloatPositive()
    measureddepth_confidencelevel = ConfidenceLevel()

    sections = fields.Nested(SectionSchema, many=True,
                               attribute='_sections')

    @post_load
    def make_borehole(self, data):
        return Borehole(**data)
