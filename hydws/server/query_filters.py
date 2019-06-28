"""
.. module:: query_filters
    :synopsis: Contains class to interact with SQLAlchemy Query
        object including filter and paginate.

.. moduleauthor:: Laura Sarson <laura.sarson@sed.ethz.ch>

"""
import datetime
from sqlalchemy import or_
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
FILTER_HYDRAULICS = [
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

FILTER_SECTIONS_EPOCH = [
    ('starttime', 'le', 'endtime'),
    ('endtime', 'ge', 'starttime')]


FILTER_SECTIONS = [
    [('toplatitude_value', 'ge', 'minlatitude'),
     ('bottomlatitude_value', 'ge', 'minlatitude')],
    [('toplatitude_value', 'le', 'maxlatitude'),
     ('bottomlatitude_value', 'le', 'maxlatitude')],
    [('toplongitude_value', 'ge', 'minlongitude'),
     ('bottomlongitude_value', 'ge', 'minlongitude')],
    [('toplongitude_value', 'le', 'maxlongitude'),
     ('longitude_value', 'le', 'maxlongitude')],
    ('casingdiameter_value', 'ge', 'mincasingdiameter'),
    ('casingdiameter_value', 'le', 'maxcasingdiameter'),
    ('holediameter_value', 'ge', 'minholediameter'),
    ('holediameter_value', 'le', 'maxholediameter'),
    ('topdepth_value', 'ge', 'mintopdepth'),
    ('topdepth_value', 'le', 'maxtopdepth'),
    ('bottomdepth_value', 'ge', 'minbottomdepth'),
    ('bottomdepth_value', 'le', 'maxbottomdepth'),
    ('topclosed_value', 'eq', 'topclosed'),
    ('bottomclosed_value', 'eq', 'bottomclosed'),
    ('casingtype_value', 'eq', 'casingtype'),
    ('sectiontype_value', 'eq', 'sectiontype')]


FILTER_BOREHOLES = [
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

    def return_all(self):
        """Returns all results from query.

        :rtype: list
        """
        try:
            return self.query.all()
        except NoResultFound as err:
            return None

    def return_one(self):
        """
        Returns one result from query.

        :rtype: dict
        """
        # TODO (sarsonl) MultipleResultsFound from sqlalchemy.orm.exc
        return self.query.one_or_none()

    def format_results(self, order_column=None, limit=None, offset=None):
        """
        Return a subset of results of size limit
        and with an offset if required.

        :param limit: Limit to number of results returned.
        :type query: sqlalchemy.orm.query.Query()
        """
        if order_column:
            self.query = self.query.order_by(order_column)
        if limit:
            self.query = self.query.limit(limit)
        if offset:
            self.query = self.query.offset(offset)

    def operator_attr(self, obj, op):
        """
        Returns method associated with an comparison operator
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
            # define a specific error here
            raise Exception(f"Invalid operator: {op}")

    def filter_section_epoch(self, column, attr, param_value):
        """
        Special case for filtering to deal with open epochs.
        This requires BoreholeSection starttime and endtime values to
        include None values if no value has been set for them.

        :param column: Attribute name of ORM table to filter on.
        :type column: str
        :params attr: Attribute name of operator to use in evaluation.
        :type filter_level: str
        :params param_value: Value of input query parameter to filter
            column on.
        :type filter_level: matches type of values stored in column.

        :return: Method to evaluate ORM column
            e.g. column_value >= 22
        :type: Column evaluation method.
        """

        eq_attr = self.operator_attr(column, 'eq')
        filt =  or_((getattr(column, attr)(param_value)),
                    (getattr(column, eq_attr)(None)))
        return filt

    def filter_level(self, query_params, filter_level):
        """
        Update self.query with chained filters based
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
            filter_condition = {"hydraulic": FILTER_HYDRAULICS}
        elif filter_level == "borehole":
            orm_class = Borehole
            filter_condition = {"borehole": FILTER_BOREHOLES}
        elif filter_level == "section":
            orm_class = BoreholeSection

            filter_condition = {"section_epoch": FILTER_SECTIONS_EPOCH,
                                "section": FILTER_SECTIONS}
        else:
            raise Exception(f'filter level not handled: {filter_level}')

        for filter_name, filter_tuples in filter_condition.items():
            for filter_clause in filter_tuples:

                if isinstance(filter_clause, list):
                    filt_list = []
                    for clause in filter_clause:
                        filt = self.get_filter(clause, filter_name,
                                               query_params, orm_class)
                        if filt is None:
                            continue

                        filt_list.append((filt))
                    self.query = self.query.filter(or_(*filt_list))

                else:
                    filt = self.get_filter(
                        filter_clause, filter_name, query_params,orm_class)
                    if filt is None:
                        continue

                    self.query = self.query.filter(filt)

    def get_filter(self, filter_clause, filter_name, query_params, orm_class):
        """Return evaluation clause for filtering query if a query param
        value exists to to the evaluation on.

        :param filter_clause: e.g. ('datetime_value', 'ge', 'starttime')
        :type filter_clause: tuple
        :params filter_name: name given to collection of filter clauses.
        :type filter_level: str
        :param query_params: values to filter query results
        :type query_params: dict
        :param orm_class: Name of ORM class that the column value belongs to.
        :type query_params: str

        :return: Method to evaluate ORM column
            e.g. getattr(col, operator)(param value)
        :type: Column evaluation method or None if no param value exists. 

        """
        key, op, param_name, param_value = self.get_query_param(filter_clause, query_params)
        if param_value:
            return self.filter_query(query_params, filter_name, key, op, param_name, param_value, orm_class)
        else:
            return None

    def get_query_param(self, filter_clause, query_params):

        try:
            key, op, param_name = filter_clause
        except ValueError as err:
            raise Exception(f"Invalid filter input")

        param_value = query_params.get(param_name)
        
        return key, op, param_name, param_value
        
    def filter_query(self, query_params, filter_name, key, op, param_name, param_value, orm_class):

        try:
            column = getattr(orm_class, key)
        except AttributeError:
           raise Exception(f"Invalid filter column: {key}")

	    # (sarsonl) Currently 'in' is unused and untested.
	    # Still requires handling for the backref quantities
        if op == "in":
            if isinstance(param_value, list):
                filt = column.in_(param_value)
            else:
                filt = column.in_(param_value.split(","))
        else:
            attr = self.operator_attr(column, op)
            if filter_name == "section_epoch":
                filt = self.filter_section_epoch(column, attr, param_value)
            else:
                filt = getattr(column, attr)(param_value)

        return filt
