#! /bin/python
import argparse
import os
import lexer
import parser as p
import asm
import code_emit
import subprocess


def handle_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument('--lex', action='store_true')
    group.add_argument('--parse', action='store_true')
    group.add_argument('--codegen', action='store_true')

    parser.add_argument('filepath', type=str)

    args = parser.parse_args()

    if not os.path.isfile(args.filepath):
        print(f'File not found {args.filepath}')
        return

    lex_result = lexer.tokenize_file(args.filepath)
    if args.lex:
        return
    x = p.parse_program(lex_result, 0)
    if x is None:
        raise ValueError('Failed to parse a program')
    if args.parse:
        return
    ast_asm = asm.parse_program(x)
    if args.codegen:
        return
    blah = code_emit.process_node(ast_asm)
    directory = os.path.dirname(args.filepath)
    filename = os.path.splitext(os.path.basename(args.filepath))[0]
    asm_file_output = f'{filename}.s'
    asm_file_output = os.path.join(directory, f'{filename}.s')
    bin_file_output = os.path.join(directory, filename)

    with open(asm_file_output, 'w') as output:
        output.writelines(blah)

    gcc_command = ['gcc', '-o', bin_file_output, asm_file_output]

    compile_result = subprocess.run(gcc_command,
                                    capture_output=True,
                                    text=True)

    if compile_result.returncode != 0:
        print(f"GCC failed to compile {asm_file_output}: {compile_result.stderr}")


if __name__ == '__main__':
    handle_args()
