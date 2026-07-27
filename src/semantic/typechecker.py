import parser
from dataclasses import dataclass
from typing import cast

from utility import Identifier


@dataclass(frozen=True)
class IntType():
    pass


@dataclass(frozen=True)
class FunType():
    param_count: int


SymbolType = IntType | FunType


@dataclass(frozen=True)
class SymbolRecord():
    type: SymbolType
    defined: bool


class SymbolTable():
    def __init__(self) -> None:
        self.table: dict[Identifier, SymbolRecord] = dict()

    def add(self,
            key: Identifier,
            val: SymbolType,
            defined: bool = False) -> None:
        self.table[key] = SymbolRecord(val, defined)

    def get(self, key: Identifier) -> SymbolRecord:
        return self.table[key]

    def __contains__(self, item) -> bool:
        return item in self.table


def typecheck_program(n: parser.Program) -> None:
    s = SymbolTable()
    for f in n.function_definition:
        typecheck_fun_decl(f, s)


def typecheck_fun_decl(n: parser.FunDecl,
                       s: SymbolTable) -> None:
    fun_type = FunType(len(n.function_definition.params))
    has_body = n.function_definition.body is not None
    already_defined = False
    if n.function_definition.name in s:
        old_decl = s.get(n.function_definition.name)
        if not isinstance(old_decl.type, FunType):
            raise RuntimeError('Incompatible function declaration')
        already_defined = old_decl.defined
        if already_defined and has_body:
            raise RuntimeError('Function is defined more than once')
        if fun_type.param_count != old_decl.type.param_count:
            raise RuntimeError('Function has mismatched params')
    s.add(n.function_definition.name,
          fun_type,
          defined=(already_defined or has_body))
    if has_body:
        body = cast(parser.Block, n.function_definition.body)
        for param in n.function_definition.params:
            s.add(param, IntType())
        typecheck_block(body, s)


def typecheck_dec(n: parser.Declaration,
                  s: SymbolTable) -> None:
    match n:
        case parser.VarDecl(var):
            typecheck_var_decl(var, s)
        case parser.FunDecl():
            typecheck_fun_decl(n, s)
        case _:
            raise RuntimeError('Unknown declaration')


def typecheck_block(n: parser.Block,
                    s: SymbolTable) -> None:
    for x in n.block_items:
        match x:
            case parser.S(stm):
                typecheck_stm(stm, s)
            case parser.D(dec):
                typecheck_dec(dec, s)
            case _:
                raise RuntimeError('Unknown parser block')


def typecheck_var_decl(n: parser.VariableDefinition,
                       s: SymbolTable) -> None:
    s.add(n.name, IntType())
    if n.exp is not None:
        typecheck_exp(n.exp, s)


def typecheck_stm(n: parser.Statement,
                  s: SymbolTable) -> None:
    match n:
        case parser.Return(exp):
            typecheck_exp(exp, s)
        case parser.ExpNode(exp):
            typecheck_exp(exp, s)
        case parser.If(exp, stm):
            typecheck_exp(exp, s)
            typecheck_stm(stm, s)
        case parser.IfElse(exp, then, otherw):
            typecheck_exp(exp, s)
            typecheck_stm(then, s)
            typecheck_stm(otherw, s)
        case parser.Null():
            return
        case parser.Label(_, stm):
            typecheck_stm(stm, s)
        case parser.Goto():
            return
        case parser.Compound(block):
            typecheck_block(block, s)
        case parser.Break():
            return
        case parser.Continue():
            return
        case parser.While(cond, body, _):
            typecheck_exp(cond, s)
            typecheck_stm(body, s)
        case parser.DoWhile(body, cond, _):
            typecheck_stm(body, s)
            typecheck_exp(cond, s)
        case parser.For(init, cond, post, body, _):
            if init is not None:
                match init:
                    case parser.VarDecl(v):
                        typecheck_var_decl(v, s)
                    case _:
                        # Warning: This passes assertion to next function call
                        # This is going to make checkig for errors harder
                        # Part of this is due to parser.Expression being an Union
                        # And this doesn't seem to match well
                        typecheck_exp(init, s)
            if cond is not None:
                typecheck_exp(cond, s)
            if post is not None:
                typecheck_exp(post, s)
            typecheck_stm(body, s)
        case parser.Case(cond, stm, _):
            typecheck_exp(cond, s)
            typecheck_stm(stm, s)
        case parser.Default(stm, _):
            typecheck_stm(stm, s)
        case parser.Switch(exp, body, _):
            typecheck_exp(exp, s)
            typecheck_stm(body, s)
        case _:
            raise NotImplementedError('Need to do statements')


def typecheck_exp(n: parser.Expression,
                  s: SymbolTable) -> None:
    match n:
        case parser.FunctionCall(f, args):
            lookup = s.get(f)
            if isinstance(lookup.type, IntType):
                raise RuntimeError(f'Var used as function {n}')
            if isinstance(lookup.type, FunType) and lookup.type.param_count != len(args):
                raise RuntimeError('Function used with wrong amount of args')
            for arg in args:
                typecheck_exp(arg, s)
        case parser.Var(v):
            if not isinstance(s.get(v).type, IntType):
                raise RuntimeError(f'Function used as variable {n}')
        case parser.Unary(_, exp):
            typecheck_exp(exp, s)
        case parser.Binary(_, left, right):
            typecheck_exp(left, s)
            typecheck_exp(right, s)
        case parser.Constant():
            return
        case parser.Assignment(left, right):
            typecheck_exp(left, s)
            typecheck_exp(right, s)
        case parser.CompoundAssign(_, left, right):
            typecheck_exp(left, s)
            typecheck_exp(right, s)
        case parser.Postfix(_, exp):
            typecheck_exp(exp, s)
        case parser.Conditional(cond, t, f):
            typecheck_exp(cond, s)
            typecheck_exp(t, s)
            typecheck_exp(f, s)
        case _:
            raise NotImplementedError(f'More junk {n}')
