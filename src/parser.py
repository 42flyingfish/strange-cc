
from dataclasses import dataclass
from enum import Enum, auto
from typing import Type

import lexer


@dataclass
class Constant:
    val: str


@dataclass
class Identifier:
    val: str


class Unary_Operator(Enum):
    NEGATION = auto()
    COMPLEMENT = auto()


class Bin_Op(Enum):
    """Binary Operators"""
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    REMAINDER = auto()


@dataclass
class Unary:
    unary_operator: Unary_Operator
    exp: 'Expression'


@dataclass
class Binary:
    binary_operator: Bin_Op
    left: 'Expression'
    right: 'Expression'


Expression = Unary | Constant | Binary


@dataclass
class Return:
    exp: Expression


type Statement = Return


@dataclass
class Function:
    name: Identifier
    body: Statement


@dataclass
class Program:
    function_definition: Function


def expect_tk(kind: Type,
              tokens: list[lexer.Token],
              index: int, verbosity=True) -> bool:
    if (index >= len(tokens)):
        return False

    if (isinstance(tokens[index], kind)):
        return True
    if verbosity:
        print("DEBUG:")
        print(f"  Expected type: {kind} (from module: {kind.__module__})")
        print(f"  Actual value: {tokens[index]}")
        print(f"  Actual type: {type(tokens[index])} \
        (from module: {type(tokens[index]).__module__})")
        print(repr(tokens[index]))
        print(type(tokens[index]))

        print(f"  isinstance result: {isinstance(tokens[index], kind)}")
    return False


def parse_constant(t: list[lexer.Token],
                   index: int) -> tuple[Constant, int] | None:
    if index >= len(t):
        return None
    match t[index]:
        case lexer.TkConstant(val):
            return Constant(val), index+1
        case _:
            return None


def parse_identifier(t: list[lexer.Token],
                     index: int) -> tuple[Identifier, int] | None:
    if index >= len(t):
        return None
    match t[index]:
        case lexer.TkIdentifier(val):
            return Identifier(val), index+1
        case _:
            return None


def parse_return(t: list[lexer.Token],
                 index: int) -> tuple[Return, int] | None:
    if not expect_tk(lexer.TkReturn, t, index):
        return None
    index += 1
    ret = parse_expr(t, index)
    if ret is None:
        raise RuntimeError(f'No expression {t[index]}')
        return None
    expr, index = ret
    if not expect_tk(lexer.TkSemicolon, t, index):
        return None
    index += 1
    return (Return(expr), index)


def parse_uop(t: list[lexer.Token],
              index: int) -> tuple[Unary_Operator, int] | None:
    if index >= len(t):
        return None
    match t[index]:
        case lexer.TkTilde():
            return Unary_Operator.COMPLEMENT, index+1
        case lexer.TkMinus():
            return Unary_Operator.NEGATION, index+1
        case _:
            None


def parse_factor(t: list[lexer.Token],
                 index: int) -> tuple[Expression, int] | None:
    if (index >= len(t)):
        return None
    match t[index]:
        case lexer.TkConstant():
            return parse_constant(t, index)
        case lexer.TkMinus() | lexer.TkTilde():
            op = parse_uop(t, index)
            if op is None:
                return None
            operator, index = op
            result = parse_factor(t, index)
            if result is None:
                return None
            inner_expr, index = result
            return Unary(operator, inner_expr), index
        case lexer.TkOpenParenthesis():
            index += 1
            result = parse_expr(t, index)
            if result is None:
                return None
            inner_expr, index = result
            if not expect_tk(lexer.TkCloseParenthesis, t, index):
                return None
            index += 1
            return (inner_expr, index)
        case _:
            print(f'Default {t[index]}')
            return None


def parse_binop(t: list[lexer.Token], index: int) -> tuple[Bin_Op, int] | None:
    if index >= len(t):
        return None
    match t[index]:
        case lexer.TkPlus():
            return Bin_Op.ADD, index+1
        case lexer.TkMinus():
            return Bin_Op.SUBTRACT, index+1
        case lexer.TkForwardSlash():
            return Bin_Op.DIVIDE, index+1
        case lexer.TkAsterisk():
            return Bin_Op.MULTIPLY, index+1
        case _:
            return None


def parse_expr(t: list[lexer.Token],
               index: int) -> tuple[Expression, int] | None:
    if (index >= len(t)):
        return None
    result = parse_factor(t, index)
    if result is None:
        return None
    left, index = result

    while True:
        op = parse_binop(t, index)
        if op is None:
            break
        binop, new_index = op
        result = parse_factor(t, new_index)
        if result is None:
            break
        right, new_index = result
        left = Binary(binop, left, right)
        index = new_index
    return left, index


def parse_function(t: list[lexer.Token],
                   index: int) -> tuple[Function, int] | None:
    if not expect_tk(lexer.TkInt, t, index):
        return None
    index += 1
    r_ident = parse_identifier(t, index)
    if (r_ident is None):
        return None
    index = r_ident[1]

    TK_CHUNK = (lexer.TkOpenParenthesis,
                lexer.TkVoid,
                lexer.TkCloseParenthesis,
                lexer.TkOpenBrace)

    for kind in TK_CHUNK:
        if not expect_tk(kind, t, index):
            return None
        else:
            index += 1

    r_statement = parse_return(t, index)
    if (r_statement is None):
        return None
    index = r_statement[1]
    if not expect_tk(lexer.TkCloseBrace, t, index):
        return None
    index += 1
    return (Function(r_ident[0], r_statement[0]), index)


def parse_program(t: list[lexer.Token],
                  index: int) -> Program | None:
    ret = parse_function(t, index)
    if (ret is None):
        return None
    func, num = ret
    if num < len(t):
        return None
    return Program(func)
