from dataclasses import dataclass
from string import whitespace, digits, ascii_letters
from itertools import chain, takewhile


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
class TkForwardSlash:
    pass


@dataclass
class TkStar:
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


Token = (TkOpenParenthesis
         | TkCloseParenthesis
         | TkOpenBrace
         | TkCloseBrace
         | TkSemicolon
         | TkComma
         | TkForwardSlash
         | TkBackSlash
         | TkStar
         | TkColon
         | TkMinus
         | TkInt
         | TkVoid
         | TkReturn
         | TkConstant
         | TkIdentifier)


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
    LEGAL_CHAR = digits + ascii_letters
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
        case _:
            return (TkIdentifier(token_string), token_len)


def tokenize_string(line: str) -> list[Token]:
    """Takes a str and return a list of matching tokens"""
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
                # checking for a line comment
                if index <= len(line) and line[index] == '/':
                    return token_list
                token_list.append(TkForwardSlash())
            case '-':
                token_list.append(TkMinus())
                index += 1
            case ':':
                token_list.append(TkColon())
                index += 1
            case '\'':
                token_list.append(TkBackSlash())
                index += 1
            case '*':
                token_list.append(TkStar())
                index += 1
            case ',':
                token_list.append(TkComma())
                index += 1
            case c if c in whitespace:
                # TODO Handle whitespace for strings
                index += 1
            case '0' | '1' | '2' | '3' | '5' | '6' | '7' | '8' | '9':
                # TODO Start of a constant token
                # Output should either be a valid constant or an invalid token
                thing = parse_constant(line[index:])
                token_list.append(thing)
                index += len(thing.val)
            case c if c in ascii_letters:
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


if __name__ == '__main__':
    with open('./hello.c') as source:
        for line in source:
            for tokens in tokenize_string(line):
                print(tokens)
