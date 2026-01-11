from dataclasses import dataclass
from itertools import chain, takewhile
from string import ascii_letters, digits, whitespace


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
         | TkIf)


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
        case _:
            return (TkIdentifier(token_string), token_len)


def tokenize_string(line: str) -> list[Token]:
    """Takes a str and return a list of matching tokens"""
    CHRS = ascii_letters + '_'
    token_list: list[Token] = []
    index = 0

    while index < len(line):
        match item := line[index]:
            case '(':
                token_list.append(TkOpenParenthesis())
                index += 1
            case ')':
                token_list.append(TkCloseParenthesis())
                index += 1
            case '{':
                token_list.append(TkOpenBrace())
                index += 1
            case '}':
                token_list.append(TkCloseBrace())
                index += 1
            case ';':
                token_list.append(TkSemicolon())
                index += 1
            case '/':
                index += 1
                peek = None if index > len(line) else line[index]
                # checking for a line comment
                if peek == '/':
                    return token_list
                elif peek == '=':
                    index += 1
                    token_list.append(TkDivEqual())
                else:
                    token_list.append(TkForwardSlash())
            case '-':
                index += 1
                peek = None if index > len(line) else line[index]
                # checking for --
                if peek == '-':
                    token_list.append(TkDecrement())
                    index += 1
                elif peek == '=':
                    token_list.append(TkSubEqual())
                    index += 1
                else:
                    token_list.append(TkMinus())
            case '~':
                token_list.append(TkTilde())
                index += 1
            case ':':
                token_list.append(TkColon())
                index += 1
            case '\'':
                token_list.append(TkBackSlash())
                index += 1
            case '*':
                index += 1
                peek = None if index > len(line) else line[index]
                if peek == '=':
                    index += 1
                    token_list.append(TkMulEqual())
                else:
                    token_list.append(TkAsterisk())
            case ',':
                token_list.append(TkComma())
                index += 1
            case '+':
                index += 1
                peek = None if index > len(line) else line[index]
                if peek == '=':
                    token_list.append(TkPlusEqual())
                    index += 1
                elif peek == '+':
                    token_list.append(TkIncrement())
                    index += 1
                else:
                    token_list.append(TkPlus())
            case '%':
                index += 1
                peek = None if index > len(line) else line[index]
                if peek == '=':
                    index += 1
                    token_list.append(TkModEqual())
                else:
                    token_list.append(TkPercent())

            case '<':
                index += 1
                peek = None if index > len(line) else line[index]
                if peek == '<':
                    index += 1
                    # Yuck
                    peek = None if index > len(line) else line[index]
                    if peek == '=':
                        index += 1
                        token_list.append(TkLSEqual())
                    else:
                        token_list.append(TkLShift())
                elif peek == '=':
                    token_list.append(TkLessEqual())
                    index += 1
                else:
                    token_list.append(TkLessThan())
            case '>':
                index += 1
                peek = None if index > len(line) else line[index]
                if peek == '>':
                    index += 1
                    peek = None if index > len(line) else line[index]
                    if peek == '=':
                        index += 1
                        token_list.append(TkRSEqual())
                    else:
                        token_list.append(TkRShift())
                elif peek == '=':
                    token_list.append(TkGreaterEqual())
                    index += 1
                else:
                    token_list.append(TkGreaterThan())
            case '&':
                index += 1
                peek = None if index > len(line) else line[index]
                if peek == '&':
                    token_list.append(TkLAnd())
                    index += 1
                elif peek == '=':
                    token_list.append(TkBAndEqual())
                    index += 1
                else:
                    token_list.append(TkBAnd())
            case '|':
                index += 1
                peek = None if index > len(line) else line[index]
                if peek == '|':
                    token_list.append(TkLOr())
                    index += 1
                elif peek == '=':
                    token_list.append(TkBOrEqual())
                    index += 1
                else:
                    token_list.append(TkBOr())
            case '^':
                index += 1
                peek = None if index > len(line) else line[index]
                if peek == '=':
                    token_list.append(TkXorEqual())
                    index += 1
                else:
                    token_list.append(TkXor())
            case '=':
                index += 1
                # checking for !=
                if index <= len(line) and line[index] == '=':
                    token_list.append(TkDEqual())
                    index += 1
                else:
                    token_list.append(TkEqual())
            case '!':
                index += 1
                # checking for !=
                if index <= len(line) and line[index] == '=':
                    token_list.append(TkNotEqual())
                    index += 1
                else:
                    token_list.append(TkNot())
            case '?':
                index += 1
                token_list.append(TkQuestion())
            case c if c in whitespace:
                # TODO Handle whitespace for strings
                index += 1
            case '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9':
                # TODO Start of a constant token
                # Output should either be a valid constant or an invalid token
                thing = parse_constant(line[index:])
                token_list.append(thing)
                index += len(thing.val)
            case c if c in CHRS:
                ret, ret_len = parse_identity_keyword(line[index:])
                token_list.append(ret)
                index += ret_len
            case _:
                raise ValueError(f'Unkown token prefix {item}')
    return token_list


def tokenize_file(filepath: str) -> list[Token]:
    with open(filepath, 'r') as f:
        result = list(chain(*(tokenize_string(line) for line in f)))
        return result
