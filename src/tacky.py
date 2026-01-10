import parser
from dataclasses import dataclass
from enum import Enum, auto
from itertools import count

from utility import Identifier

# Nasty Global for use below
counter = count()


def make_temporary(prefix='tmp') -> Identifier:
    return Identifier(f'{prefix}{next(counter)}')


class Unary_Operator(Enum):
    COMPLEMENT = auto()
    NEGATION = auto()
    NOT = auto()


class Bin_Op(Enum):
    """Binary Operators"""
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    REMAINDER = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()
    BITW_AND = auto()
    BITW_OR = auto()
    XOR = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_THAN = auto()
    GREATER_EQUAL = auto()


@dataclass
class Constant:
    x: int


@dataclass
class Var:
    identifier: Identifier


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


@dataclass
class Copy:
    src: Val
    dst: Val


@dataclass
class Jump:
    target: Identifier


@dataclass
class JumpIfZero:
    condition: Val
    target: Identifier


@dataclass
class JumpIfNotZero:
    condition: Val
    target: Identifier


@dataclass
class Label:
    identifier: Identifier


Instruction = (Return
               | Unary
               | Binary
               | Copy
               | Jump
               | JumpIfZero
               | JumpIfNotZero
               | Label)


@dataclass
class Function:
    identifier: Identifier
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
        case parser.Unary_Operator.NOT:
            return Unary_Operator.NOT
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
        case parser.Bin_Op.LEFT_SHIFT:
            return Bin_Op.LEFT_SHIFT
        case parser.Bin_Op.RIGHT_SHIFT:
            return Bin_Op.RIGHT_SHIFT
        case parser.Bin_Op.BIT_AND:
            return Bin_Op.BITW_AND
        case parser.Bin_Op.BIT_OR:
            return Bin_Op.BITW_OR
        case parser.Bin_Op.XOR:
            return Bin_Op.XOR
        case parser.Bin_Op.EQUAL:
            return Bin_Op.EQUAL
        case parser.Bin_Op.NOT_EQUAL:
            return Bin_Op.NOT_EQUAL
        case parser.Bin_Op.LESS_THAN:
            return Bin_Op.LESS_THAN
        case parser.Bin_Op.LESS_EQUAL:
            return Bin_Op.LESS_EQUAL
        case parser.Bin_Op.GREATER_THAN:
            return Bin_Op.GREATER_THAN
        case parser.Bin_Op.GREATER_EQUAL:
            return Bin_Op.GREATER_EQUAL
        case _:
            raise RuntimeError(f'Unexpected binary operator {node}')


def emit_tacky(node, instructions: list[Instruction]) -> Val:
    match node:
        case parser.Constant(x):
            return Constant(x=int(x))
        case parser.Unary(parser.Unary_Operator.INCREMENT, a):
            tacky_dst = emit_tacky(a, instructions)
            node = Binary(Bin_Op.ADD, tacky_dst, Constant(1), tacky_dst)
            instructions.append(node)
            return tacky_dst
        case parser.Unary(parser.Unary_Operator.DECREMENT, a):
            tacky_dst = emit_tacky(a, instructions)
            node = Binary(Bin_Op.SUBTRACT, tacky_dst, Constant(1), tacky_dst)
            instructions.append(node)
            return tacky_dst
        case parser.Unary(op, operand):
            tacky_op = convert_unop(op)
            src = emit_tacky(operand, instructions)
            dst = Var(make_temporary())
            instructions.append(Unary(tacky_op, src, dst))
            return dst
        case parser.Binary(parser.Bin_Op.LOG_AND, a, b):
            result = Var(make_temporary('and_result'))
            false_label = make_temporary('and_false')
            end_label = make_temporary('and_end')
            left = emit_tacky(a, instructions)
            instructions.append(JumpIfZero(left, false_label))
            right = emit_tacky(b, instructions)
            instructions.extend((JumpIfZero(right, false_label),
                                 Copy(Constant(1), result),
                                 Jump(end_label),
                                 Label(false_label),
                                 Copy(Constant(0), result),
                                 Label(end_label)))
            return result
        case parser.Binary(parser.Bin_Op.LOG_OR, a, b):
            result = Var(make_temporary('or_result'))
            true_label = make_temporary('or_true')
            end_label = make_temporary('or_end')
            left = emit_tacky(a, instructions)
            instructions.append(JumpIfNotZero(left, true_label))
            right = emit_tacky(b, instructions)
            instructions.extend((JumpIfNotZero(right, true_label),
                                 Copy(Constant(0), result),
                                 Jump(end_label),
                                 Label(true_label),
                                 Copy(Constant(1), result),
                                 Label(end_label)))
            return result
        case parser.Binary(op, left, right):
            bin_op = convert_binop(op)
            v1 = emit_tacky(left, instructions)
            v2 = emit_tacky(right, instructions)
            dst_name = make_temporary()
            dst = Var(dst_name)
            instructions.append(Binary(bin_op, v1, v2, dst))
            return dst
        case parser.Var(id):
            return Var(id)
        case parser.Assignment(parser.Var(id), right):
            r = emit_tacky(right, instructions)
            instructions.append(Copy(r, Var(id)))
            return Var(id)
        case parser.CompoundAssign(bop, l, r):
            table = {parser.Bin_Op.ADD_ASSIGN: parser.Bin_Op.ADD,
                     parser.Bin_Op.SUB_ASSIGN: parser.Bin_Op.SUBTRACT,
                     parser.Bin_Op.MUL_ASSIGN: parser.Bin_Op.MULTIPLY,
                     parser.Bin_Op.DIV_ASSIGN: parser.Bin_Op.DIVIDE,
                     parser.Bin_Op.MOD_ASSIGN: parser.Bin_Op.REMAINDER,
                     parser.Bin_Op.BAND_ASSIGN: parser.Bin_Op.BIT_AND,
                     parser.Bin_Op.BOR_ASSIGN: parser.Bin_Op.BIT_OR,
                     parser.Bin_Op.XOR_ASSIGN: parser.Bin_Op.XOR,
                     parser.Bin_Op.LS_ASSIGN: parser.Bin_Op.LEFT_SHIFT,
                     parser.Bin_Op.RS_ASSIGN: parser.Bin_Op.RIGHT_SHIFT}
            bop2 = table[bop]
            return emit_tacky(parser.Assignment(l, parser.Binary(bop2, l, r)),
                              instructions)
        case parser.DeclareNode(name, init):
            if init is None:
                # This should be discarded
                return Var(name)
            r = emit_tacky(init, instructions)
            instructions.append(Copy(r, Var(name)))
            return Var(name)
        case parser.D(decl):
            return emit_tacky(decl, instructions)
        case parser.S(statement):
            return emit_tacky(statement, instructions)
        case parser.ExpNode(exp):
            return emit_tacky(exp, instructions)
        case parser.Null():
            # This too should be discarded
            return Var(Identifier('Null'))
        case parser.Return(exp):
            inner = emit_tacky(exp, instructions)
            instructions.append(Return(inner))
            return inner
        case parser.Postfix(True, exp):
            tmp = Var(make_temporary('postfix_inc'))
            src = emit_tacky(exp, instructions)
            instructions.extend((Copy(src, tmp),
                                 Binary(Bin_Op.ADD, src, Constant(1), src)))
            return tmp
        case parser.Postfix(False, exp):
            tmp = Var(make_temporary('postfix_dec'))
            src = emit_tacky(exp, instructions)
            instructions.extend((Copy(src, tmp),
                                 Binary(Bin_Op.SUBTRACT,
                                        src, Constant(1), src)))
            return tmp
        case _:
            raise RuntimeError(f'Uhandled Expression {node}')


def emit_tacky_function(node: parser.Function) -> Function:
    match node:
        case parser.Function(name, body):
            arr: list[Instruction] = []
            for instr in body:
                emit_tacky(instr, arr)
            # To handle functions without returns
            # Append this extra return 0
            arr.append(Return(Constant(0)))
            return Function(name, arr)
        case _:
            raise RuntimeError(f'Non function node passed {node}')


def emit_tack_program(node: parser.Program) -> Program:
    match node:
        case parser.Program(func):
            return Program(emit_tacky_function(func))
        case _:
            raise RuntimeError(f'Non program node passed {node}')
