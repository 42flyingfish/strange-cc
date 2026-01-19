import parser
from dataclasses import replace

from utility import Identifier, make_temporary

ScopeStack = list[dict[Identifier, Identifier]]


class VariableMap:
    def __init__(self) -> None:
        self.scope: ScopeStack = [dict()]

    def push(self) -> None:
        self.scope.append(dict())

    def pop(self) -> None:
        self.scope.pop()

    def check_in_scope(self, val: Identifier) -> bool:
        return val in self.scope[-1].keys()

    def lookup(self, val: Identifier) -> Identifier | None:
        for x in reversed(self.scope):
            if val in x.keys():
                return x[val]
        return None

    def register(self, key: Identifier, val: Identifier) -> None:
        self.scope[-1][key] = val


def resolve_declaration(d: parser.Declaration,
                        v: VariableMap) -> parser.Declaration:
    if v.check_in_scope(d.name):
        raise RuntimeError(f'Duplicate variable detected: {d.name}')
    unique_name = make_temporary(str(d.name))
    v.register(d.name, unique_name)
    if d.exp is None:
        return parser.DeclareNode(unique_name, None)
    new_exp = resolve_exp(d.exp, v)
    return parser.DeclareNode(unique_name, new_exp)


def resolve_func(f: parser.Function,
                 v: VariableMap) -> parser.Function:
    """ Resolves the function contents but not the function as of yet"""
    items = resolve_block(f.body, v)
    return replace(f, body=items)


def resolve_block(b: parser.Block,
                  v: VariableMap) -> parser.Block:
    items = [resolve_blockItem(x, v) for x in b.block_items]
    return replace(b, block_items=items)


def resolve_blockItem(b: parser.Block_Item,
                      v: VariableMap) -> parser.Block_Item:
    match b:
        case parser.S(statement):
            stmt = resolve_statement(statement, v)
            return parser.S(stmt)
        case parser.D(declaration):
            decl = resolve_declaration(declaration, v)
            return parser.D(decl)
        case _:
            raise RuntimeError('Impossible')


def resolve_statement(s: parser.Statement,
                      v: VariableMap) -> parser.Statement:
    match s:
        case parser.Null():
            return s
        case parser.Return(exp):
            e = resolve_exp(exp, v)
            return parser.Return(e)
        case parser.ExpNode(exp):
            e = resolve_exp(exp, v)
            return parser.ExpNode(e)
        case parser.If(cond, then):
            new_cond = resolve_exp(cond, v)
            new_then = resolve_statement(then, v)
            return parser.If(new_cond, new_then)
        case parser.IfElse(cond, then, otherwise):
            new_cond = resolve_exp(cond, v)
            new_then = resolve_statement(then, v)
            new_otherwise = resolve_statement(otherwise, v)
            return parser.IfElse(new_cond, new_then, new_otherwise)
        case parser.Label(id, stm):
            new_stm = resolve_statement(stm, v)
            return parser.Label(id, new_stm)
        case parser.Goto():
            return s
        case parser.Compound(block):
            v.push()
            new_block = resolve_block(block, v)
            v.pop()
            return replace(s, block=new_block)
        case _:
            raise RuntimeError('Impossible')


def resolve_exp(e: parser.Expression,
                v: VariableMap) -> parser.Expression:
    match e:
        case parser.Constant():
            return e
        case parser.Assignment(left, right):
            if not isinstance(left, parser.Var):
                raise RuntimeError('left is an invalid lvalue')
            new_left = resolve_exp(left, v)
            new_right = resolve_exp(right, v)
            return parser.Assignment(new_left, new_right)
        case parser.CompoundAssign(bop, left, right):
            if not isinstance(left, parser.Var):
                raise RuntimeError('left is an invalid lvalue')
            new_left = resolve_exp(left, v)
            new_right = resolve_exp(right, v)
            return parser.CompoundAssign(bop, new_left, new_right)
        case parser.Var(id):
            unique_id = v.lookup(id)
            if unique_id is None:
                raise RuntimeError(f'Id {id} is not in scope')
            return parser.Var(unique_id)
        case parser.Unary(up, exp):
            PREFIX = {parser.Unary_Operator.INCREMENT,
                      parser.Unary_Operator.DECREMENT}
            if up in PREFIX and not isinstance(exp, parser.Var):
                raise RuntimeError('exp is an invalid lvalue')
            new_exp = resolve_exp(exp, v)
            return parser.Unary(up, new_exp)
        case parser.Binary(bop, left, right):
            new_left = resolve_exp(left, v)
            new_right = resolve_exp(right, v)
            return parser.Binary(bop, new_left, new_right)
        case parser.Postfix(b, exp):
            if not isinstance(exp, parser.Var):
                raise RuntimeError('exp is an invalid lvalue')
            new_exp = resolve_exp(exp, v)
            return parser.Postfix(b, new_exp)
        case parser.Conditional(cond, t, f):
            new_cond = resolve_exp(cond, v)
            new_t = resolve_exp(t, v)
            new_f = resolve_exp(f, v)
            return parser.Conditional(new_cond, new_t, new_f)
        case _:
            raise RuntimeError(f'Impossible {e}')


def resolve_program(p: parser.Program) -> parser.Program:
    var_map = VariableMap()
    func = resolve_func(p.function_definition, var_map)
    return parser.Program(func)
