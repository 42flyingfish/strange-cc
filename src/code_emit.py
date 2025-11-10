from collections.abc import Generator

import asm


def decode_suffix(x: asm.Size) -> str:
    match x:
        case asm.Size.B:
            return 'b'
        case asm.Size.W:
            return 'w'
        case asm.Size.L:
            return 'l'
        case asm.Size.Q:
            return 'q'
        case _:
            raise RuntimeError(f'Unhandled size{x}')


def decode_32_operand(x) -> str:
    match x:
        case asm.Imm(val):
            return f'${val}'
        case asm.Register(asm.Register_Enum.AX):
            return '%eax'
        case asm.Register(asm.Register_Enum.CX):
            return '%ecx'
        case asm.Register(asm.Register_Enum.DX):
            return '%edx'
        case asm.Register(asm.Register_Enum.R10):
            return '%r10d'
        case asm.Register(asm.Register_Enum.R11):
            return '%r11d'
        case asm.Stack(offset):
            return f'-{offset}(%rbp)'
        case _:
            raise RuntimeError(f'Unhandled op {x}')


def decode_8_operand(x) -> str:
    match x:
        case asm.Imm(val):
            return f'${val}'
        case asm.Register(asm.Register_Enum.AX):
            return '%al'
        case asm.Register(asm.Register_Enum.CX):
            return '%cl'
        case asm.Register(asm.Register_Enum.DX):
            return '%dl'
        case asm.Register(asm.Register_Enum.R10):
            return '%r10b'
        case asm.Register(asm.Register_Enum.R11):
            return '%r11b'
        case asm.Stack(offset):
            return f'-{offset}(%rbp)'
        case _:
            raise RuntimeError(f'Unhandled op {x}')


def decode_operator(x) -> str:
    match x:
        case asm.Unary_Operator.NEGATION:
            return 'neg'
        case asm.Unary_Operator.COMPLEMENT:
            return 'not'
        case asm.Bin_Op.ADD:
            return 'add'
        case asm.Bin_Op.SUB:
            return 'sub'
        case asm.Bin_Op.MULT:
            return 'imul'
        case asm.Bin_Op.LEFT_SHIFT:
            return 'sal'
        case asm.Bin_Op.RIGHT_SHIFT:
            return 'sar'
        case asm.Bin_Op.AND:
            return 'and'
        case asm.Bin_Op.OR:
            return 'or'
        case asm.Bin_Op.XOR:
            return 'xor'
        case _:
            raise RuntimeError(f'Unhandled op {x}')


def decode_operand(op: asm.Operand, size: asm.Size) -> str:
    match size:
        case asm.Size.B:
            return decode_8_operand(op)
        case asm.Size.L:
            return decode_32_operand(op)
        case _:
            raise RuntimeError(f'Unhandled size {size}')


def decode_cond_code(x: asm.Cond_Code) -> str:
    match x:
        case asm.Cond_Code.E:
            return 'e'
        case asm.Cond_Code.NE:
            return 'ne'
        case asm.Cond_Code.L:
            return 'l'
        case asm.Cond_Code.LE:
            return 'le'
        case asm.Cond_Code.G:
            return 'g'
        case asm.Cond_Code.GE:
            return 'ge'
        case _:
            raise RuntimeError(f'Unhandled cond_code {x}')


def process_node(x) -> Generator[str]:
    match x:
        case asm.Program():
            yield from process_node(x.function_definition)
            yield '.section .note.GNU-stack,"",@progbits\n'
        case asm.Function(name, instructions):
            yield f'\t.global {name}\n'
            yield f'{name}:\n'
            yield '\tpushq %rbp\n'
            yield '\tmovq %rsp, %rbp\n'
            for instruction in instructions:
                yield from process_node(instruction)
        case asm.Mov(src, dst):
            yield f'\tmovl {decode_operand(src)}, {decode_operand(dst)}\n'
        case asm.Ret():
            yield '\tmovq %rbp, %rsp\n'
            yield '\tpopq %rbp\n'
            yield '\tret\n'
        case asm.Unary(operator, dst):
            yield f'\t{decode_operator(operator)} {decode_operand(dst)}\n'
        case asm.Binary(operator, left, right):
            op1 = decode_operand(left)
            op2 = decode_operand(right)
            yield f'\t{decode_operator(operator)} {op1}, {op2}\n'
        case asm.Idiv(operand):
            yield f'\tidivl {decode_operand(operand)}\n'
        case asm.Cdq():
            yield '\tcdq\n'
        case asm.Allocate_Stack(0):
            yield '# \t No stack allocation \n'
        case asm.Allocate_Stack(offset):
            yield f'\tsubq ${offset}, %rsp\n'
        case _:
            raise RuntimeError(f'Unandled instruction {x}')
