"""
SQLAlchemy object actions including filter, order by, paginate,
limit.
"""
from sqlalchemy.orm.exc import NoResultFound

class DynamicQuery(object):
    """

    Dynamic filtering and of query.

    Example:
     dyn_query = DynamicQuery(query, orm.BoreholeSection)
     dyn_query.filter_query([('m_starttime', 'eq', datetime(...))])

    """

    def __init__(self, query):
        self.query = query
        self.page = 1

    def return_all(self):
        try: 
            return self.query.all()
        except NoResultFound:
            return None


    def paginate_query(self, limit, page=None, error_flag=False):
        """Paginate used to return a subset of results, starting from
        offset*limit to offset*limit + limit.
        To be used instead of self.return_all()

        :returns type: Pagination object. Use .items to get similar
            response to .all()
        """
        if not page:
            page = self.page
        return self.query.paginate(page, limit, error_flag)

    
    def limit_by_query(self, limit):
        """Append a limit_by clause to the query.
        """
        self.query = self.query.limit_by(limit)

    def order_by_query(self, orm_class, key, ascending=True):
        """Append an order_by clause to the query.

        :orm_class: str name of ORM class included in query.
        :param key: str name of column belonging to orm_class.

        """
        try:
            column = getattr(orm_class, key)
            if not ascending:
                column = column.desc()
        except AttributeError:
            raise Exception('Key: {} is not an attribute of class: {}'.\
                format(key, orm_class))
        try:
            self.query = self.query.order_by(column)
        except KeyError:
            raise Exception('Invalid column: %s' % key)


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

    def filter_query(self, orm_class, query_params, filter_condition,
                     key_suffix="_value"):
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
                key_basename, op, param_name = f
            except ValueError:
                raise Exception('Invalid filter input: %s' % f)
            if key_suffix:
                key = "{}{}".format(key_basename, key_suffix)
            else:
                key = key_basename
            #put in try statement?
            param_value = query_params.get(param_name)
            if not param_value:
                continue
            # todo: check column type against value type
            # and if they don't match then error?
            try:
                column = getattr(orm_class, key)
            except AttributeError:
                raise Exception('Invalid filter column: %s' % key)
            
            if op == 'in':
                if isinstance(value, list):
                    filt = column.in_(param_value)
                else:
                    filt = column.in_(param_value.split(','))
            else:
                attr = self.operator_attr(column, op)
                filt = getattr(column, attr)(param_value)
            self.query = self.query.filter(filt)


