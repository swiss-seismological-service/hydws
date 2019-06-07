"""
.. module:: query_filters
    :synopsis: Contains class to interact with SQLAlchemy Query
        object including filter and paginate.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""
from sqlalchemy.orm.exc import NoResultFound

from hydws.db.orm import Borehole, BoreholeSection, HydraulicSample


# Mapping of orm table columns to comparison operator and input values.
# [(orm attr, operator, input comparison value)]
#            operator examples:
#                eq for ==
#                lt for <
#                ge for >=
#                in for in_
#                like for like
#
#            input comparison value can be list or a string.
#            operator must belong in orm attr as op, op_, __op__
filter_hydraulics = [
    ('datetime_value', 'ge', 'starttime'),
    ('datetime_value', 'le', 'endtime'),
    ('toptemperature_value', 'ge', 'mintoptemperature'),
    ('toptemperature_value', 'le', 'maxtoptemperature'),
    ('bottomtemperature_value', 'ge', 'minbottomtemperature'),
    ('bottomtemperature_value', 'le', 'maxbottomtemperature'),
    ('toppressure_value', 'ge', 'mintoppressure'),
    ('toppressure_value', 'le', 'maxtoppressure'),
    ('bottompressure_value', 'ge', 'minbottompressure'),
    ('bottompressure_value', 'le', 'maxbottompressure'),
    ('topflow_value', 'ge', 'mintopflow'),
    ('topflow_value', 'le', 'maxtopflow'),
    ('bottomflow_value', 'ge', 'minbottomflow'),
    ('bottomflow_value', 'le', 'maxbottomflow'),
    ('fluiddensity_value', 'ge', 'minfluiddensity'),
    ('fluiddensity_value', 'le', 'maxfluiddensity'),
    ('fluidviscosity_value', 'ge', 'minfluidviscosity'),
    ('fluidviscosity_value', 'le', 'maxfluidviscosity'),
    ('fluidph_value', 'ge', 'minfluidph'),
    ('fluidph_value', 'le', 'maxfluidph')]

filter_boreholes = [
    ('latitude_value', 'ge', 'minlatitude'),
    ('latitude_value', 'le', 'maxlatitude'),
    ('longitude_value', 'ge', 'minlongitude'),
    ('longitude_value', 'le', 'maxlongitude')]


class DynamicQuery(object):
    """

    Dynamic filtering and of query.

    Example:
     dq = DynamicQuery(session.query)
     dq.filter_query([('m_starttime', 'eq', datetime(...))], 'borehole')
     results = dq.return_all()

    :param query: sqlalchemy query to manipulate.
    :type query: sqlalchemy.orm.query.Query()

    """

    def __init__(self, query):
        self.query = query
        self.page = 1

    def return_all(self):
        """Returns all results from query.

        :rtype: list
        """
        try: 
            return self.query.all()
        except NoResultFound as err:
            return None

    def paginate_query(self, limit, page=None, error_flag=False):
        """Paginate used to return a subset of results, starting from
        offset*limit to offset*limit + limit.
        To be used instead of self.return_all()

        :returns:  Pagination of query. Use .items to get similar
            response to .return_all()
        :rtype: Pagination object

        """
        if not page:
            page = self.page
        return self.query.paginate(page, limit, error_flag)

    def operator_attr(self, obj, op):
        """Returns method associated with an comparison operator
        If one of op,  op_, __op__ do not exist, Exception raised

        :param obj: Object used to find existing operator methods
        :type obj: Class or class instance.
        :param str op: Operator to find method for, e.g. 'eq'

        :return: Method that exists ob obj associted with op
        :rtype: str
        :raises: Exception

        """
        obj_methods = [op, f"{op}_", f"__{op}__"]
        existing_methods = [m for m in obj_methods
                                if hasattr(obj, m)]
        if existing_methods:
            return existing_methods[0]
        else:
            raise Exception(f"Invalid operator: {op}")

    def filter_query(self, query_params, filter_level):
        """Update self.query with chained filters based
        on query_params

        :param query_params: values to filter query results
        :type query_params: dict
        :params filter_level: orm table level to use to filter query,
             one of ("hydraulic", "borehole")
        :type filter_level: str
        :raises: Exception

        """
        if filter_level == "hydraulic":
            orm_class = HydraulicSample
            filter_condition = filter_hydraulics
        elif filter_level == "borehole":
            orm_class = Borehole
            filter_condition = filter_boreholes
        else:
            raise Exception(f'filter level not handled: {filter_level}')

        for filter_tuple in filter_condition:
            try:
                key, op, param_name = filter_tuple
            except ValueError:
                raise Exception(f"Invalid filter input: {filter_tuple}")

            param_value = query_params.get(param_name)

            if not param_value:
                continue

            try:
                column = getattr(orm_class, key)
            except AttributeError:
                raise Exception(f"Invalid filter column: {key}")

            if op == "in":
                if isinstance(value, list):
                    filt = column.in_(param_value)
                else:
                    filt = column.in_(param_value.split(","))
            else:
                attr = self.operator_attr(column, op)
                filt = getattr(column, attr)(param_value)

            self.query = self.query.filter(filt)
