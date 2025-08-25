import parser
from dataclasses import dataclass
from enum import Enum, auto
from itertools import count

# Nasty Global for use below
counter = count()


def make_temporary() -> str:
    return f'tmp.{next(counter)}'


class Unary_Operator(Enum):
    COMPLEMENT = auto()
    NEGATION = auto()


class Bin_Op(Enum):
    """Binary Operators"""
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    REMAINDER = auto()


@dataclass
class Constant:
    x: int


@dataclass
class Var:
    identifier: str


Val = Constant | Var


@dataclass
class Return:
    val: Val


@dataclass
class Unary:
    unary_operator: Unary_Operator
    src: Val
    dst: Val


@dataclass
class Binary:
    bin_op: Bin_Op
    src1: Val
    src2: Val
    dst: Val


Instruction = Return | Unary


@dataclass
class Function:
    identifier: str
    body: list[Instruction]


@dataclass
class Program:
    function_definition: Function


Tacky = Val | Instruction | Function | Program


def convert_unop(node) -> Unary_Operator:
    """Helper function to decode the operator
       I am currently undecided if the operators
       Should be seperately defined or shared
    """
    match node:
        case parser.Unary_Operator.COMPLEMENT:
            return Unary_Operator.COMPLEMENT
        case parser.Unary_Operator.NEGATION:
            return Unary_Operator.NEGATION
        case _:
            raise RuntimeError(f'Unexpected unary operator {node}')


def convert_binop(node) -> Bin_Op:
    match node:
        case parser.Bin_Op.ADD:
            return Bin_Op.ADD
        case parser.Bin_Op.SUBTRACT:
            return Bin_Op.SUBTRACT
        case parser.Bin_Op.DIVIDE:
            return Bin_Op.DIVIDE
        case parser.Bin_Op.MULTIPLY:
            return Bin_Op.MULTIPLY
        case parser.Bin_Op.REMAINDER:
            return Bin_Op.REMAINDER
        case _:
            raise RuntimeError(f'Unexpected binary operator {node}')


def emit_tacky(node, instructions: list[Instruction]) -> Val:
    match node:
        case parser.Constant(x):
            return Constant(x=int(x))
        case parser.Unary(op, operand):
            tacky_op = convert_unop(op)
            src = emit_tacky(operand, instructions)
            dst = Var(make_temporary())
            instructions.append(Unary(tacky_op, src, dst))
            return dst
        case parser.Binary(op, left, right):
            tacky_op = convert_binop(op)
            v1 = emit_tacky(left, instructions)
            v2 = emit_tacky(right, instructions)
            dst_name = make_temporary()
            dst = Var(dst_name)
            instructions.append(Binary(tacky_op, v1, v2, dst))
            return dst
        case _:
            raise RuntimeError(f'Uhandled Expression {node}')


def emit_tacky_return(node, instructions: list[Instruction]) -> None:
    match node:
        case parser.Return(exp):
            inner = emit_tacky(exp, instructions)
            instructions.append(Return(inner))
        case _:
            raise RuntimeError(f'Non return node passed {node}')


def emit_tacky_function(node: parser.Function) -> Function:
    match node:
        case parser.Function(name, body):
            arr: list[Instruction] = []
            emit_tacky_return(body, arr)
            return Function(name.val, arr)
        case _:
            raise RuntimeError(f'Non function node passed {node}')


def emit_tack_program(node: parser.Program) -> Program:
    match node:
        case parser.Program(func):
            return Program(emit_tacky_function(func))
        case _:
            raise RuntimeError(f'Non program node passed {node}')
