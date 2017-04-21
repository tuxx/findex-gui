import operator

import sqlalchemy
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import DeclarativeMeta
#from sqlalchemy.sql.annotation import AnnotatedColumn
from sqlalchemy.sql.elements import BinaryExpression, BindParameter, BooleanClauseList, TextClause
from sqlalchemy.sql.expression import FunctionElement, ColumnClause
from sqlalchemy.sql.operators import match_op, like_op
from sqlalchemy.sql.sqltypes import String
from sqlalchemy import Column as _Column


class _ZdbDomain(sqlalchemy.types.UserDefinedType):
    """
    phrases/fulltext/fulltext_with_shingles are postgres DOMAIN's
    that sits on top of the standard text datatype. As far as
    Postgres is concerned, it is functionally no different than
    the text datatype, however they have special meaning to
    ZomboDB when indexing and searching. In brief, they indicate
    that such fields should be analyzed.
    """
    def __init__(self, *args):
        self._args = args

    def convert_bind_param(self, value, engine):
        return value

    def convert_result_value(self, value, engine):
        return value

    @property
    def python_type(self):
        return str


class Phrase( _ZdbDomain):
    def __init__(self, *args):
        super(Phrase, self).__init__(*args)

    def get_col_spec(self):
        return "phrase"

    def is_mutable(self):
        return True


class Fulltext(_ZdbDomain):
    def __init__(self, *args):
        super(Fulltext, self).__init__(*args)

    def get_col_spec(self):
        return "fulltext"

    def is_mutable(self):
        return True


class FulltextWithShingles(_ZdbDomain):
    def __init__(self, *args):
        super(FulltextWithShingles, self).__init__(*args)

    def get_col_spec(self):
        return "fulltext_with_shingles"

    def is_mutable(self):
        return True


class Column(_Column):
    """
    Represents a column in a database table. Inherits
    from `sqlalchemy.Column`. Adds the kwargs keyword
    `zombodb` for marking a column to be of one of the
    special zombodb types.
    """
    def __init__(self, *args, **kwargs):
        if kwargs.get("zombodb"):
            if kwargs.get("info"):
                kwargs["info"]["zombodb"] = True
            else:
                kwargs["info"] = {"zombodb": True}
            kwargs.pop("zombodb")

        super(Column, self).__init__(*args, **kwargs)

# COMPARE_OPERATORS = {
#     operator.gt: ' > ',
#     operator.lt: ' < ',
#     operator.ge: ' >= ',
#     operator.le: ' <= ',
#     operator.ne: ' != ',
#     match_op: ':@',
#     like_op: ':~',
#     operator.eq: ':',
# }
#
#
# class ZdbPhrase(object):
#     def __init__(self, phrase):
#         self.phrase = phrase.strip('"')
#
#     def __str__(self):
#         return '"%s"' % self.phrase
#
#
# def compile_binary_clause(c, compiler, tables, format_args):
#     left = c.left
#     right = c.right
#
#     _oper = COMPARE_OPERATORS.get(c.operator, None)
#     if _oper is None:
#         raise ValueError('Unsupported binary operator %s' % c.operator)
#
#     if not isinstance(left, AnnotatedColumn):
#         raise ValueError('Incorrect field')
#
#     tables.add(left.table.name)
#     return '%s%s%s' % (left.name, _oper, compile_clause(right, compiler, tables, format_args))
#
#
# def compile_boolean_clause_list(c, compiler, tables, format_args):
#     query = []
#
#     for _c in c.clauses:
#         query.append(compile_clause(_c, compiler, tables, format_args))
#
#     if c.operator == operator.or_:
#         _oper = ' or '
#     elif c.operator == operator.and_:
#         _oper = ' and '
#     else:
#         raise ValueError('Unsupported boolean clause')
#
#     return '(%s)' % _oper.join(query)
#
#
# def compile_column_clause(c, compiler, tables, format_args):
#     format_args.append('replace(%s, \'"\', \'\')' % compiler.process(c))
#     return '"%%s"'
#
#
# def compile_clause(c, compiler, tables, format_args):
#     if isinstance(c, BindParameter) and isinstance(c.value, str):
#         return c.value
#     elif isinstance(c, TextClause):
#         return c.text
#     elif isinstance(c, BinaryExpression):
#         raise Exception("BinaryExpression not supported because sqla is missing AnnotatedColumn (?)")
#         #return compile_binary_clause(c, compiler, tables, format_args)
#     elif isinstance(c, BooleanClauseList):
#         return compile_boolean_clause_list(c, compiler, tables, format_args)
#     elif isinstance(c, Column):
#         return compile_column_clause(c, compiler, tables, format_args)
#
#     raise ValueError('Unsupported clause')
#
#
# class zdb_query(FunctionElement):
#     name = 'zdb_query'
#
#
# @compiles(zdb_query)
# def compile_zdb_query(element, compiler, **kw):
#     query = []
#     tables = set()
#     format_args = []
#
#     for i, c in enumerate(element.clauses):
#         add_to_query = True
#
#         if isinstance(c, BinaryExpression):
#             tables.add(c.left.table.name)
#         elif isinstance(c, BindParameter):
#             if isinstance(c.value, str):
#                 pass
#             elif isinstance(c.value, DeclarativeMeta):
#                 if i > 0:
#                     raise ValueError('Table can be specified only as first param')
#                 tables.add(c.value.__tablename__)
#                 add_to_query = False
#         elif isinstance(c, BooleanClauseList):
#             pass
#         elif isinstance(c, Column):
#             pass
#         else:
#             raise ValueError('Unsupported filter')
#
#         if add_to_query:
#             query.append(compile_clause(c, compiler, tables, format_args))
#
#     if not tables:
#         raise ValueError('No filters passed')
#     elif len(tables) > 1:
#         raise ValueError('Different tables passed')
#     else:
#         table = tables.pop()
#
#     if format_args:
#         return 'zdb(\'%s\', ctid) ==> format(\'%s\', %s)' % (table, ' and '.join(query), ', '.join(format_args))
#     return 'zdb(\'%s\', ctid) ==> \'%s\'' % (table, ' and '.join(query))
#
#
# class zdb_score(FunctionElement):
#     name = 'zdb_score'
#
#
# @compiles(zdb_score)
# def compile_zdb_score(element, compiler, **kw):
#     clauses = list(element.clauses)
#     if len(clauses) != 1:
#         raise ValueError('Incorrect params')
#
#     c = clauses[0]
#     if isinstance(c, BindParameter) and isinstance(c.value, DeclarativeMeta):
#         return 'zdb_score(\'%s\', %s.ctid)' % (c.value.__tablename__, c.value.__tablename__)
#
#     raise ValueError('Incorrect param')