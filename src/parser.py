from dataclasses import dataclass
from typing import Type, cast
from enum import Enum, auto
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


@dataclass
class Unary:
    unary_operator: Unary_Operator
    exp: 'Expression'


Expression = Unary | Constant


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
    if expect_tk(lexer.TkConstant, t, index):
        tok = cast(lexer.TkConstant, t[index])
        return (Constant(tok.val), index+1)
    return None


def parse_identifier(t: list[lexer.Token],
                     index: int) -> tuple[Identifier, int] | None:
    if expect_tk(lexer.TkIdentifier, t, index):
        tok = cast(lexer.TkIdentifier, t[index])
        return (Identifier(tok.val), index+1)
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


def parse_expr(t: list[lexer.Token],
               index: int) -> tuple[Expression, int] | None:
    if (index >= len(t)):
        return None
    match t[index]:
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
        case lexer.TkMinus():
            print('Minus world')
            index += 1
            result = parse_expr(t, index)
            if result is None:
                print(f'No sub expression {t[index-1]} and then {t[index]}')
                return None
            inner_expr, index = result
            return Unary(Unary_Operator.NEGATION, inner_expr), index
        case lexer.TkTilde():
            index += 1
            result = parse_expr(t, index)
            if result is None:
                return None
            inner_expr, index = result
            return Unary(Unary_Operator.COMPLEMENT, inner_expr), index
        case lexer.TkConstant():
            print(f'Got constant {t[index]}')
            return parse_constant(t, index)
        case _:
            print(f'Default {t[index]}')
            return None


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
