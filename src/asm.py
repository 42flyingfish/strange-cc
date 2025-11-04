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
    CL = auto()
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
    AND = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()
    OR = auto()
    XOR = auto()


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
class Cmp:
    left: Operand
    right: Operand


@dataclass
class Idiv:
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
            return (Mov(src, Register(Register_Enum.AX)), Ret())
        case tacky.Unary(operator, src, dst):
            asm_src = convert_tacky_val(src)
            asm_dst = convert_tacky_val(dst)
            match operator:
                case tacky.Unary_Operator.NOT:
                    return (Cmp(Imm(0), asm_src),
                            Mov(Imm(0), asm_dst),
                            SetCC(Cond_Code.E, asm_dst))
                case _:
                    asm_op = convert_tacky_uop(operator)
                    return (Mov(asm_src, asm_dst), Unary(asm_op, asm_dst))
        case tacky.Binary(operator, src1, src2, dst):
            asm_src1 = convert_tacky_val(src1)
            asm_src2 = convert_tacky_val(src2)
            asm_dst = convert_tacky_val(dst)
            match operator:
                case tacky.Bin_Op.DIVIDE:
                    return (Mov(asm_src1, Register(Register_Enum.AX)),
                            Cdq(),
                            Idiv(asm_src2),
                            Mov(Register(Register_Enum.AX), asm_dst))
                case tacky.Bin_Op.REMAINDER:
                    return (Mov(asm_src1, Register(Register_Enum.AX)),
                            Cdq(),
                            Idiv(asm_src2),
                            Mov(Register(Register_Enum.DX), asm_dst))
                case (tacky.Bin_Op.GREATER_THAN
                      | tacky.Bin_Op.GREATER_EQUAL
                      | tacky.Bin_Op.LESS_THAN
                      | tacky.Bin_Op.LESS_EQUAL
                      | tacky.Bin_Op.EQUAL
                      | tacky.Bin_Op.NOT_EQUAL):
                    asm_cc = convert_tacky_relational(operator)
                    return (Cmp(asm_src2, asm_src1),
                            Mov(Imm(0), asm_dst),
                            SetCC(asm_cc, asm_dst))
                case _:
                    asm_bop = convert_tacky_bop(operator)
                    return (Mov(asm_src1, asm_dst),
                            Binary(asm_bop, asm_src2, asm_dst))
        case tacky.Jump(target):
            return (Jmp(target),)
        case tacky.JumpIfZero(condtion, target):
            asm_condition = convert_tacky_val(condtion)
            return ((Cmp(Imm(0), asm_condition)),
                    JmpCC(Cond_Code.E, target))
        case tacky.JumpIfNotZero(condition, target):
            asm_condition = convert_tacky_val(condition)
            return ((Cmp(Imm(0), asm_condition)),
                    JmpCC(Cond_Code.NE, target))
        case tacky.Copy(src, dst):
            asm_src = convert_tacky_val(src)
            asm_dst = convert_tacky_val(dst)
            return (Mov(asm_src, asm_dst),)
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
            case Cmp(left, right):
                new_left = replace_operand(left)
                new_right = replace_operand(right)
                modified_instr.append(Cmp(new_left, new_right))
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
            case Binary(Bin_Op.AND, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(Stack(a), scratch))
                modified_instr.append(Binary(Bin_Op.AND, scratch, Stack(b)))
            case Binary(Bin_Op.OR, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(Stack(a), scratch))
                modified_instr.append(Binary(Bin_Op.OR, scratch, Stack(b)))
            case Binary(Bin_Op.XOR, Stack(a), Stack(b)):
                scratch = Register(Register_Enum.R10)
                modified_instr.append(Mov(Stack(a), scratch))
                modified_instr.append(Binary(Bin_Op.XOR, scratch, Stack(b)))
            case Binary(Bin_Op.RIGHT_SHIFT, Stack() as op1, op2):
                scratch = Register(Register_Enum.CX)
                cl = Register(Register_Enum.CL)
                modified_instr.extend(
                    (Mov(op1, scratch),
                     Binary(Bin_Op.RIGHT_SHIFT, cl, op2)))
            case Binary(Bin_Op.LEFT_SHIFT, Stack() as op1, op2):
                scratch = Register(Register_Enum.CX)
                cl = Register(Register_Enum.CL)
                modified_instr.extend(
                    (Mov(op1, scratch),
                     Binary(Bin_Op.LEFT_SHIFT, cl, op2)))
            case Cmp(Stack() as left, Stack() as right):
                scratch = Register(Register_Enum.R10)
                modified_instr.extend((Mov(left, scratch),
                                       Cmp(scratch, right)))
            case Cmp(left, Imm() as right):
                scratch = Register(Register_Enum.R11)
                modified_instr.extend((Mov(right, scratch),
                                       Cmp(left, scratch)))
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
