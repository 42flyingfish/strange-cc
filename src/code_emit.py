from collections.abc import Generator

import asm


def decode_operand(x) -> str:
    match x:
        case asm.Imm(val):
            return f'${val}'
        case asm.Register(asm.Register_Enum.AX):
            return '%eax'
        case asm.Register(asm.Register_Enum.CX):
            return '%ecx'
        case asm.Register(asm.Register_Enum.DX):
            return '%edx'
        case asm.Register(asm.Register_Enum.CL):
            return '%cl'
        case asm.Register(asm.Register_Enum.R10):
            return '%r10d'
        case asm.Register(asm.Register_Enum.R11):
            return '%r11d'
        case asm.Stack(offset):
            return f'-{offset}(%rbp)'
        case _:
            raise RuntimeError(f'Unhandled op {x}')


def decode_operator(x) -> str:
    match x:
        case asm.Unary_Operator.NEGATION:
            return 'negl'
        case asm.Unary_Operator.COMPLEMENT:
            return 'notl'
        case asm.Bin_Op.ADD:
            return 'addl'
        case asm.Bin_Op.SUB:
            return 'subl'
        case asm.Bin_Op.MULT:
            return 'imull'
        case asm.Bin_Op.LEFT_SHIFT:
            return 'sall'
        case asm.Bin_Op.RIGHT_SHIFT:
            return 'sarl'
        case asm.Bin_Op.AND:
            return 'andl'
        case asm.Bin_Op.OR:
            return 'orl'
        case asm.Bin_Op.XOR:
            return 'xorl'
        case _:
            raise RuntimeError(f'Unhandled op {x}')


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
