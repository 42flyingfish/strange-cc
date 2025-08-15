from collections.abc import Iterable
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
    R10 = auto()


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


@dataclass
class Unary:
    unary_operator: Unary_Operator
    operand: Operand


Instruction = Mov | Allocate_Stack | Unary | Ret


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


def convert_tacky_instr(node: tacky.Instruction) -> Iterable[Instruction]:
    match node:
        case tacky.Return(val):
            src = convert_tacky_val(val)
            return (Mov(src, Register(Register_Enum.AX)), Ret())
        case tacky.Unary(unary_operator, src, dst):
            asm_src = convert_tacky_val(src)
            asm_dst = convert_tacky_val(dst)
            asm_op = convert_tacky_uop(unary_operator)
            return (Mov(asm_src, asm_dst), Unary(asm_op, asm_dst))
        case _:
            raise RuntimeError(f'Unhandled Instruction {node}')


def convert_tacky(node) -> Program | Function:
    match node:
        case tacky.Program(func):
            return Program(convert_tacky(func))
        case tacky.Function(name, instr):
            asm_instr = [x for y in instr for x in convert_tacky_instr(y)]
            return Function(name, asm_instr)
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
            case _:
                modified_instr.append(instr)
    func.instructions = modified_instr


def emit_asm_ast(node: tacky.Program) -> Program:
    asm_ast = convert_tacky(node)
    blah = replace_psuedo(asm_ast.function_definition)
    instruction_fixup(asm_ast.function_definition, blah)
    return asm_ast
