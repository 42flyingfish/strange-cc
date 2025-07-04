import asm


def decode_op(x) -> str:
    match x:
        case asm.Imm(val):
            return f'${val}'
        case asm.Register():
            return '%eax'


def process_node(x) -> list[str]:
    result: list[str] = []
    match x:
        case asm.Program():
            result.extend(process_node(x.function_definition))
            result.append('.section .note.GNU-stack,"",@progbits\n')
        case asm.Function(name, instructions):
            result.append(f'\t.global {name}\n')
            result.append(f'{name}:\n')
            for instruction in instructions:
                result.extend(process_node(instruction))
        case asm.Mov(src, dst):
            result.append(f'\tmovl {decode_op(src)}, {decode_op(dst)}\n')
        case asm.Ret():
            result.append('\tret\n')
        case _:
            result.append('ERROR DETECTED\n')
    return result
