"""
HYDWS datamodel ORM entity de-/serialization facilities.
"""
import logging

import datetime

from marshmallow import Schema, fields, post_dump, pre_load, missing, validate
from marshmallow.utils import get_value
from collections import defaultdict
from functools import reduce, partial
from operator import getitem

from hydws.server.v1.ostream import schema_literaturesource as sdc
from hydws.db.orm import Borehole


_ATTR_PREFIX = 'm_'



ValidateLatitude = validate.Range(min=-90., max=90.)
ValidateLongitude = validate.Range(min=-180., max=180.)
ValidatePositive = validate.Range(min=0.)
ValidateConfidenceLevel = validate.Range(min=0., max=100.)
ValidateCelcius = validate.Range(min=-273.15)

Datetime = fields.DateTime(format='iso')
Degree = partial(fields.Float)
Latitude = partial(Degree, validate=ValidateLatitude)
Longitude = partial(Degree, validate=ValidateLongitude)
Uncertainty = partial(fields.Float, validate=ValidatePositive)
ConfidenceLevel = partial(fields.Float, validate=ValidateConfidenceLevel)
Depth = partial(fields.Float, validate=ValidatePositive)
BedrockDepth = partial(fields.Float, validate=ValidatePositive)
MeasuredDepth = partial(fields.Float, validate=ValidatePositive)
Diameter = partial(fields.Float, validate=ValidatePositive)
Temperature = partial(fields.Float, validate=ValidateCelcius)
Pressure = partial(fields.Float, validate=ValidatePositive)
Flow = partial(fields.Float, validate=ValidatePositive)
FluidPh = partial(fields.Float, validate=ValidatePositive)
FluidViscosity = partial(fields.Float, validate=ValidatePositive)
FluidDensity = partial(fields.Float, validate=ValidatePositive)


class SchemaBase(Schema):
    """Schema base class for object de-/serialization.

    """
    @classmethod
    def remove_empty(self, data):
        """
        Filter out fields with empty (e.g. :code:`None`, :code:`[], etc.)
        values.
        """
        return {k: v for k, v in data.items() if v}

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
    """Schema implementation of literature source and creation info
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
    """Schema implementation of literature source and creation info
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
    """Schema implementation of literature source and creation info
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
    """Schema implementation of literature source and creation info
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
    """Schema implementation of literature source and creation info
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
    """Schema implementation of literature source and creation info
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
    """Schema implementation of an hydraulic data sample.

    """
    datetime_value = Datetime
    datetime_uncertainty = Uncertainty()
    datetime_loweruncertainty = Uncertainty()
    datetime_upperuncertainty = Uncertainty()
    datetime_confidencelevel = ConfidenceLevel()

    toptemperature_value = Temperature()
    toptemperature_uncertainty = Uncertainty()
    toptemperature_loweruncertainty = Uncertainty()
    toptemperature_upperuncertainty = Uncertainty()
    toptemperature_confidencelevel = ConfidenceLevel()

    bottomtemperature_value = Temperature()
    bottomtemperature_uncertainty = Uncertainty()
    bottomtemperature_loweruncertainty = Uncertainty()
    bottomtemperature_upperuncertainty = Uncertainty()
    bottomtemperature_confidencelevel = ConfidenceLevel()

    topflow_value = Flow()
    topflow_uncertainty = Uncertainty()
    topflow_loweruncertainty = Uncertainty()
    topflow_upperuncertainty = Uncertainty()
    topflow_confidencelevel = ConfidenceLevel()

    bottomflow_value = Flow()
    bottomflow_uncertainty = Uncertainty()
    bottomflow_loweruncertainty = Uncertainty()
    bottomflow_upperuncertainty = Uncertainty()
    bottomflow_confidencelevel = ConfidenceLevel()

    toppressure_value = Pressure()
    toppressure_uncertainty = Uncertainty()
    toppressure_loweruncertainty = Uncertainty()
    toppressure_upperuncertainty = Uncertainty()
    toppressure_confidencelevel = ConfidenceLevel()

    bottompressure_value = Pressure()
    bottompressure_uncertainty = Uncertainty()
    bottompressure_loweruncertainty = Uncertainty()
    bottompressure_upperuncertainty = Uncertainty()
    bottompressure_confidencelevel = ConfidenceLevel()

    fluiddensity_value = FluidDensity()
    fluiddensity_uncertainty = Uncertainty()
    fluiddensity_loweruncertainty = Uncertainty()
    fluiddensity_upperuncertainty = Uncertainty()
    fluiddensity_confidencelevel = ConfidenceLevel()

    fluidviscosity_value = FluidViscosity()
    fluidviscosity_uncertainty = Uncertainty()
    fluidviscosity_loweruncertainty = Uncertainty()
    fluidviscosity_upperuncertainty = Uncertainty()
    fluidviscosity_confidencelevel = ConfidenceLevel()

    fluidph_value = FluidPh()
    fluidph_uncertainty = Uncertainty()
    fluidph_loweruncertainty = Uncertainty()
    fluidph_upperuncertainty = Uncertainty()
    fluidph_confidencelevel = ConfidenceLevel()

    fluidcomposition = fields.String()


class SectionSchema(SchemaBase):
    """Schema implementation of a borehole section.

    """
    publicid = fields.String()
    starttime = Datetime
    endtime = Datetime

    toplongitude_value = Longitude()
    toplongitude_uncertainty = Uncertainty()
    toplongitude_loweruncertainty = Uncertainty()
    toplongitude_upperuncertainty = Uncertainty()
    toplongitude_confidencelevel = ConfidenceLevel()

    bottomlongitude_value = Longitude()
    bottomlongitude_uncertainty = Uncertainty()
    bottomlongitude_loweruncertainty = Uncertainty()
    bottomlongitude_upperuncertainty = Uncertainty()
    bottomlongitude_confidencelevel = ConfidenceLevel()

    toplatitude_value = Latitude()
    toplatitude_uncertainty = Uncertainty()
    toplatitude_loweruncertainty = Uncertainty()
    toplatitude_upperuncertainty = Uncertainty()
    toplatitude_confidencelevel = ConfidenceLevel()

    bottomlatitude_value = Latitude()
    bottomlatitude_uncertainty = Uncertainty()
    bottomlatitude_loweruncertainty = Uncertainty()
    bottomlatitude_upperuncertainty = Uncertainty()
    bottomlatitude_confidencelevel = ConfidenceLevel()

    topdepth_value = Depth()
    topdepth_uncertainty = Uncertainty()
    topdepth_loweruncertainty = Uncertainty()
    topdepth_upperuncertainty = Uncertainty()
    topdepth_confidencelevel = ConfidenceLevel()

    bottomdepth_value = Depth()
    bottomdepth_uncertainty = Uncertainty()
    bottomdepth_loweruncertainty = Uncertainty()
    bottomdepth_upperuncertainty = Uncertainty()
    bottomdepth_confidencelevel = ConfidenceLevel()


    holediameter_value = Diameter()
    holediameter_uncertainty = Uncertainty()
    holediameter_loweruncertainty = Uncertainty()
    holediameter_upperuncertainty = Uncertainty()
    holediameter_confidencelevel = ConfidenceLevel()


    casingdiameter_value = Diameter()
    casingdiameter_uncertainty = Uncertainty()
    casingdiameter_loweruncertainty = Uncertainty()
    casingdiameter_upperuncertainty = Uncertainty()
    casingdiameter_confidencelevel = ConfidenceLevel()


    topclosed = fields.Boolean()
    bottomclosed = fields.Boolean()
    sectiontype = fields.String()
    casingtype = fields.String()
    description = fields.String()

    hydraulics = fields.Nested(HydraulicSampleSchema, many=True,
                               attribute='_hydraulics')


class BoreholeSchema(LiteratureSourceCreationInfoSchema, SchemaBase):
    """Schema implementation of a borehole."""
    # TODO(damb): Provide a hierarchical implementation of sub_types; create
    # them dynamically (see: e.g. QuakeMLQuantityField)
    publicid = fields.String()

    longitude_value = Longitude()
    longitude_uncertainty = Uncertainty()
    longitude_loweruncertainty = Uncertainty()
    longitude_upperuncertainty = Uncertainty()
    longitude_confidencelevel = ConfidenceLevel()

    latitude_value = Latitude()
    latitude_uncertainty = Uncertainty()
    latitude_loweruncertainty = Uncertainty()
    latitude_upperuncertainty = Uncertainty()
    latitude_confidencelevel = ConfidenceLevel()

    depth_value = Depth()
    depth_uncertainty = Uncertainty()
    depth_loweruncertainty = Uncertainty()
    depth_upperuncertainty = Uncertainty()
    depth_confidencelevel = ConfidenceLevel()

    bedrockdepth_value = BedrockDepth()
    bedrockdepth_uncertainty = Uncertainty()
    bedrockdepth_loweruncertainty = Uncertainty()
    bedrockdepth_upperuncertainty = Uncertainty()
    bedrockdepth_confidencelevel = ConfidenceLevel()

    measureddepth_value = MeasuredDepth()
    measureddepth_uncertainty = Uncertainty()
    measureddepth_loweruncertainty = Uncertainty()
    measureddepth_upperuncertainty = Uncertainty()
    measureddepth_confidencelevel = ConfidenceLevel()

    sections = fields.Nested(SectionSchema, many=True,
                               attribute='_sections')
