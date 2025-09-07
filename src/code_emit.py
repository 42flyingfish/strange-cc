import asm


def decode_operand(x) -> str:
    match x:
        case asm.Imm(val):
            return f'${val}'
        case asm.Register(asm.Register_Enum.AX):
            return '%eax'
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
        case _:
            raise RuntimeError(f'Unhandled op {x}')


def process_node(x) -> list[str]:
    match x:
        case asm.Program():
            result = process_node(x.function_definition)
            result.append('.section .note.GNU-stack,"",@progbits\n')
            return result
        case asm.Function(name, instructions):
            result = [f'\t.global {name}\n',
                      f'{name}:\n',
                      '\tpushq %rbp\n',
                      '\tmovq %rsp, %rbp\n']
            for instruction in instructions:
                result.extend(process_node(instruction))
            return result
        case asm.Mov(src, dst):
            return [f'\tmovl {decode_operand(src)}, {decode_operand(dst)}\n']
        case asm.Ret():
            return ['\tmovq %rbp, %rsp\n',
                    '\tpopq %rbp\n',
                    '\tret\n']
        case asm.Unary(operator, dst):
            return [f'\t{decode_operator(operator)} {decode_operand(dst)}\n']
        case asm.Binary(operator, left, right):
            op1 = decode_operand(left)
            op2 = decode_operand(right)
            return [f'\t{decode_operator(operator)} {op1}, {op2}\n']
        case asm.Idiv(operand):
            return [f'\tidivl {decode_operand(operand)}\n']
        case asm.Cdq():
            return ['\tcdq\n']
        case asm.Allocate_Stack(0):
            return ['# \t No stack allocation \n']
        case asm.Allocate_Stack(offset):
            return [f'\tsubq ${offset}, %rsp\n']
        case _:
            raise RuntimeError(f'Unandled instruction {x}')
