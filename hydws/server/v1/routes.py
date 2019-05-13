"""
HYDWS resources.
"""

import logging

from flask_restful import Api, Resource
from sqlalchemy.orm.exc import NoResultFound
from webargs.flaskparser import use_kwargs

from hydws import __version__
from hydws.db import orm
from hydws.server import db, settings
from hydws.server.errors import FDSNHTTPError
from hydws.server.misc import (with_fdsnws_exception_handling, decode_publicid,
                               make_response)
from hydws.server.v1 import blueprint
from hydws.server.v1.ostream.schema import BoreholeSchema
from hydws.server.v1.parser import BoreholeHydraulicDataListResourceSchema


api_v1 = Api(blueprint)


class ResourceBase(Resource):

    LOGGER = 'hydws.server.v1.resource'

    def __init__(self, logger=None):
        super().__init__()
        self.logger = logging.getLogger(logger if logger else self.LOGGER)

    def get(self):
        """
        Template method to be implemented by HYDWS resources in order to serve
        HTTP GET requests.
        """
        raise NotImplementedError

    def _handle_nodata(self, query_params):
        """
        Handle an empty query result

        :param dict query_params: Dict of query parameters

        :raises: :py:class:`FDSNHTTPError`
        """
        raise FDSNHTTPError.create(
            int(query_params.get(
                'nodata',
                settings.FDSN_DEFAULT_NO_CONTENT_ERROR_CODE)))

    def _process_request(self, borehole_id=None, section_id=None,
                         **query_params):
        """
        Template method intended to process a request

        :param borehole_id: Borehole publicid
        :type borehole_id: str or None
        :param section_id: Borehole section publicid
        :type section_id: str or None
        """
        raise NotImplementedError


class BoreholeListResource(ResourceBase):

    def get(self):
        pass


class BoreholeResource(ResourceBase):

    def get(self, borehole_id):
        pass


class DynamicFilter(ResourceBase):
    """

    Dynamic filtering of query.

    Example:
     dyn_query = DynamicFilter(query, orm.BoreholeSection)
     dyn_query.filter_query([('m_starttime', 'eq', datetime(...))])

    """

    def __init__(self, query, orm_class):
        self.query = query
        self.orm_class = orm_class

    def operator_attr(self, column, op):
        """
        Returns method associated with an comparison operator.
        If op, op_ or __op__ does not exist, Exception returned.

        :returns type: str.

        """
        try:
            return list(filter(
                lambda e: hasattr(column, e % op),
                    ['%s', '%s_', '__%s__']))[0] % op
        except IndexError:
            raise Exception('Invalid filter operator: %s' % op)

    def filter_query(self, filter_condition):
        """
        Update self.query based on filter_condition.
        :param filter_condition: list, ie: [(key,operator,value)]
            operator examples:
                eq for ==
                lt for <
                ge for >=
                in for in_
                like for like

            value can be list or a string.
            key must belong in self.orm_class.

        """

        for f in filter_condition:
            try:
                key, op, value = f
            except ValueError:
                raise Exception('Invalid filter input: %s' % f)
            column = getattr(self.orm_class, key)
            if not column:
                raise Exception('Invalid filter column: %s' % key)
            if op == 'in':
                if isinstance(value, list):
                    filt = column.in_(value)
                else:
                    filt = column.in_(value.split(','))
            else:
                attr = self.operator_attr(self, column, op)
                if value == 'null':
                    value = None
                print(column, attr, value)
                filt = getattr(column, attr)(value)
            self.query = self.query.filter(filt)

    def return_query(self):
        return self.query


class BoreholeHydraulicDataListResource(ResourceBase):

    LOGGER = 'hydws.server.v1.boreholehydraulicdatalistresource'

    @with_fdsnws_exception_handling(__version__)
    @use_kwargs(BoreholeHydraulicDataListResourceSchema(),
                locations=("query", ))
    def get(self, borehole_id, **query_params):
        print('get')
        borehole_id = decode_publicid(borehole_id)

        self.logger.debug(
            f"Received request: borehole_id={borehole_id}, "
            f"query_params={query_params}")

        resp = self._process_request(db.session, borehole_id=borehole_id,
                                     **query_params)

        if not resp:
            self._handle_nodata(query_params)

        # TODO(damb): Serialize according to query_param format=JSON|XML
        # format response
        resp = BoreholeSchema().dumps(resp)

        return make_response(resp, settings.MIMETYPE_JSON)
    

    def _process_request(self, session, borehole_id=None, section_id=None,
                         **query_params):

        print('_process_request')
        if not borehole_id:
            raise ValueError(f"Invalid borehole identifier: {borehole_id!r}")

        query = session.query(orm.Borehole).\
            join(orm.BoreholeSection).\
            join(orm.HydraulicSample).\
            filter(orm.Borehole.m_publicid==borehole_id)

        dynamic_query = DynamicFilter(query, orm.BoreholeSection)

        # XXX(damb): Emulate QuakeML type Epoch (though on DB level it is
        # defined as QuakeML type OpenEpoch
        starttime = query_params.get('starttime')
        if starttime:
            query = query.\
                filter((orm.BoreholeSection.m_starttime >= starttime) &  # noqa
                       (orm.BoreholeSection.m_starttime != None)).\
                filter(orm.HydraulicSample.m_datetime_value >= starttime)

        endtime = query_params.get('endtime')
        if endtime:
            query = query.\
                filter((orm.BoreholeSection.m_endtime <= endtime) |  # noqa
                       (orm.BoreholeSection.m_endtime == None)).\
                filter(orm.HydraulicSample.m_datetime_value <= endtime)

        # XXX(lsarson): Filter None first or query will fail due to type differences.
        dynamic_query.filter_query([('m_starttime', 'ne', None),
            ('m_starttime', 'ge', query_params.get('starttime'))])

        # TODO(lsarson): Think about if endtime not defined.
        dynamic_query.filter_query(['m_endtime', 'le', query_params.get('endtime')])
        # TODO(lsarson): Add additional filter criteria. Just test out this for now.

        try:
            return query.\
                order_by(orm.BoreholeSection.m_starttime).\
                order_by(orm.HydraulicSample.m_datetime_value).\
                one()
        except NoResultFound:
            return None


class SectionHydraulicDataListResource(ResourceBase):

    def get(self, borehole_id, section_id):
        pass


# TODO(damb):
# Add resources to API

api_v1.add_resource(BoreholeHydraulicDataListResource,
                    '{}/<borehole_id>'.format(settings.HYDWS_PATH_BOREHOLES))
