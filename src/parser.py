from dataclasses import dataclass
from enum import Enum, auto
from typing import Type

import lexer
from utility import Identifier


@dataclass
class Constant:
    val: str


@dataclass
class Var:
    identifier: Identifier


class Unary_Operator(Enum):
    NEGATION = auto()
    COMPLEMENT = auto()
    NOT = auto()
    INCREMENT = auto()
    DECREMENT = auto()


class Bin_Op(Enum):
    """Binary Operators"""
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    REMAINDER = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()
    BIT_AND = auto()
    BIT_OR = auto()
    XOR = auto()
    LOG_AND = auto()
    LOG_OR = auto()
    LESS_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_EQUAL = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    ASSIGN = auto()
    ADD_ASSIGN = auto()
    SUB_ASSIGN = auto()
    MUL_ASSIGN = auto()
    DIV_ASSIGN = auto()
    MOD_ASSIGN = auto()
    BAND_ASSIGN = auto()
    BOR_ASSIGN = auto()
    XOR_ASSIGN = auto()
    LS_ASSIGN = auto()
    RS_ASSIGN = auto()


@dataclass
class Unary:
    unary_operator: Unary_Operator
    exp: 'Expression'


@dataclass
class Binary:
    binary_operator: Bin_Op
    left: 'Expression'
    right: 'Expression'


@dataclass
class Assignment:
    left: 'Expression'
    right: 'Expression'


@dataclass
class CompoundAssign:
    binary_operator: Bin_Op
    left: 'Expression'
    right: 'Expression'


@dataclass
class Postfix:
    increment: bool
    exp: 'Expression'


@dataclass
class Conditional:
    condition: 'Expression'
    t: 'Expression'
    f: 'Expression'


Expression = (Constant | Var | Unary | Binary | Assignment
              | CompoundAssign | Postfix | Conditional)


@dataclass
class Return:
    exp: Expression


@dataclass
class ExpNode:
    exp: Expression

# Oddly enough trying to forward declare Statement and making optional
# causes a TypeError where it thinks that it is a str
# Until I figure out what I did wrong, I am declaring them seperate


@dataclass
class If:
    condition: Expression
    then: 'Statement'


@dataclass
class IfElse:
    condition: Expression
    then: 'Statement'
    otherwise: 'Statement'


@dataclass
class Null:
    pass


@dataclass
class Label:
    id: Identifier
    stm: 'Statement'


@dataclass
class Goto:
    id: Identifier


@dataclass
class Compound:
    block: 'Block'


Statement = (Return
             | ExpNode
             | If
             | IfElse
             | Null
             | Label
             | Goto
             | Compound)


@dataclass
class DeclareNode:
    name: Identifier
    exp: Expression | None = None


type Declaration = DeclareNode


@dataclass
class S:
    statement: Statement


@dataclass
class D:
    declaration: Declaration


Block_Item = S | D


@dataclass
class Block:
    block_items: list[Block_Item]


@dataclass
class Function:
    name: Identifier
    body: Block


@dataclass
class Program:
    function_definition: Function


def expect_tk(kind: Type,
              tokens: list[lexer.Token],
              index: int, verbosity=False) -> bool:
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


def precedence(operator) -> int | None:
    # This takes tokens and gives the respective precedence
    # as if these were binary or ternary operators
    # Unary operators are handled elsewhere
    match operator:
        case (lexer.TkAsterisk()
              | lexer.TkForwardSlash()
              | lexer.TkPercent()):
            return 50
        case (lexer.TkPlus()
              | lexer.TkMinus()):
            return 45
        case (lexer.TkLShift()
              | lexer.TkRShift()):
            return 40
        case (lexer.TkLessThan()
              | lexer.TkLessEqual()
              | lexer.TkGreaterThan()
              | lexer.TkGreaterEqual()):
            return 35
        case (lexer.TkDEqual()
              | lexer.TkNotEqual()):
            return 30
        case lexer.TkBAnd():
            return 25
        case lexer.TkXor():
            return 20
        case lexer.TkBOr():
            return 15
        case lexer.TkLAnd():
            return 10
        case lexer.TkLOr():
            return 5
        case lexer.TkQuestion():
            return 4
        case (lexer.TkEqual()
              | lexer.TkPlusEqual()
              | lexer.TkSubEqual()
              | lexer.TkMulEqual()
              | lexer.TkDivEqual()
              | lexer.TkModEqual()
              | lexer.TkBAndEqual()
              | lexer.TkBOrEqual()
              | lexer.TkXorEqual()
              | lexer.TkLSEqual()
              | lexer.TkRSEqual()):
            return 1
        case _:
            return None


def parse_constant(t: list[lexer.Token],
                   index: int) -> tuple[Constant, int] | None:
    if index >= len(t):
        return None
    match t[index]:
        case lexer.TkConstant(val):
            return Constant(val), index+1
        case _:
            return None


def parse_var(t: list[lexer.Token],
              index: int) -> tuple[Var, int] | None:
    if index >= len(t):
        return None
    result = parse_identifier(t, index)
    if result is None:
        return None
    id, index = result
    return Var(id), index


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
        return None
    expr, index = ret
    if not expect_tk(lexer.TkSemicolon, t, index):
        return None
    index += 1
    return (Return(expr), index)


def parse_exprNode(t: list[lexer.Token],
                   index: int) -> tuple[ExpNode, int] | None:
    ret = parse_expr(t, index)
    if ret is None:
        return None
    expr, index = ret
    if not expect_tk(lexer.TkSemicolon, t, index):
        return None
    index += 1
    return (ExpNode(expr), index)


def parse_uop(t: list[lexer.Token],
              index: int) -> tuple[Unary_Operator, int] | None:
    if index >= len(t):
        return None
    match t[index]:
        case lexer.TkTilde():
            return Unary_Operator.COMPLEMENT, index+1
        case lexer.TkMinus():
            return Unary_Operator.NEGATION, index+1
        case lexer.TkNot():
            return Unary_Operator.NOT, index+1
        case lexer.TkIncrement():
            return Unary_Operator.INCREMENT, index+1
        case lexer.TkDecrement():
            return Unary_Operator.DECREMENT, index+1
        case _:
            return None


def parse_statement(t: list[lexer.Token],
                    index: int) -> tuple[Statement, int] | None:
    if (index >= len(t)):
        return None
    match t[index]:
        case lexer.TkSemicolon():
            return Null(), index+1
        case lexer.TkReturn():
            return parse_return(t, index)
        case lexer.TkIf():
            index += 1
            if not expect_tk(lexer.TkOpenParenthesis, t, index):
                return None
            index += 1
            exp_result = parse_expr(t, index)
            if exp_result is None:
                return None
            exp, index = exp_result
            if not expect_tk(lexer.TkCloseParenthesis, t, index):
                return None
            index += 1
            stm_result = parse_statement(t, index)
            if stm_result is None:
                return None
            stm, index = stm_result
            if expect_tk(lexer.TkElse, t, index):
                index += 1
                stm_result = parse_statement(t, index)
                if stm_result is None:
                    return None
                otherwise, index = stm_result
                if otherwise is None:
                    return If(exp, stm), index
                else:
                    return IfElse(exp, stm, otherwise), index
            else:
                return If(exp, stm), index
        case lexer.TkIdentifier(val):
            index += 1
            if not expect_tk(lexer.TkColon, t, index):
                # This might be a expression instead
                # for example val + 1;
                return parse_exprNode(t, index-1)
            index += 1
            stm_result = parse_statement(t, index)
            if stm_result is None:
                return None
            stm, index = stm_result
            return Label(Identifier(val), stm), index
        case lexer.TkGoto():
            index += 1
            id_result = parse_identifier(t, index)
            if id_result is None:
                return None
            id, index = id_result
            if expect_tk(lexer.TkSemicolon, t, index):
                return Goto(id), index+1
            return None
        case lexer.TkOpenBrace():
            block_result = parse_block(t, index)
            if block_result is None:
                return None
            body, index = block_result
            return Compound(body), index
        case _:
            return parse_exprNode(t, index)


def parse_declaration(t: list[lexer.Token],
                      index: int) -> tuple[Declaration, int] | None:
    if not expect_tk(lexer.TkInt, t, index):
        return None
    index += 1
    id_result = parse_identifier(t, index)
    if id_result is None:
        return None
    id, index = id_result
    match t[index]:
        case lexer.TkSemicolon():
            return DeclareNode(id), index+1
        case lexer.TkEqual():
            index += 1
            exp_result = parse_expr(t, index)
            if exp_result is None:
                return None
            exp, index = exp_result
            if not expect_tk(lexer.TkSemicolon, t, index):
                return None
            return DeclareNode(id, exp), index+1
        case _:
            return None


def parse_block_item(t: list[lexer.Token],
                     index: int) -> tuple[Block_Item, int] | None:
    s_result = parse_statement(t, index)
    if s_result is not None:
        s, index = s_result
        return S(s), index
    d_result = parse_declaration(t, index)
    if d_result is None:
        return None
    d, index = d_result
    return D(d), index


def parse_factor(t: list[lexer.Token],
                 index: int) -> tuple[Expression, int] | None:
    def inner(t: list[lexer.Token],
              index: int) -> tuple[Expression, int] | None:
        if (index >= len(t)):
            return None
        match t[index]:
            case lexer.TkConstant():
                return parse_constant(t, index)
            case (lexer.TkMinus() | lexer.TkTilde() | lexer.TkNot()
                  | lexer.TkIncrement() | lexer.TkDecrement()):
                # TODO, this is needs a rework as more operators will come
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
                id_result = parse_identifier(t, index)
                if id_result is None:
                    return None
                id, index = id_result
                return Var(id), index
    result = inner(t, index)
    if result is None:
        return None
    factor, index = result
    while True:
        peek = None if index > len(t) else t[index]
        match peek:
            case lexer.TkIncrement():
                factor, index = Postfix(True, factor), index+1
            case lexer.TkDecrement():
                factor, index = Postfix(False, factor), index+1
            case _:
                break
    return factor, index


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
        case lexer.TkPercent():
            return Bin_Op.REMAINDER, index+1
        case lexer.TkLShift():
            return Bin_Op.LEFT_SHIFT, index+1
        case lexer.TkRShift():
            return Bin_Op.RIGHT_SHIFT, index+1
        case lexer.TkBAnd():
            return Bin_Op.BIT_AND, index+1
        case lexer.TkBOr():
            return Bin_Op.BIT_OR, index+1
        case lexer.TkXor():
            return Bin_Op.XOR, index+1
        case lexer.TkLAnd():
            return Bin_Op.LOG_AND, index+1
        case lexer.TkLOr():
            return Bin_Op.LOG_OR, index+1
        case lexer.TkEqual():
            return Bin_Op.ASSIGN, index+1
        case lexer.TkDEqual():
            return Bin_Op.EQUAL, index+1
        case lexer.TkNotEqual():
            return Bin_Op.NOT_EQUAL, index+1
        case lexer.TkLessThan():
            return Bin_Op.LESS_THAN, index+1
        case lexer.TkLessEqual():
            return Bin_Op.LESS_EQUAL, index+1
        case lexer.TkGreaterThan():
            return Bin_Op.GREATER_THAN, index+1
        case lexer.TkGreaterEqual():
            return Bin_Op.GREATER_EQUAL, index+1
        case lexer.TkPlusEqual():
            return Bin_Op.ADD_ASSIGN, index+1
        case lexer.TkSubEqual():
            return Bin_Op.SUB_ASSIGN, index+1
        case lexer.TkMulEqual():
            return Bin_Op.MUL_ASSIGN, index+1
        case lexer.TkDivEqual():
            return Bin_Op.DIV_ASSIGN, index+1
        case lexer.TkModEqual():
            return Bin_Op.MOD_ASSIGN, index+1
        case lexer.TkBAndEqual():
            return Bin_Op.BAND_ASSIGN, index+1
        case lexer.TkBOrEqual():
            return Bin_Op.BOR_ASSIGN, index+1
        case lexer.TkXorEqual():
            return Bin_Op.XOR_ASSIGN, index+1
        case lexer.TkLSEqual():
            return Bin_Op.LS_ASSIGN, index+1
        case lexer.TkRSEqual():
            return Bin_Op.RS_ASSIGN, index+1
        case _:
            return None


def parse_cond_middle(t: list[lexer.Token],
                      index: int) -> tuple[Expression, int] | None:
    if not expect_tk(lexer.TkQuestion, t, index):
        return None
    index += 1
    exp_result = parse_expr(t, index)
    if exp_result is None:
        return None
    exp, index = exp_result
    if not expect_tk(lexer.TkColon, t, index):
        return None
    return exp, index+1


def parse_expr(t: list[lexer.Token],
               index: int,
               min_prec: int = 0) -> tuple[Expression, int] | None:
    if (index >= len(t)):
        return None
    result = parse_factor(t, index)
    if result is None:
        return None
    left, index = result
    peek = None if index > len(t) else t[index]
    while (prec := precedence(peek)) is not None and prec >= min_prec:
        match peek:
            case lexer.TkEqual():
                index = index + 1
                right_result = parse_expr(t, index, prec)
                if right_result is None:
                    return None
                right, index = right_result
                left = Assignment(left, right)
            case (lexer.TkPlusEqual()
                  | lexer.TkSubEqual()
                  | lexer.TkMulEqual()
                  | lexer.TkDivEqual()
                  | lexer.TkModEqual()
                  | lexer.TkBAndEqual()
                  | lexer.TkBOrEqual()
                  | lexer.TkXorEqual()
                  | lexer.TkLSEqual()
                  | lexer.TkRSEqual()):
                binop_result = parse_binop(t, index)
                if binop_result is None:
                    return None
                binop, index = binop_result
                right_result = parse_expr(t, index, prec)
                if right_result is None:
                    return None
                right, index = right_result
                left = CompoundAssign(binop, left, right)
            case lexer.TkQuestion():
                middle_result = parse_cond_middle(t, index)
                if middle_result is None:
                    return None
                middle, index = middle_result
                exp_result = parse_expr(t, index, prec)
                if exp_result is None:
                    return None
                right, index = exp_result
                left = Conditional(left, middle, right)
            case _:
                binop_result = parse_binop(t, index)
                if binop_result is None:
                    return None
                binop, index = binop_result
                result = parse_expr(t, index, prec+1)
                if result is None:
                    return None
                right, index = result
                left = Binary(binop, left, right)
        peek = None if index > len(t) else t[index]
    return left, index


def parse_block(t: list[lexer.Token],
                index: int) -> tuple[Block, int] | None:
    if not expect_tk(lexer.TkOpenBrace, t, index):
        return None
    index += 1
    body: list[Block_Item] = list()
    while (b_result := parse_block_item(t, index)) is not None:
        item, index = b_result
        body.append(item)
    if not expect_tk(lexer.TkCloseBrace, t, index):
        return None
    return Block(body), index+1


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
                lexer.TkCloseParenthesis)

    for kind in TK_CHUNK:
        if not expect_tk(kind, t, index):
            return None
        else:
            index += 1

    body_result = parse_block(t, index)
    if body_result is None:
        return None
    body, index = body_result
    return (Function(r_ident[0], body), index)


def parse_program(t: list[lexer.Token],
                  index: int) -> Program | None:
    ret = parse_function(t, index)
    if (ret is None):
        return None
    func, num = ret
    if num < len(t):
        return None
    return Program(func)
