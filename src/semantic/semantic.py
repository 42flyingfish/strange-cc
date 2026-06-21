import parser
from dataclasses import dataclass, replace

from utility import Identifier, make_temporary


@dataclass
class Id_Entry():
    name: Identifier
    has_linkage: bool = False


ScopeStack = list[dict[Identifier, Id_Entry]]


class IdentifierMap:
    def __init__(self) -> None:
        self.scope: ScopeStack = [dict()]

    def push(self) -> None:
        self.scope.append(dict())

    def pop(self) -> None:
        self.scope.pop()

    def check_in_block(self, val: Identifier) -> bool:
        return val in self.scope[-1].keys()

    def lookup(self, val: Identifier) -> Id_Entry | None:
        for x in reversed(self.scope):
            if val in x.keys():
                return x[val]
        return None

    def register(self, key: Identifier,
                 val: Identifier, linkage: bool) -> None:
        self.scope[-1][key] = Id_Entry(val, linkage)


def resolve_declaration(d: parser.Declaration,
                        v: IdentifierMap) -> parser.Declaration:
    match d:
        case parser.VarDecl(v_def):
            if v.check_in_block(v_def.name):
                raise RuntimeError(f'Duplicate var detected: {v_def.name}')
            unique_name = make_temporary(str(v_def.name))
            # For now assuming that Vars never have external linkage
            # This will be False in the future
            v.register(v_def.name, unique_name, False)
            if v_def.exp is None:
                return parser.VarDecl(
                    parser.VariableDefinition(unique_name, None))
            new_exp = resolve_exp(v_def.exp, v)
            return parser.VarDecl(
                parser.VariableDefinition(unique_name, new_exp))
        case parser.FunDecl():
            # Notice that we are calling the special local variant
            return resolve_func_local_decl(d, v)
        case _:
            raise RuntimeError()


def resolve_func_decl(d: parser.FunDecl,
                      v: IdentifierMap) -> parser.FunDecl:
    fun_def = d.function_definition
    if (lookup := v.lookup(fun_def.name)) is not None:
        if v.check_in_block(fun_def.name) and not lookup.has_linkage:
            raise RuntimeError('Duplicate function')
    v.register(fun_def.name, fun_def.name, True)
    v.push()
    new_params: list[Identifier] = list()
    for x in fun_def.params:
        new_params.append(resolve_param(x, v))
    new_body = None if fun_def.body is None else resolve_block(fun_def.body, v)
    v.pop()
    return parser.FunDecl(parser.Function(fun_def.name, new_params, new_body))


# This is for locally declared functions
def resolve_func_local_decl(d: parser.FunDecl,
                            v: IdentifierMap) -> parser.FunDecl:
    if d.function_definition.body is not None:
        raise RuntimeError('Nested function not allowed')
    return resolve_func_decl(d, v)


def resolve_param(i: Identifier,
                  v: IdentifierMap) -> Identifier:
    if v.check_in_block(i):
        raise RuntimeError(f'Duplicate identifier in func: {i}')
    unique_name = make_temporary(str(i))
    v.register(i, unique_name, False)
    return Identifier(unique_name)


def resolve_func(f: parser.Function,
                 v: IdentifierMap) -> parser.Function:
    """ Resolves the function contents but not the function as of yet"""
    if f.body is None:
        return f
    items = resolve_block(f.body, v)
    return replace(f, body=items)


def resolve_block(b: parser.Block,
                  v: IdentifierMap) -> parser.Block:
    items = [resolve_blockItem(x, v) for x in b.block_items]
    return replace(b, block_items=items)


def resolve_blockItem(b: parser.Block_Item,
                      v: IdentifierMap) -> parser.Block_Item:
    match b:
        case parser.S(statement):
            stmt = resolve_statement(statement, v)
            return parser.S(stmt)
        case parser.D(declaration):
            decl = resolve_declaration(declaration, v)
            return parser.D(decl)
        case _:
            raise RuntimeError('Impossible')


def resolve_for_init(i: parser.ForInit,
                     v: IdentifierMap) -> parser.ForInit:
    match i:
        case None:
            return None
        case parser.VarDecl():
            # ugly type coupling
            new_decl = resolve_declaration(i, v)
            if isinstance(new_decl, parser.VarDecl):
                return new_decl
            else:
                raise RuntimeError('Impossible')
        case _ if isinstance(i, parser.Expression):
            return resolve_exp(i, v)
        case _:
            raise RuntimeError('Impossible')


def resolve_statement(s: parser.Statement,
                      v: IdentifierMap) -> parser.Statement:
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
        case parser.Break() | parser.Continue():
            return s
        case parser.While(exp, body, label):
            new_exp = resolve_exp(exp, v)
            new_body = resolve_statement(body, v)
            return parser.While(new_exp, new_body, label)
        case parser.DoWhile(body, exp, label):
            new_body = resolve_statement(body, v)
            new_exp = resolve_exp(exp, v)
            return parser.DoWhile(new_body, new_exp, label)
        case parser.For(init, mid, post, body, label):
            v.push()
            new_init = resolve_for_init(init, v)
            new_mid = None if mid is None else resolve_exp(mid, v)
            new_post = None if post is None else resolve_exp(post, v)
            new_body = resolve_statement(body, v)
            v.pop()
            return parser.For(new_init, new_mid, new_post, new_body, label)
        case parser.Switch(exp, body, label):
            v.push()
            new_exp = resolve_exp(exp, v)
            new_body = resolve_statement(body, v)
            v.pop()
            return parser.Switch(new_exp, new_body, label)
        case parser.Case(cond, stm, label):
            new_cond = resolve_exp(cond, v)
            new_stm = resolve_statement(stm, v)
            return parser.Case(new_cond, new_stm, label)
        case parser.Default(stm, label):
            new_stm = resolve_statement(stm, v)
            return parser.Default(new_stm, label)
        case _:
            raise RuntimeError(f'Unknown statement passed {type(s)}')


def resolve_exp(e: parser.Expression,
                v: IdentifierMap) -> parser.Expression:
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
            return parser.Var(unique_id.name)
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
        case parser.FunctionCall(id, args):
            if (new_func_name := v.lookup(id)) is not None:
                new_args = [resolve_exp(x, v) for x in args]
                return replace(e, id=new_func_name.name, args=new_args)
            raise RuntimeError(f'id {id} is undeclared function')
        case _:
            raise RuntimeError(f'Impossible {e}')


def resolve_program(p: parser.Program) -> parser.Program:
    var_map = IdentifierMap()
    new_func_list: list[parser.FunDecl] = list()
    for x in p.function_definition:
        new_func = resolve_func_decl(x, var_map)
        new_func_list.append(new_func)
    return parser.Program(new_func_list)
