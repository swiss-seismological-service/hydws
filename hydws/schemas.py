import uuid
from datetime import datetime
from typing import Callable, Generic, List, TypeVar

from pydantic import (BaseModel, ConfigDict, Field, computed_field,
                      create_model, field_validator)

base_config = ConfigDict(extra='allow',
                         arbitrary_types_allowed=True,
                         from_attributes=True,
                         use_enum_values=False)


class Model(BaseModel):
    model_config = base_config


class CreationInfoSchema(Model):
    author: str | None = None
    agencyid: str | None = None
    creationtime: datetime | None = None
    version: str | None = None
    copyrightowner: str | None = None
    licence: str | None = None


def creationinfo_factory(obj: Model) -> CreationInfoSchema:
    return CreationInfoSchema(
        author=obj.creationinfo_author,
        agencyid=obj.creationinfo_agencyid,
        creationtime=obj.creationinfo_creationtime,
        version=obj.creationinfo_version,
        copyrightowner=obj.creationinfo_copyrightowner,
        licence=obj.creationinfo_licence)


class CreationInfoMixin(Model):
    creationinfo_author: str | None = Field(default=None, exclude=True)
    creationinfo_agencyid: str | None = Field(default=None, exclude=True)
    creationinfo_creationtime: datetime = Field(default=None, exclude=True)
    creationinfo_version: str | None = Field(default=None, exclude=True)
    creationinfo_copyrightowner: str | None = Field(default=None, exclude=True)
    creationinfo_licence: str | None = Field(default=None, exclude=True)

    @computed_field
    @property
    def creationinfo(self) -> CreationInfoSchema:
        return creationinfo_factory(self)


DataT = TypeVar('DataT')


class RealValueSchema(Model, Generic[DataT]):
    value: DataT | None = None
    uncertainty: float | None = None
    loweruncertainty: float | None = None
    upperuncertainty: float | None = None
    confidencelevel: float | None = None


def real_float_value_factory(name: str, real_type: TypeVar) -> Callable:
    def create_schema(obj: Model) -> RealValueSchema[real_type]:
        return RealValueSchema[real_type](
            value=getattr(obj, f'{name}_value'),
            uncertainty=getattr(obj, f'{name}_uncertainty'),
            loweruncertainty=getattr(obj, f'{name}_loweruncertainty'),
            upperuncertainty=getattr(obj, f'{name}_upperuncertainty'),
            confidencelevel=getattr(obj, f'{name}_confidencelevel'))
    return create_schema


def real_float_value_mixin(field_name: str, real_type: TypeVar) -> Model:
    _func_map = dict([
        (f'{field_name}_value',
         (real_type | None, Field(default=None, exclude=True))),
        (f'{field_name}_uncertainty',
         (float | None, Field(default=None, exclude=True))),
        (f'{field_name}_loweruncertainty',
         (float | None, Field(default=None, exclude=True))),
        (f'{field_name}_upperuncertainty',
         (float | None, Field(default=None, exclude=True))),
        (f'{field_name}_confidencelevel',
         (float | None, Field(default=None, exclude=True))),
        (field_name,
         computed_field(real_float_value_factory(field_name, real_type)))
    ])

    retval = create_model(field_name, __base__=Model, **_func_map)

    return retval


class HydraulicSampleSchema(real_float_value_mixin('datetime', datetime),
                            real_float_value_mixin('bottomtemperature', float),
                            real_float_value_mixin('bottomflow', float),
                            real_float_value_mixin('bottompressure', float),
                            real_float_value_mixin('toptemperature', float),
                            real_float_value_mixin('topflow', float),
                            real_float_value_mixin('toppressure', float),
                            real_float_value_mixin('fluiddensity', float),
                            real_float_value_mixin('fluidviscosity', float),
                            real_float_value_mixin('fluidph', float)):

    fluidcomposition: str | None = None


class BoreholeSectionSchema(
        real_float_value_mixin('toplongitude', float),
        real_float_value_mixin('toplatitude', float),
        real_float_value_mixin('topaltitude', float),
        real_float_value_mixin('bottomlongitude', float),
        real_float_value_mixin('bottomlatitude', float),
        real_float_value_mixin('bottomaltitude', float),
        real_float_value_mixin('topmeasureddepth', float),
        real_float_value_mixin('bottommeasureddepth', float),
        real_float_value_mixin('holediameter', float),
        real_float_value_mixin('casingdiameter', float)):
    publicid: uuid.UUID
    starttime: datetime | None = None
    endtime: datetime | None = None
    topclosed: bool
    bottomclosed: bool
    sectiontype: str | None = None
    casingtype: str | None = None
    description: str | None = None
    name: str | None = None
    hydraulics: List[HydraulicSampleSchema] | None = None

    @field_validator("publicid")
    @classmethod
    def serialize_uuid(cls, value) -> uuid.UUID:
        if value:
            return uuid.UUID(str(value))


class BoreholeSchema(CreationInfoMixin,
                     real_float_value_mixin('longitude', float),
                     real_float_value_mixin('latitude', float),
                     real_float_value_mixin('altitude', float),
                     real_float_value_mixin('bedrockaltitude', float),
                     real_float_value_mixin('measureddepth', float)):
    publicid: uuid.UUID
    description: str | None = None
    name: str | None = None
    location: str | None = None
    institution: str | None = None
    sections: List[BoreholeSectionSchema] | None = None

    @field_validator("publicid")
    @classmethod
    def serialize_uuid(cls, value) -> uuid.UUID:
        if value:
            return uuid.UUID(str(value))


def flatten_dict(name: str, real_object: dict):
    return_dict = {}
    for real, value in real_object.items():
        return_dict[f'{name}_{real}'] = value
    return return_dict


def flatten_attributes(self_obj: object, schema_dict: dict):
    return_dict = {}
    for k, v in schema_dict.items():
        if isinstance(getattr(self_obj, k),
                      RealValueSchema):
            return_dict.update(**flatten_dict(k, v))
        elif isinstance(v, (str, int, float, bool, datetime)):
            return_dict[k] = v
    return return_dict


class HydraulicSampleJSONSchema(Model):
    datetime: RealValueSchema[datetime]

    bottomtemperature: RealValueSchema[float] | None = None
    bottomflow: RealValueSchema[float] | None = None
    bottompressure: RealValueSchema[float] | None = None

    toptemperature: RealValueSchema[float] | None = None
    topflow: RealValueSchema[float] = 0.0
    toppressure: RealValueSchema[float] = 0.0

    fluiddensity: RealValueSchema[float] | None = None
    fluidviscosity: RealValueSchema[float] | None = None
    fluidph: RealValueSchema[float] | None = None

    fluidcomposition: str | None = None

    def flat_dict(self, exclude_unset=False, exclude_defaults=False):
        schema_dict = self.model_dump(
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults)

        return_dict = flatten_attributes(self, schema_dict)

        return return_dict


class BoreholeSectionJSONSchema(Model):
    toplongitude: RealValueSchema[float] | None = None
    toplatitude: RealValueSchema[float] | None = None
    topaltitude: RealValueSchema[float] | None = None
    bottomlongitude: RealValueSchema[float] | None = None
    bottomlatitude: RealValueSchema[float] | None = None
    bottomaltitude: RealValueSchema[float] | None = None
    topmeasureddepth: RealValueSchema[float] | None = None
    bottommeasureddepth: RealValueSchema[float] | None = None
    holediameter: RealValueSchema[float] | None = None
    casingdiameter: RealValueSchema[float] | None = None

    publicid: str
    starttime: datetime | None = None
    endtime: datetime | None = None
    topclosed: bool = False
    bottomclosed: bool = False
    sectiontype: str | None = None
    casingtype: str | None = None
    description: str | None = None
    name: str
    hydraulics: List[HydraulicSampleJSONSchema] | None = None

    def flat_dict(self, exclude_unset=False, exclude_defaults=False):
        schema_dict = self.model_dump(
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults)

        return_dict = flatten_attributes(self, schema_dict)

        if hasattr(self, 'hydraulics') and \
                isinstance(self.hydraulics, list):
            return_dict['hydraulics'] = \
                [h.flat_dict() for h in self.hydraulics]

        return return_dict


class BoreholeJSONSchema(Model):
    creationinfo: CreationInfoSchema | None = None
    longitude: RealValueSchema[float] | None = None
    latitude: RealValueSchema[float] | None = None
    altitude: RealValueSchema[float] | None = None
    bedrockaltitude: RealValueSchema[float] | None = None
    measureddepth: RealValueSchema[float] | None = None
    publicid: str
    description: str | None = None
    name: str | None = None
    location: str | None = None
    institution: str | None = None
    sections: List[BoreholeSectionJSONSchema] | None = None

    def flat_dict(self, exclude_unset=False, exclude_defaults=False):
        schema_dict = self.model_dump(
            exclude={'sections': True},
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults)

        return_dict = flatten_attributes(self, schema_dict)

        if hasattr(self, 'sections') and \
                isinstance(self.sections, list):
            return_dict['sections'] = \
                [s.flat_dict() for s in self.sections]

        return return_dict
