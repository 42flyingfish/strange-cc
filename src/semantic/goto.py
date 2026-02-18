import parser
from dataclasses import replace
from typing import cast

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

    def print_topmost(self) -> None:
        print('This is a print for scope')
        for key, value in self.scope[-1].items():
            print(f'key {key} value {value}')


def resolve_labels_program(n: parser.Program,
                           v: VariableMap) -> parser.Program:
    func_node = resolve_labels_func(n.function_definition, v)
    return replace(n, function_definition=func_node)


def resolve_labels_func(n: parser.Function,
                        v: VariableMap) -> parser.Function:
    new_body = resolve_labels_block(n.body, v)
    return replace(n, body=new_body)


def resolve_labels_block(n: parser.Block,
                         v: VariableMap) -> parser.Block:
    items = [resolve_labels_block_items(x, v) for x in n.block_items]
    return replace(n, block_items=items)


def resolve_labels_block_items(n: parser.Block_Item,
                               v: VariableMap) -> parser.Block_Item:
    match n:
        case parser.S(statement):
            stm = resolve_labels_stm(statement, v)
            return replace(n, statement=stm)
        case parser.D(declare):
            decl = resolve_labels_decl(declare, v)
            return replace(n, declaration=decl)
        case _:
            raise RuntimeError(f'impossible {n}')


def resolve_labels_for_init(i: parser.ForInit,
                            v: VariableMap) -> parser.ForInit:
    match i:
        case None:
            return None
        case parser.DeclareNode():
            return resolve_labels_decl(i, v)
        case _ if isinstance(i, parser.Expression):
            return resolve_labels_exp(i, v)
        case _:
            raise RuntimeError('Impossible')


def resolve_labels_stm(n: parser.Statement,
                       v: VariableMap) -> parser.Statement:
    match n:
        case parser.Null():
            return n
        case parser.Return(exp):
            new_exp = resolve_labels_exp(exp, v)
            return replace(n, exp=new_exp)
        case parser.ExpNode(exp):
            new_exp = resolve_labels_exp(exp, v)
            return replace(n, exp=new_exp)
        case parser.If(cond, thing):
            new_cond = resolve_labels_exp(cond, v)
            new_then = resolve_labels_stm(thing, v)
            return replace(n, condition=new_cond, then=new_then)
        case parser.IfElse(cond, thing, other):
            new_cond = resolve_labels_exp(cond, v)
            new_then = resolve_labels_stm(thing, v)
            new_other = resolve_labels_stm(other, v)
            return replace(n, condition=new_cond,
                           then=new_then,
                           otherwise=new_other)
        case parser.Label(id, statement):
            if v.check_in_scope(id):
                raise RuntimeError(f'Label {id} is already in scope')
            new_id = make_temporary(f'Label{id}')
            v.register(id, new_id)
            new_stm = resolve_labels_stm(statement, v)
            return replace(n, id=new_id, stm=new_stm)
        case parser.Goto():
            return n
        case parser.Compound(block):
            new_block = resolve_labels_block(block, v)
            return replace(n, block=new_block)
        case parser.Break() | parser.Continue():
            return n
        case parser.While(cond, body, label):
            new_cond = resolve_labels_exp(cond, v)
            new_body = resolve_labels_stm(body, v)
            return parser.While(new_cond, new_body, label)
        case parser.DoWhile(body, cond, label):
            new_body = resolve_labels_stm(body, v)
            new_cond = resolve_labels_exp(cond, v)
            return parser.DoWhile(new_body, new_cond, label)
        case parser.For(init, mid, post, body, label):
            new_init = resolve_labels_for_init(init, v)
            new_mid = None if mid is None else resolve_labels_exp(mid, v)
            new_post = None if post is None else resolve_labels_exp(post, v)
            new_body = resolve_labels_stm(body, v)
            return parser.For(new_init, new_mid, new_post, new_body, label)
        case parser.Switch(exp, body, label):
            new_body = resolve_labels_stm(body, v)
            return parser.Switch(exp, new_body, label)
        case parser.Case(cond, stm, label):
            new_stm = resolve_labels_stm(stm, v)
            return parser.Case(cond, new_stm, label)
        case parser.Default(stm, label):
            new_stm = resolve_labels_stm(stm, v)
            return parser.Default(new_stm, label)
        case _:
            raise NotImplementedError(f'Unhandled statement {n}')


def resolve_labels_exp(n: parser.Expression,
                       v: VariableMap) -> parser.Expression:
    match n:
        case parser.Constant():
            return n
        case parser.Assignment(lhs, rhs):
            new_lhs = resolve_labels_exp(lhs, v)
            new_rhs = resolve_labels_exp(rhs, v)
            return replace(n, left=new_lhs, right=new_rhs)
        case parser.CompoundAssign(_, lhs, rhs):
            new_lhs = resolve_labels_exp(lhs, v)
            new_rhs = resolve_labels_exp(rhs, v)
            return replace(n, left=new_lhs, right=new_rhs)
        case parser.Var():
            return n
        case parser.Unary(_, exp):
            new_exp = resolve_labels_exp(exp, v)
            return replace(n, exp=new_exp)
        case parser.Binary(_, lhs, rhs):
            new_lhs = resolve_labels_exp(lhs, v)
            new_rhs = resolve_labels_exp(rhs, v)
            return replace(n, left=new_lhs, right=new_rhs)
        case parser.Postfix(_, exp):
            new_exp = resolve_labels_exp(exp, v)
            return replace(n, exp=new_exp)
        case parser.Conditional(cond, t, f):
            new_cond = resolve_labels_exp(cond, v)
            new_t = resolve_labels_exp(t, v)
            new_f = resolve_labels_exp(f, v)
            return replace(n, condition=new_cond, t=new_t, f=new_f)
        case _:
            raise NotImplementedError(f'Unhandled exp {n}')


def resolve_labels_decl(n: parser.DeclareNode,
                        v: VariableMap) -> parser.DeclareNode:
    if n.exp is None:
        return n
    tmp_exp = cast(parser.Expression, n.exp)
    new_exp = resolve_labels_exp(tmp_exp, v)
    return replace(n, exp=new_exp)


# Validating and Replacing Labels on Goto


def resolve_goto_program(n: parser.Program,
                         v: VariableMap) -> parser.Program:
    func_node = resolve_goto_func(n.function_definition, v)
    return replace(n, function_definition=func_node)


def resolve_goto_func(n: parser.Function,
                      v: VariableMap) -> parser.Function:
    body = resolve_goto_block(n.body, v)
    return replace(n, body=body)


def resolve_goto_block(n: parser.Block,
                       v: VariableMap) -> parser.Block:
    items = [resolve_goto_block_items(x, v) for x in n.block_items]
    return replace(n, block_items=items)


def resolve_goto_block_items(n: parser.Block_Item,
                             v: VariableMap) -> parser.Block_Item:
    match n:
        case parser.S(statement):
            stm = resolve_goto_stm(statement, v)
            return replace(n, statement=stm)
        case parser.D(declare):
            decl = resolve_goto_decl(declare, v)
            return replace(n, declaration=decl)
        case _:
            raise RuntimeError(f'impossible {n}')


def resolve_goto_for_init(i: parser.ForInit,
                          v: VariableMap) -> parser.ForInit:
    match i:
        case None:
            return None
        case parser.DeclareNode():
            return resolve_goto_decl(i, v)
        case _ if isinstance(i, parser.Expression):
            return resolve_goto_exp(i, v)
        case _:
            raise RuntimeError('Impossible')


def resolve_goto_stm(n: parser.Statement,
                     v: VariableMap) -> parser.Statement:
    match n:
        case parser.Null():
            return n
        case parser.Return(exp):
            new_exp = resolve_goto_exp(exp, v)
            return replace(n, exp=new_exp)
        case parser.ExpNode(exp):
            new_exp = resolve_goto_exp(exp, v)
            return replace(n, exp=new_exp)
        case parser.If(cond, thing):
            new_cond = resolve_goto_exp(cond, v)
            new_then = resolve_goto_stm(thing, v)
            return replace(n, condition=new_cond, then=new_then)
        case parser.IfElse(cond, thing, other):
            new_cond = resolve_goto_exp(cond, v)
            new_then = resolve_goto_stm(thing, v)
            new_other = resolve_goto_stm(other, v)
            return replace(n, condition=new_cond,
                           then=new_then,
                           otherwise=new_other)
        case parser.Label(_, statement):
            new_stm = resolve_goto_stm(statement, v)
            return replace(n, stm=new_stm)
        case parser.Goto(id):
            new_id = v.lookup(id)
            if new_id is None or not v.check_in_scope(id):
                raise NotImplementedError(f'There is no {id} to Goto')
            return replace(n, id=new_id)
        case parser.Compound(block):
            new_block = resolve_goto_block(block, v)
            return replace(n, block=new_block)
        case parser.Break() | parser.Continue():
            return n
        case parser.While(cond, body, label):
            new_cond = resolve_goto_exp(cond, v)
            new_body = resolve_goto_stm(body, v)
            return parser.While(new_cond, new_body, label)
        case parser.DoWhile(body, cond, label):
            new_body = resolve_goto_stm(body, v)
            new_cond = resolve_goto_exp(cond, v)
            return parser.DoWhile(new_body, new_cond, label)
        case parser.For(init, mid, post, body, label):
            new_init = resolve_goto_for_init(init, v)
            new_mid = None if mid is None else resolve_goto_exp(mid, v)
            new_post = None if post is None else resolve_goto_exp(post, v)
            new_body = resolve_goto_stm(body, v)
            return parser.For(new_init, new_mid, new_post, new_body, label)
        case parser.Switch(exp, body, label):
            new_body = resolve_goto_stm(body, v)
            return parser.Switch(exp, new_body, label)
        case parser.Case(cond, stm, label):
            new_stm = resolve_goto_stm(stm, v)
            return parser.Case(cond, new_stm, label)
        case parser.Default(stm, label):
            new_stm = resolve_goto_stm(stm, v)
            return parser.Default(new_stm, label)
        case _:
            raise NotImplementedError(f'Unhandled statement {n}')


def resolve_goto_exp(n: parser.Expression,
                     v: VariableMap) -> parser.Expression:
    match n:
        case parser.Constant():
            return n
        case parser.Assignment(lhs, rhs):
            new_lhs = resolve_goto_exp(lhs, v)
            new_rhs = resolve_goto_exp(rhs, v)
            return replace(n, left=new_lhs, right=new_rhs)
        case parser.CompoundAssign(_, lhs, rhs):
            new_lhs = resolve_goto_exp(lhs, v)
            new_rhs = resolve_goto_exp(rhs, v)
            return replace(n, left=new_lhs, right=new_rhs)
        case parser.Var():
            return n
        case parser.Unary(_, exp):
            new_exp = resolve_goto_exp(exp, v)
            return replace(n, exp=new_exp)
        case parser.Binary(_, lhs, rhs):
            new_lhs = resolve_goto_exp(lhs, v)
            new_rhs = resolve_labels_exp(rhs, v)
            return replace(n, left=new_lhs, right=new_rhs)
        case parser.Postfix(_, exp):
            new_exp = resolve_goto_exp(exp, v)
            return replace(n, exp=new_exp)
        case parser.Conditional(cond, t, f):
            new_cond = resolve_goto_exp(cond, v)
            new_t = resolve_goto_exp(t, v)
            new_f = resolve_goto_exp(f, v)
            return replace(n, condition=new_cond, t=new_t, f=new_f)
        case _:
            raise NotImplementedError(f'Unhandled exp {n}')


def resolve_goto_decl(n: parser.DeclareNode,
                      v: VariableMap) -> parser.DeclareNode:
    if n.exp is None:
        return n
    tmp_exp = cast(parser.Expression, n.exp)
    new_exp = resolve_labels_exp(tmp_exp, v)
    return replace(n, exp=new_exp)


def resolve_program(p: parser.Program) -> parser.Program:
    var_map = VariableMap()
    # First pass collects and replaces label stms
    ast = resolve_labels_program(p, var_map)
    var_map.print_topmost()
    # Second pass replaces and validates goto labels
    ast = resolve_goto_program(ast, var_map)
    return ast
