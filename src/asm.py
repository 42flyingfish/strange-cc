from dataclasses import dataclass
from enum import Enum, auto

import tacky


@dataclass(frozen=True)
class Pseudo():
    identifier: str


@dataclass
class Imm():
    val: int


class Register_Enum(Enum):
    AX = auto()
    DX = auto()
    R10 = auto()
    R11 = auto()


@dataclass
class Register():
    reg: Register_Enum


@dataclass
class Stack():
    val: int


Operand = Imm | Register | Pseudo | Stack


@dataclass
class Ret():
    pass


@dataclass
class Mov():
    src: Operand
    dst: Operand


@dataclass
class Allocate_Stack():
    offset: int


class Unary_Operator(Enum):
    COMPLEMENT = auto()
    NEGATION = auto()


class Bin_Op(Enum):
    ADD = auto()
    SUB = auto()
    MULT = auto()


@dataclass
class Unary:
    unary_operator: Unary_Operator
    operand: Operand


@dataclass
class Binary:
    binary_operator: Bin_Op
    left: Operand
    right: Operand


@dataclass
class Idiv:
    operand: Operand


@dataclass
class Cdq:
    pass


Instruction = Mov | Allocate_Stack | Unary | Ret | Binary | Cdq | Idiv


@dataclass
class Function():
    name: str
    instructions: list[Instruction]


@dataclass
class Program():
    function_definition: Function


def convert_tacky_val(node: tacky.Val) -> Imm | Pseudo:
    match node:
        case tacky.Constant(x):
            return Imm(x)
        case tacky.Var(x):
            return Pseudo(x)
        case _:
            raise RuntimeError(f'Unhandled return operand {node}')


def convert_tacky_uop(node: tacky.Unary_Operator) -> Unary_Operator:
    match node:
        case tacky.Unary_Operator.COMPLEMENT:
            return Unary_Operator.COMPLEMENT
        case tacky.Unary_Operator.NEGATION:
            return Unary_Operator.NEGATION
        case _:
            raise RuntimeError(f'Unhandled unary operator {node}')


def convert_tacky_bop(node: tacky.Bin_Op) -> Bin_Op:
    match node:
        case tacky.Bin_Op.ADD:
            return Bin_Op.ADD
        case tacky.Bin_Op.SUBTRACT:
            return Bin_Op.SUB
        case tacky.Bin_Op.MULTIPLY:
            return Bin_Op.MULT
        case _:
            raise RuntimeError(f'Unhandled unary operator {node}')


def convert_tacky_instr(node: tacky.Instruction) -> tuple[Instruction, ...]:
    match node:
        case tacky.Return(val):
            src = convert_tacky_val(val)
            return (Mov(src, Register(Register_Enum.AX)), Ret())
        case tacky.Unary(unary_operator, src, dst):
            asm_src = convert_tacky_val(src)
            asm_dst = convert_tacky_val(dst)
            asm_op = convert_tacky_uop(unary_operator)
            return (Mov(asm_src, asm_dst), Unary(asm_op, asm_dst))
        case tacky.Binary(tacky.Bin_Op.DIVIDE, src1, src2, dst):
            asm_src1 = convert_tacky_val(src1)
            asm_src2 = convert_tacky_val(src2)
            asm_dst = convert_tacky_val(dst)
            return (Mov(asm_src1, Register(Register_Enum.AX)),
                    Cdq(),
                    Idiv(asm_src2),
                    Mov(Register(Register_Enum.AX), asm_dst))
        case tacky.Binary(tacky.Bin_Op.REMAINDER, src1, src2, dst):
            asm_src1 = convert_tacky_val(src1)
            asm_src2 = convert_tacky_val(src2)
            asm_dst = convert_tacky_val(dst)
            return (Mov(asm_src1, Register(Register_Enum.AX)),
                    Cdq(),
                    Idiv(asm_src2),
                    Mov(Register(Register_Enum.DX), asm_dst))
        case tacky.Binary(operator, src1, src2, dst):
            asm_bop = convert_tacky_bop(operator)
            asm_src1 = convert_tacky_val(src1)
            asm_src2 = convert_tacky_val(src2)
            asm_dst = convert_tacky_val(dst)
            return (Mov(asm_src1, asm_dst),
                    Binary(asm_bop, asm_src2, asm_dst))
        case _:
            raise RuntimeError(f'Unhandled Instruction {node}')


def convert_tacky_function(node: tacky.Function) -> Function:
    match node:
        case tacky.Function(name, instr):
            asm_instr = [x for y in instr for x in convert_tacky_instr(y)]
            return Function(name, asm_instr)
        case _:
            raise RuntimeError(f'Unhandled node {node}')


def convert_tacky(node) -> Program:
    match node:
        case tacky.Program(func):
            return Program(convert_tacky_function(func))
        case _:
            raise RuntimeError(f'Unhandled node {node}')


def replace_psuedo(func: Function) -> int:
    """This pass replaces psuedo and returns stack allocation use"""
    counter = 0
    table: dict[Pseudo, Stack] = {}

    def replace_operand(op: Operand) -> Operand:
        nonlocal counter

        match op:
            case Pseudo():

                stack = table.get(op)
                if stack is not None:
                    return stack
                else:
                    # Incrementing by four for ints
                    counter += 4
                    val = Stack(counter)
                    table[op] = val
                    return val
            case _:
                return op

    modified_instr: list[Instruction] = []

    for instr in func.instructions:
        print(instr)
        match instr:
            case Mov(src, dst):
                new_src = replace_operand(src)
                new_dst = replace_operand(dst)
                modified_instr.append(Mov(new_src, new_dst))
            case Unary(operator, dst):
                new_dst = replace_operand(dst)
                modified_instr.append(Unary(operator, new_dst))
            case Binary(operator, left, right):
                new_left = replace_operand(left)
                new_right = replace_operand(right)
                modified_instr.append(Binary(operator, new_left, new_right))
            case Idiv(operand):
                new_operand = replace_operand(operand)
                modified_instr.append(Idiv(new_operand))
            case _:
                modified_instr.append(instr)

    func.instructions = modified_instr
    return counter


def instruction_fixup(func: Function, alloc_count: int) -> None:
    """Mov can't have mem address as both src and dst"""
    modified_instr: list[Instruction] = [Allocate_Stack(alloc_count)]

    for instr in func.instructions:
        match instr:
            case Mov(Stack(a), Stack(b)):
                # Currently using %R10 as a scratch register
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(Stack(a), scratch))
                modified_instr.append(Mov(scratch, Stack(b)))
            case Binary(Bin_Op.ADD, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(Stack(a), scratch))
                modified_instr.append(Binary(Bin_Op.ADD, scratch, Stack(b)))
            case Binary(Bin_Op.SUB, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(Stack(a), scratch))
                modified_instr.append(Binary(Bin_Op.SUB, scratch, Stack(b)))
            case Binary(Bin_Op.MULT, src, Stack(a)):
                # imul can't use a memory address as a dst
                scratch = Register(Register_Enum.R11)
                modified_instr.append(Mov(Stack(a), scratch))
                modified_instr.append(Binary(Bin_Op.MULT, src, scratch))
                modified_instr.append(Mov(scratch, Stack(a)))
            case Idiv(Imm(a)):
                # idiv can't use an immediate as an operand
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(Imm(a), scratch))
                modified_instr.append(Idiv(scratch))
            case _:
                modified_instr.append(instr)
    func.instructions = modified_instr


def emit_asm_ast(node: tacky.Program) -> Program:
    asm_ast = convert_tacky(node)
    blah = replace_psuedo(asm_ast.function_definition)
    instruction_fixup(asm_ast.function_definition, blah)
    return asm_ast
