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
    CX = auto()
    DX = auto()
    R10 = auto()
    R11 = auto()


class Size(Enum):
    B = auto()
    W = auto()
    L = auto()
    Q = auto()


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
    size: Size
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
    AND = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()
    OR = auto()
    XOR = auto()


@dataclass
class Unary:
    unary_operator: Unary_Operator
    size: Size
    operand: Operand


@dataclass
class Binary:
    binary_operator: Bin_Op
    size: Size
    left: Operand
    right: Operand


@dataclass
class Cmp:
    size: Size
    left: Operand
    right: Operand


@dataclass
class Idiv:
    size: Size
    operand: Operand


@dataclass
class Cdq:
    pass


@dataclass
class Jmp:
    identifier: str


class Cond_Code(Enum):
    E = auto()
    NE = auto()
    G = auto()
    GE = auto()
    L = auto()
    LE = auto()


@dataclass
class JmpCC:
    cond_code: Cond_Code
    identifier: str


@dataclass
class SetCC:
    cond_code: Cond_Code
    operand: Operand


@dataclass
class Label:
    identifier: str


Instruction = (Mov
               | Allocate_Stack
               | Unary
               | Ret
               | Binary
               | Cmp
               | Cdq
               | Idiv
               | Jmp
               | JmpCC
               | SetCC
               | Label)


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
        case tacky.Bin_Op.LEFT_SHIFT:
            return Bin_Op.LEFT_SHIFT
        case tacky.Bin_Op.RIGHT_SHIFT:
            return Bin_Op.RIGHT_SHIFT
        case tacky.Bin_Op.BITW_AND:
            return Bin_Op.AND
        case tacky.Bin_Op.BITW_OR:
            return Bin_Op.OR
        case tacky.Bin_Op.XOR:
            return Bin_Op.XOR
        case _:
            raise RuntimeError(f'Unhandled unary operator {node}')


def convert_tacky_relational(node: tacky.Bin_Op) -> Cond_Code:
    match node:
        case tacky.Bin_Op.EQUAL:
            return Cond_Code.E
        case tacky.Bin_Op.NOT_EQUAL:
            return Cond_Code.NE
        case tacky.Bin_Op.GREATER_THAN:
            return Cond_Code.G
        case tacky.Bin_Op.GREATER_EQUAL:
            return Cond_Code.GE
        case tacky.Bin_Op.LESS_THAN:
            return Cond_Code.L
        case tacky.Bin_Op.LESS_EQUAL:
            return Cond_Code.LE
        case _:
            raise RuntimeError(f'Unhandled relational operator {node}')


def convert_tacky_instr(node: tacky.Instruction) -> tuple[Instruction, ...]:
    match node:
        case tacky.Return(val):
            src = convert_tacky_val(val)
            return (Mov(Size.L, src, Register(Register_Enum.AX)), Ret())
        case tacky.Unary(operator, src, dst):
            asm_src = convert_tacky_val(src)
            asm_dst = convert_tacky_val(dst)
            match operator:
                case tacky.Unary_Operator.NOT:
                    return (Cmp(Size.L, Imm(0), asm_src),
                            Mov(Size.L, Imm(0), asm_dst),
                            SetCC(Cond_Code.E, asm_dst))
                case _:
                    asm_op = convert_tacky_uop(operator)
                    return (Mov(Size.L, asm_src, asm_dst),
                            Unary(asm_op, Size.L, asm_dst))
        case tacky.Binary(operator, src1, src2, dst):
            asm_src1 = convert_tacky_val(src1)
            asm_src2 = convert_tacky_val(src2)
            asm_dst = convert_tacky_val(dst)
            match operator:
                case tacky.Bin_Op.DIVIDE:
                    return (Mov(Size.L, asm_src1, Register(Register_Enum.AX)),
                            Cdq(),
                            Idiv(Size.L, asm_src2),
                            Mov(Size.L, Register(Register_Enum.AX), asm_dst))
                case tacky.Bin_Op.REMAINDER:
                    return (Mov(Size.L, asm_src1, Register(Register_Enum.AX)),
                            Cdq(),
                            Idiv(Size.L, asm_src2),
                            Mov(Size.L, Register(Register_Enum.DX), asm_dst))
                case (tacky.Bin_Op.GREATER_THAN
                      | tacky.Bin_Op.GREATER_EQUAL
                      | tacky.Bin_Op.LESS_THAN
                      | tacky.Bin_Op.LESS_EQUAL
                      | tacky.Bin_Op.EQUAL
                      | tacky.Bin_Op.NOT_EQUAL):
                    asm_cc = convert_tacky_relational(operator)
                    return (Cmp(Size.L, asm_src2, asm_src1),
                            Mov(Size.L, Imm(0), asm_dst),
                            SetCC(asm_cc, asm_dst))
                case _:
                    asm_bop = convert_tacky_bop(operator)
                    return (Mov(Size.L, asm_src1, asm_dst),
                            Binary(asm_bop, Size.L, asm_src2, asm_dst))
        case tacky.Jump(target):
            return (Jmp(target),)
        case tacky.JumpIfZero(condtion, target):
            asm_condition = convert_tacky_val(condtion)
            return ((Cmp(Size.L, Imm(0), asm_condition)),
                    JmpCC(Cond_Code.E, target))
        case tacky.JumpIfNotZero(condition, target):
            asm_condition = convert_tacky_val(condition)
            return ((Cmp(Size.L, Imm(0), asm_condition)),
                    JmpCC(Cond_Code.NE, target))
        case tacky.Copy(src, dst):
            asm_src = convert_tacky_val(src)
            asm_dst = convert_tacky_val(dst)
            return (Mov(Size.L, asm_src, asm_dst),)
        case tacky.Label(identifier):
            return (Label(identifier),)
        case _:
            raise RuntimeError(f'Unhandled Instruction {node}')


def convert_tacky_function(node: tacky.Function) -> Function:
    match node:
        case tacky.Function(name, instr):
            asm_instr = [x for y in instr for x in convert_tacky_instr(y)]
            print('Checking function conversion')
            for x in asm_instr:
                print(x)
            print('End Checking function conversion')
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
            case Mov(size, src, dst):
                new_src = replace_operand(src)
                new_dst = replace_operand(dst)
                modified_instr.append(Mov(size, new_src, new_dst))
            case Unary(operator, size, dst):
                new_dst = replace_operand(dst)
                modified_instr.append(Unary(operator, size, new_dst))
            case Binary(operator, size, left, right):
                new_left = replace_operand(left)
                new_right = replace_operand(right)
                modified_instr.append(
                    Binary(operator, size, new_left, new_right))
            case Idiv(size, operand):
                new_operand = replace_operand(operand)
                modified_instr.append(Idiv(size, new_operand))
            case Cmp(size, left, right):
                new_left = replace_operand(left)
                new_right = replace_operand(right)
                modified_instr.append(Cmp(size, new_left, new_right))
            case _:
                modified_instr.append(instr)

    func.instructions = modified_instr
    return counter


def instruction_fixup(func: Function, alloc_count: int) -> None:
    """Mov can't have mem address as both src and dst"""
    modified_instr: list[Instruction] = [Allocate_Stack(alloc_count)]

    for instr in func.instructions:
        match instr:
            case Mov(size, Stack(a), Stack(b)):
                # Currently using %R10 as a scratch register
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(size, Stack(a), scratch))
                modified_instr.append(Mov(size, scratch, Stack(b)))
            case Binary(Bin_Op.ADD, size, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(size, Stack(a), scratch))
                modified_instr.append(
                    Binary(Bin_Op.ADD, size, scratch, Stack(b)))
            case Binary(Bin_Op.SUB, size, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(size, Stack(a), scratch))
                modified_instr.append(
                    Binary(Bin_Op.SUB, size, scratch, Stack(b)))
            case Binary(Bin_Op.MULT, size, src, Stack(a)):
                # imul can't use a memory address as a dst
                scratch = Register(Register_Enum.R11)
                modified_instr.append(Mov(size, Stack(a), scratch))
                modified_instr.append(Binary(Bin_Op.MULT, size, src, scratch))
                modified_instr.append(Mov(size, scratch, Stack(a)))
            case Binary(Bin_Op.AND, size, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(size, Stack(a), scratch))
                modified_instr.append(
                    Binary(Bin_Op.AND, size, scratch, Stack(b)))
            case Binary(Bin_Op.OR, size, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(size, Stack(a), scratch))
                modified_instr.append(
                    Binary(Bin_Op.OR, size, scratch, Stack(b)))
            case Binary(Bin_Op.XOR, size, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(size, Stack(a), scratch))
                modified_instr.append(
                    Binary(Bin_Op.XOR, size, scratch, Stack(b)))
            case Binary(Bin_Op.RIGHT_SHIFT, size, Stack() as op1, op2):
                scratch = Register(Register_Enum.CX)
                cl = Register(Register_Enum.CX)
                modified_instr.extend(
                    (Mov(size, op1, scratch),
                     Binary(Bin_Op.RIGHT_SHIFT, size, cl, op2)))
            case Binary(Bin_Op.LEFT_SHIFT, size, Stack() as op1, op2):
                scratch = Register(Register_Enum.CX)
                cl = Register(Register_Enum.CX)
                modified_instr.extend(
                    (Mov(size, op1, scratch),
                     Binary(Bin_Op.LEFT_SHIFT, size, cl, op2)))
            case Cmp(size, Stack() as left, Stack() as right):
                scratch = Register(Register_Enum.R10)
                modified_instr.extend((Mov(size, left, scratch),
                                       Cmp(size, scratch, right)))
            case Cmp(size, left, Imm() as right):
                scratch = Register(Register_Enum.R11)
                modified_instr.extend((Mov(size, right, scratch),
                                       Cmp(size, left, scratch)))
            case Idiv(size, Imm(a)):
                # idiv can't use an immediate as an operand
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(size, Imm(a), scratch))
                modified_instr.append(Idiv(size, scratch))
            case _:
                modified_instr.append(instr)
    func.instructions = modified_instr


def emit_asm_ast(node: tacky.Program) -> Program:
    asm_ast = convert_tacky(node)
    blah = replace_psuedo(asm_ast.function_definition)
    instruction_fixup(asm_ast.function_definition, blah)
    return asm_ast
