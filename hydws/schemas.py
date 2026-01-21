import uuid
from datetime import datetime
from typing import Callable, Generic, List, Type, TypeVar

from pydantic import (BaseModel, ConfigDict, Field, computed_field,
                      create_model, field_validator, model_validator)

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
    license: str | None = None


def creationinfo_factory(obj: Model) -> CreationInfoSchema:
    return CreationInfoSchema(
        author=obj.creationinfo_author,
        agencyid=obj.creationinfo_agencyid,
        creationtime=obj.creationinfo_creationtime,
        version=obj.creationinfo_version,
        copyrightowner=obj.creationinfo_copyrightowner,
        license=obj.creationinfo_license)


class CreationInfoMixin(Model):
    creationinfo_author: str | None = Field(default=None, exclude=True)
    creationinfo_agencyid: str | None = Field(default=None, exclude=True)
    creationinfo_creationtime: datetime | None = Field(
        default=None, exclude=True)
    creationinfo_version: str | None = Field(default=None, exclude=True)
    creationinfo_copyrightowner: str | None = Field(default=None, exclude=True)
    creationinfo_license: str | None = Field(default=None, exclude=True)

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


def real_float_value_factory(name: str, real_type: Type) -> Callable:
    def create_schema(obj: Model) -> RealValueSchema:
        return RealValueSchema[real_type](
            value=getattr(obj, f'{name}_value'),
            uncertainty=getattr(obj, f'{name}_uncertainty'),
            loweruncertainty=getattr(obj, f'{name}_loweruncertainty'),
            upperuncertainty=getattr(obj, f'{name}_upperuncertainty'),
            confidencelevel=getattr(obj, f'{name}_confidencelevel'))
    return create_schema


def real_float_value_mixin(field_name: str, real_type: Type) -> type[Model]:
    field_definitions = {
        f'{field_name}_value':
            (real_type | None, Field(default=None, exclude=True)),
        f'{field_name}_uncertainty':
            (float | None, Field(default=None, exclude=True)),
        f'{field_name}_loweruncertainty':
            (float | None, Field(default=None, exclude=True)),
        f'{field_name}_upperuncertainty':
            (float | None, Field(default=None, exclude=True)),
        f'{field_name}_confidencelevel':
            (float | None, Field(default=None, exclude=True)),
    }

    computed_fields = {
        field_name: computed_field(
            property(real_float_value_factory(field_name, real_type)),
            return_type=RealValueSchema[real_type]
        )
    }

    base_model = type(
        f'{field_name}BaseMixin',
        (Model,),
        computed_fields,
    )

    return create_model(field_name, __base__=base_model, **field_definitions)


def flatten_nested(data: dict) -> dict:
    """Flatten nested RealValueSchema/CreationInfo dicts to flat fields."""
    if not isinstance(data, dict):
        return data
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            if 'value' in value or key == 'creationinfo':
                for subkey, subvalue in value.items():
                    if subvalue is not None:
                        result[f'{key}_{subkey}'] = subvalue
            else:
                result[key] = value
        else:
            result[key] = value
    return result


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

    @model_validator(mode='before')
    @classmethod
    def handle_nested_input(cls, data):
        return flatten_nested(data)

    def flat_dict(self, exclude_unset=False, exclude_defaults=False) -> dict:
        """Return flat fields for DB operations."""
        result = {}
        fields_set = self.model_fields_set if exclude_unset else None
        for name in self.__class__.model_fields:
            if exclude_unset and name not in fields_set:
                continue
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        return result


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
    topclosed: bool | None = None
    bottomclosed: bool | None = None
    sectiontype: str | None = None
    casingtype: str | None = None
    description: str | None = None
    name: str
    hydraulics: List[HydraulicSampleSchema] | None = None

    @field_validator("publicid")
    @classmethod
    def serialize_uuid(cls, value) -> uuid.UUID | None:
        if value:
            return uuid.UUID(str(value))
        return None

    @model_validator(mode='before')
    @classmethod
    def handle_nested_input(cls, data):
        return flatten_nested(data)

    def flat_dict(self, exclude_unset=False, exclude_defaults=False) -> dict:
        """Return flat fields for DB operations."""
        result = {}
        fields_set = self.model_fields_set if exclude_unset else None
        for name in self.__class__.model_fields:
            if name == 'hydraulics':
                continue
            if exclude_unset and name not in fields_set:
                continue
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        if self.hydraulics:
            result['hydraulics'] = \
                [h.flat_dict(exclude_unset, exclude_defaults)
                 for h in self.hydraulics]
        return result


class BoreholeSchema(CreationInfoMixin,
                     real_float_value_mixin('longitude', float),
                     real_float_value_mixin('latitude', float),
                     real_float_value_mixin('altitude', float),
                     real_float_value_mixin('bedrockaltitude', float),
                     real_float_value_mixin('measureddepth', float)):
    publicid: uuid.UUID
    description: str | None = None
    name: str
    location: str | None = None
    institution: str | None = None
    sections: List[BoreholeSectionSchema] | None = None

    @field_validator("publicid")
    @classmethod
    def serialize_uuid(cls, value) -> uuid.UUID | None:
        if value:
            return uuid.UUID(str(value))
        return None

    @model_validator(mode='before')
    @classmethod
    def handle_nested_input(cls, data):
        return flatten_nested(data)

    def flat_dict(self, exclude_unset=False, exclude_defaults=False) -> dict:
        """Return flat fields for DB operations."""
        result = {}
        fields_set = self.model_fields_set if exclude_unset else None
        for name in self.__class__.model_fields:
            if name == 'sections':
                continue
            if exclude_unset and name not in fields_set:
                continue
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        if self.sections:
            result['sections'] = [s.flat_dict(exclude_unset, exclude_defaults)
                                  for s in self.sections]
        return result
