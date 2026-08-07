from dataclasses import dataclass
from itertools import takewhile
from string import ascii_letters, digits, whitespace
from typing import Generator

from utility import peek


@dataclass
class TkOpenBrace:
    pass


@dataclass
class TkCloseBrace:
    pass


@dataclass
class TkOpenParenthesis:
    pass


@dataclass
class TkCloseParenthesis:
    pass


@dataclass
class TkSemicolon:
    pass


@dataclass
class TkColon:
    pass


@dataclass
class TkSingleQuote:
    pass


@dataclass
class TkComma:
    pass


@dataclass
class TkMinus:
    pass


@dataclass
class TkDecrement:
    pass


@dataclass
class TkTilde:
    pass


@dataclass
class TkForwardSlash:
    pass


@dataclass
class TkAsterisk:
    pass


@dataclass
class TkBackSlash:
    pass


@dataclass
class TkConstant:
    val: str


@dataclass
class TkInt:
    pass


@dataclass
class TkVoid:
    pass


@dataclass
class TkReturn:
    pass


@dataclass
class TkIdentifier:
    val: str


@dataclass
class TkPlus:
    pass


@dataclass
class TkPercent:
    pass


@dataclass
class TkLessThan:
    pass


@dataclass
class TkLessEqual:
    pass


@dataclass
class TkGreaterThan:
    pass


@dataclass
class TkGreaterEqual:
    pass


@dataclass
class TkLShift:
    pass


@dataclass
class TkRShift:
    pass


@dataclass
class TkLAnd:
    pass


@dataclass
class TkBAnd:
    pass


@dataclass
class TkLOr:
    pass


@dataclass
class TkBOr:
    pass


@dataclass
class TkXor:
    pass


@dataclass
class TkEqual:
    pass


@dataclass
class TkDEqual:
    pass


@dataclass
class TkNot:
    pass


@dataclass
class TkNotEqual:
    pass


@dataclass
class TkPlusEqual:
    pass


@dataclass
class TkSubEqual:
    pass


@dataclass
class TkMulEqual:
    pass


@dataclass
class TkDivEqual:
    pass


@dataclass
class TkModEqual:
    pass


@dataclass
class TkBAndEqual:
    pass


@dataclass
class TkBOrEqual:
    pass


@dataclass
class TkXorEqual:
    pass


@dataclass
class TkLSEqual:
    pass


@dataclass
class TkRSEqual:
    pass


@dataclass
class TkIncrement:
    pass


@dataclass
class TkQuestion:
    pass


@dataclass
class TkIf:
    pass


@dataclass
class TkElse:
    pass


@dataclass
class TkGoto:
    pass


@dataclass
class TkDo:
    pass


@dataclass
class TkWhile:
    pass


@dataclass
class TkFor:
    pass


@dataclass
class TkBreak:
    pass


@dataclass
class TkContinue:
    pass


@dataclass
class TkSwitch:
    pass


@dataclass
class TkCase:
    pass


@dataclass
class TkDefault:
    pass


@dataclass
class TkStatic:
    pass


@dataclass
class TkExtern:
    pass


Token = (TkOpenParenthesis
         | TkCloseParenthesis
         | TkOpenBrace
         | TkCloseBrace
         | TkSemicolon
         | TkComma
         | TkForwardSlash
         | TkBackSlash
         | TkAsterisk
         | TkColon
         | TkMinus
         | TkDecrement
         | TkTilde
         | TkInt
         | TkVoid
         | TkReturn
         | TkConstant
         | TkIdentifier
         | TkPlus
         | TkPercent
         | TkLShift
         | TkRShift
         | TkLAnd
         | TkBAnd
         | TkLOr
         | TkBOr
         | TkXor
         | TkLessThan
         | TkLessEqual
         | TkGreaterThan
         | TkGreaterEqual
         | TkEqual
         | TkDEqual
         | TkNot
         | TkNotEqual
         | TkPlusEqual
         | TkSubEqual
         | TkMulEqual
         | TkDivEqual
         | TkModEqual
         | TkBAndEqual
         | TkBOrEqual
         | TkXorEqual
         | TkLSEqual
         | TkRSEqual
         | TkIncrement
         | TkQuestion
         | TkIf
         | TkElse
         | TkGoto
         | TkDo
         | TkWhile
         | TkFor
         | TkBreak
         | TkContinue
         | TkSwitch
         | TkCase
         | TkDefault
         | TkStatic
         | TkExtern)


def parse_constant(x: str) -> TkConstant:
    token_string = ''.join(c for c in takewhile(lambda ch: ch in digits, x))
    if len(token_string) < len(x) and x[len(token_string)] in ascii_letters:
        raise ValueError(f'Invalid constant stuffix {x}')

    return TkConstant(token_string)


def parse_identity_keyword(x: str) -> tuple[Token, int]:
    """Takes a string and returns either an identifier or a keyword token"""
    if (x == ''):
        raise ValueError('Tried to parse empty string as identity')
    head = x[0]
    LEGAL_CHAR = digits + ascii_letters + '_'
    tail = ''.join(c for c in takewhile(lambda ch: ch in LEGAL_CHAR, x[1:]))
    token_string = head + tail
    token_len = len(token_string)
    match token_string:
        case 'int':
            return (TkInt(), token_len)
        case 'void':
            return (TkVoid(), token_len)
        case 'return':
            return (TkReturn(), token_len)
        case 'if':
            return (TkIf(), token_len)
        case 'else':
            return (TkElse(), token_len)
        case 'goto':
            return (TkGoto(), token_len)
        case 'do':
            return (TkDo(), token_len)
        case 'while':
            return (TkWhile(), token_len)
        case 'for':
            return (TkFor(), token_len)
        case 'break':
            return (TkBreak(), token_len)
        case 'continue':
            return (TkContinue(), token_len)
        case 'switch':
            return (TkSwitch(), token_len)
        case 'case':
            return (TkCase(), token_len)
        case 'default':
            return (TkDefault(), token_len)
        case 'static':
            return (TkStatic(), token_len)
        case 'extern':
            return (TkExtern(), token_len)
        case _:
            return (TkIdentifier(token_string), token_len)


def tokenize_string(line: str) -> Generator[Token]:
    """Takes a str and return a list of matching tokens"""
    CHRS = ascii_letters + '_'
    index = 0

    while index < len(line):
        match item := line[index]:
            case '(':
                yield TkOpenParenthesis()
                index += 1
            case ')':
                yield TkCloseParenthesis()
                index += 1
            case '{':
                yield TkOpenBrace()
                index += 1
            case '}':
                yield TkCloseBrace()
                index += 1
            case ';':
                yield TkSemicolon()
                index += 1
            case '/':
                index += 1
                peeked = peek(line, index)
                # checking for a line comment
                if peeked == '/':
                    return
                elif peeked == '=':
                    index += 1
                    yield TkDivEqual()
                else:
                    yield TkForwardSlash()
            case '-':
                index += 1
                peeked = peek(line, index)
                # checking for --
                if peeked == '-':
                    yield TkDecrement()
                    index += 1
                elif peeked == '=':
                    yield TkSubEqual()
                    index += 1
                else:
                    yield TkMinus()
            case '~':
                yield TkTilde()
                index += 1
            case ':':
                yield TkColon()
                index += 1
            case '\'':
                yield TkBackSlash()
                index += 1
            case '*':
                index += 1
                peeked = peek(line, index)
                if peeked == '=':
                    index += 1
                    yield TkMulEqual()
                else:
                    yield TkAsterisk()
            case ',':
                yield TkComma()
                index += 1
            case '+':
                index += 1
                peeked = peek(line, index)
                if peeked == '=':
                    yield TkPlusEqual()
                    index += 1
                elif peeked == '+':
                    yield TkIncrement()
                    index += 1
                else:
                    yield TkPlus()
            case '%':
                index += 1
                peeked = peek(line, index)
                if peeked == '=':
                    index += 1
                    yield TkModEqual()
                else:
                    yield TkPercent()

            case '<':
                index += 1
                peeked = peek(line, index)
                if peeked == '<':
                    index += 1
                    # Yuck
                    peeked = peek(line, index)
                    if peeked == '=':
                        index += 1
                        yield TkLSEqual()
                    else:
                        yield TkLShift()
                elif peeked == '=':
                    yield TkLessEqual()
                    index += 1
                else:
                    yield TkLessThan()
            case '>':
                index += 1
                peeked = peek(line, index)
                if peeked == '>':
                    index += 1
                    peeked = peek(line, index)
                    if peeked == '=':
                        index += 1
                        yield TkRSEqual()
                    else:
                        yield TkRShift()
                elif peeked == '=':
                    yield TkGreaterEqual()
                    index += 1
                else:
                    yield TkGreaterThan()
            case '&':
                index += 1
                peeked = peek(line, index)
                if peeked == '&':
                    yield TkLAnd()
                    index += 1
                elif peeked == '=':
                    yield TkBAndEqual()
                    index += 1
                else:
                    yield TkBAnd()
            case '|':
                index += 1
                peeked = peek(line, index)
                if peeked == '|':
                    yield TkLOr()
                    index += 1
                elif peeked == '=':
                    yield TkBOrEqual()
                    index += 1
                else:
                    yield TkBOr()
            case '^':
                index += 1
                peeked = peek(line, index)
                if peeked == '=':
                    yield TkXorEqual()
                    index += 1
                else:
                    yield TkXor()
            case '=':
                index += 1
                # checking for !=
                if index <= len(line) and line[index] == '=':
                    yield TkDEqual()
                    index += 1
                else:
                    yield TkEqual()
            case '!':
                index += 1
                # checking for !=
                if index <= len(line) and line[index] == '=':
                    yield TkNotEqual()
                    index += 1
                else:
                    yield TkNot()
            case '?':
                index += 1
                yield TkQuestion()
            case c if c in whitespace:
                # TODO Handle whitespace for strings
                index += 1
            case '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9':
                # TODO Start of a constant token
                # Output should either be a valid constant or an invalid token
                thing = parse_constant(line[index:])
                yield thing
                index += len(thing.val)
            case c if c in CHRS:
                ret, ret_len = parse_identity_keyword(line[index:])
                yield ret
                index += ret_len
            case _:
                raise ValueError(f'Unkown token prefix {item}')


def tokenize_file(filepath: str) -> list[Token]:
    with open(filepath, 'r') as f:
        result = [t for line in f for t in tokenize_string(line)]
        # result = list(chain(*(tokenize_string(line) for line in f)))
        return result
