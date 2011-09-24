from l20n.format.lol import ast
import sys
from itertools import izip_longest as zip_longest
from itertools import chain

if sys.version >= "3":
    basestring = str

def is_string(string):
    return isinstance(string, basestring)


class Serializer():
    @classmethod
    def serialize(cls, lol):
        if hasattr(lol, '_struct') and lol._struct is True:
            string = ''.join(chain(*zip_longest(
                lol._template2,
                [cls.dump_entry(element) for element in lol.body],
                fillvalue='')))
        else:
            string = '\n'.join([cls.dump_entry(element, struct=False) for element in lol.body])
        return string

    @classmethod
    def dump_entry(cls, entry, struct=True):
        if isinstance(entry, ast.Entity):
            return cls.dump_entity(entry, struct=struct)
        elif isinstance(entry, ast.Comment):
            return cls.dump_comment(entry)
        elif isinstance(entry, ast.Macro):
            return cls.dump_macro(entry)
        elif isinstance(entry, ast.WS):
            return cls.dump_ws(entry)
        else:
            return unicode(entry)

    @classmethod
    def dump_ws(cls, ws):
        return ws.content

    @classmethod
    def dump_entity(cls, entity, struct=True):
        return str(entity)

    @classmethod
    def dump_kvp(cls, kvp, struct=True):
        if struct:
            return '%s%s%s:%s%s%s' % (
                kvp._template['ws_pre_key'],
                kvp.key.name,
                kvp._template['ws_post_key'],
                kvp._template['ws_pre_value'],
                cls.dump_value(kvp.value),
                kvp._template['ws_post_value'])
        else:
            return '%s: %s' % (kvp.key.name,
                               cls.dump_value(kvp.value))

    @classmethod
    def dump_value(cls, value, struct=True):
        if not value:
            return ''
        if isinstance(value, ast.String):
            return cls.dump_string(value)
        elif isinstance(value, ast.Array):
            if struct:
                elems = ['%s%s%s' % x for x in zip_longest(
                                                value._template['pre_ws'],
                                                map(cls.dump_value, value.content),
                                                value._template['post_ws'],
                                                fillvalue=''
                                                )]
                return '[%s]' % ','.join(elems)
            else:
                return '[%s]' % ', '.join(map(cls.dump_value, value.content))
        elif isinstance(value, ast.Hash):
            if struct:
                return '{%s%s}' % (value._template['pre_ws'],
                                     ','.join(map(cls.dump_kvp, value.content)))
            else:
                return '{%s}' % ', '.join(map(cls.dump_kvp, value.content))


    @classmethod
    def dump_index(cls, index, index_ws, struct=True):
        if struct:
            elems = ['%s%s' % x for x in zip_longest(
                ['']+index_ws[1:],
                [cls.dump_expression(i, struct=True) for i in index],
                fillvalue='')]
            return '[%s%s]' % (index_ws[0],
                               ','.join(elems))
        else:
            return '[%s]' % ', '.join([cls.dump_expression(i, struct=False) for i in index])

    @classmethod
    def dump_expression(cls, expression, struct=True):
        if isinstance(expression, ast.ConditionalExpression):
            return cls.dump_conditional_expression(expression, struct=struct)
        elif isinstance(expression, ast.LogicalExpression):
            return cls.dump_logical_expression(expression)
        elif isinstance(expression, ast.BinaryExpression):
            return cls.dump_binary_expression(expression)
        elif isinstance(expression, ast.UnaryExpression):
            return cls.dump_unary_expression(expression)
        elif isinstance(expression, ast.ParenthesisExpression):
            return cls.dump_parenthesis_expression(expression)
        elif isinstance(expression, ast.PropertyExpression):
            return cls.dump_propertyexpression(expression)
        elif isinstance(expression, ast.Identifier):
            return cls.dump_identifier(expression)
        elif isinstance(expression, ast.Literal):
            return cls.dump_literal(expression)
        elif isinstance(expression, ast.String):
            return cls.dump_string(expression, struct=struct)
        elif isinstance(expression, int):
            return str(expression)

    @classmethod
    def dump_logical_expression(cls, e):
        return '%s%s%s' % (cls.dump_expression(e.left),
                           cls.dump_operator(e.operator),
                           cls.dump_expression(e.right))

        s = cls.dump_expression(e[0])
        for i in range(0,1+int((len(e)-3)/2)):
            s = '%s%s%s' % (s, e[(i*2)+1], cls.dump_expression(e[2+(i*2)]))
        return s

    dump_binary_expression = dump_logical_expression 
    dump_equality_expression = dump_logical_expression
    dump_relational_expression = dump_logical_expression
    dump_additive_expression = dump_logical_expression
    dump_multiplicative_expression = dump_logical_expression
    dump_unary_expression = dump_logical_expression

    @classmethod
    def dump_parenthesis_expression(cls, e):
        return '(%s%s%s)' % (e._template['ws_pre'],
                             cls.dump_expression(e.expression),
                             e._template['ws_post'])

    @classmethod
    def dump_identifier(cls, i):
        return i.name

    @classmethod
    def dump_propertyexpression(cls, e):
        if e.computed:
            return '%s[%s]' % (cls.dump_expression(e.expression),
                               cls.dump_expression(e.property))
        else:
            return '%s.%s' % (e.expression, e.property)


    @classmethod
    def dump_literal(cls, e):
        return "%s%s" % (e.value,
                         e._template['ws_post'])

    @classmethod
    def dump_string(cls, e, struct=True):
        if struct:
            return '%s%s%s' % (e._template['str_end'],
                               e.content,
                               e._template['str_end'])
        else:
            return '"%s"' % e.content.replace('"', '\\"')

    @classmethod
    def dump_operator(cls, op):
        return op.token