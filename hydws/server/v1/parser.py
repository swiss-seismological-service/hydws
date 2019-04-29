"""
HYDWS parser related facilities.
"""
import datetime

from marshmallow import (Schema, fields, pre_load, validates_schema,
                         ValidationError)

from hydws.server.misc import from_fdsnws_datetime, fdsnws_isoformat


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


class BoreholeHydraulicDataListResourceSchema(Schema):

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

    # validate_temporal_constraints ()

    class Meta:
        strict = True
        ordered = True
