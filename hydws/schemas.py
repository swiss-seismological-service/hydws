from typing import Any, List, Optional, Type
from datetime import datetime
from pydantic import BaseConfig, BaseModel, create_model
from pydantic.utils import GetterDict
from sqlalchemy.inspection import inspect

BaseConfig.arbitrary_types_allowed = True
BaseConfig.orm_mode = True


def real_value_factory(quantity_type: type) -> Type[BaseModel]:
    _func_map = dict([
        ('value', (quantity_type, None)),
        ('uncertainty', (Optional[float], None)),
        ('loweruncertainty', (Optional[float], None)),
        ('upperuncertainty', (Optional[float], None)),
        ('confidencelevel', (Optional[float], None))
    ])

    retval = create_model(
        f'Real{quantity_type.__name__}',
        __config__=BaseConfig,
        **_func_map)
    return retval


def creationinfo_factory() -> Type[BaseModel]:
    _func_map = dict([
        ('author', (Optional[str], None)),
        ('agencyid', (Optional[str], None)),
        ('creationtime', (Optional[datetime], None)),
        ('version', (Optional[str], None)),
        ('copyrightowner', (Optional[str], None)),
        ('licence', (Optional[str], None)),
    ])
    retval = create_model(
        'CreationInfo',
        __config__=BaseConfig,
        **_func_map)
    return retval


class CreationInfo(creationinfo_factory()):
    pass


class RealFloatValue(real_value_factory(float)):
    pass


class RealDatetimeValue(real_value_factory(datetime)):
    pass


class ValueGetter(GetterDict):
    def get(self, key: str, default: Any) -> Any:
        # get SQLAlchemy's column names.
        cols = self._obj.__table__.columns.keys()
        cols += inspect(type(self._obj)).relationships.keys()

        # if the key-col mapping is 1:1 just return the value
        if f'm_{key}' in cols:
            return getattr(self._obj, key, default)
        elif f'_{key}' in cols:
            return getattr(self._obj, f'_{key}', default)

        # else it's probably a sub value
        # get all column names which are present for this key
        elem = [k for k in cols if k.startswith(f'm_{key}_')]
        if elem:
            # create a dict for the sub value
            return_dict = {}
            for k in elem:
                return_dict[k.split(
                    '_')[-1]] = getattr(self._obj, k[2:], default)
            return return_dict
        else:
            return default


def flatten_dict(name: str, real_object: dict):
    return_dict = {}
    for real, value in real_object.items():
        return_dict[f'{name}_{real}'] = value
    return return_dict


def flatten_attributes(self_obj: object, schema_dict: dict):
    return_dict = {}
    for k, v in schema_dict.items():
        if isinstance(
                getattr(self_obj, k),
                (RealFloatValue, RealDatetimeValue)):
            return_dict.update(**flatten_dict(k, v))
        elif isinstance(v, (str, int, float, bool, datetime)):
            return_dict[k] = v
    return return_dict


class HydraulicSample(BaseModel):
    datetime: RealDatetimeValue
    bottomtemperature: Optional[RealFloatValue]
    bottomflow: Optional[RealFloatValue]
    bottompressure: Optional[RealFloatValue]
    toptemperature: Optional[RealFloatValue]
    topflow: Optional[RealFloatValue]
    toppressure: Optional[RealFloatValue]
    fluiddensity: Optional[RealFloatValue]
    fluidviscosity: Optional[RealFloatValue]
    fluidph: Optional[RealFloatValue]
    fluidcomposition: Optional[str]

    class Config:
        getter_dict = ValueGetter

    def flat_dict(self, exclude_unset=False, exclude_defaults=False):
        schema_dict = self.dict(
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults)

        return_dict = flatten_attributes(self, schema_dict)

        return return_dict


class BoreholeSectionSchema(BaseModel):
    publicid: str
    starttime: datetime
    endtime: Optional[datetime]
    toplongitude: RealFloatValue
    toplatitude: RealFloatValue
    topaltitude: RealFloatValue
    bottomlongitude: RealFloatValue
    bottomlatitude: RealFloatValue
    bottomaltitude: RealFloatValue
    topmeasureddepth: Optional[RealFloatValue]
    bottommeasureddepth: Optional[RealFloatValue]
    holediameter: Optional[RealFloatValue]
    casingdiameter: Optional[RealFloatValue]
    topclosed: bool
    bottomclosed: bool
    sectiontype: Optional[str]
    casingtype: Optional[str]
    description: Optional[str]
    hydraulics: Optional[List[HydraulicSample]]

    class Config:
        getter_dict = ValueGetter

    def flat_dict(self, exclude_unset=False, exclude_defaults=False):
        schema_dict = self.dict(
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults)

        return_dict = flatten_attributes(self, schema_dict)

        if hasattr(self, 'hydraulics') and \
                isinstance(self.hydraulics, list):
            return_dict['hydraulics'] = \
                [h.flat_dict() for h in self.hydraulics]

        return return_dict


class BoreholeSchema(BaseModel):
    publicid: str
    longitude: RealFloatValue
    latitude: RealFloatValue
    altitude: RealFloatValue
    bedrockaltitude: Optional[RealFloatValue]
    measureddepth: Optional[RealFloatValue]
    description: Optional[str]
    name: Optional[str]
    sections: Optional[List[BoreholeSectionSchema]]

    class Config:
        getter_dict = ValueGetter

    def flat_dict(self, exclude_unset=False, exclude_defaults=False):
        schema_dict = self.dict(
            exclude={'sections': True},
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults)

        return_dict = flatten_attributes(self, schema_dict)

        if hasattr(self, 'sections') and \
                isinstance(self.sections, list):
            return_dict['sections'] = \
                [s.flat_dict() for s in self.sections]

        return return_dict
