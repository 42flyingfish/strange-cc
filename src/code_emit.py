import asm


def process_node(x) -> list[str]:
    result: list[str] = []
    match x:
        case asm.Program():
            result.extend(process_node(x.function_definition))
            result.append('.section .note.GNU-stack,"",@progbits\n')
        case asm.Function(name, instructions):
            result.append(f'.global {name}\n')
            result.append(f'{name}:\n')
            for instruction in instructions:
                result.extend(process_node(instruction))
        case asm.Mov():
            result.append('# mov instruction stub\n')
        case asm.Ret():
            result.append('\tRET\n')
        case _:
            result.append('ERROR DETECTED\n')
    return result
