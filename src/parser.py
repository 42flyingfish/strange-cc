from dataclasses import dataclass
from typing import Type, cast
import lexer


@dataclass
class Constant:
    val: str


@dataclass
class Identifier:
    val: str


@dataclass
class Return:
    exp: Constant


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
    ret = parse_constant(t, index)
    if ret is None:
        return None
    index += 1
    if not expect_tk(lexer.TkSemicolon, t, index):
        return None
    index += 1
    return (Return(ret[0]), index)


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
