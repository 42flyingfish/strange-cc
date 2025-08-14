#! /bin/python
import argparse
import os
import parser as p
import subprocess

import asm
import code_emit
import lexer
import tacky


def handle_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    group.add_argument('--lex', action='store_true')
    group.add_argument('--parse', action='store_true')
    group.add_argument('--codegen', action='store_true')
    group.add_argument('--tacky', action='store_true')

    parser.add_argument('filepath', type=str)

    args = parser.parse_args()

    if not os.path.isfile(args.filepath):
        print(f'File not found {args.filepath}')
        return

    file_basename = os.path.splitext(os.path.basename(args.filepath))[0]
    directory = os.path.dirname(args.filepath)
    preprocessed_file = f'{file_basename}.i'
    preprocessed_output = os.path.join(directory, preprocessed_file)

    gcc_command = ['gcc', '-E', '-P', args.filepath, '-o', preprocessed_output]

    result = subprocess.run(gcc_command,
                            capture_output=True,
                            text=True)

    if result.returncode != 0:
        err_msg = f'GCC failed to preprocess the file: {result.stderr}'
        raise RuntimeError(err_msg)

    lex_result = lexer.tokenize_file(preprocessed_output)
    if args.lex:
        return
    x = p.parse_program(lex_result, 0)
    if x is None:
        raise ValueError('Failed to parse a program')
    if args.parse:
        return
    # TODO make use of the TACKY Immediate Representation
    _ = tacky.emit_tack_program(x)
    if args.tacky:
        return
    ast_asm = asm.parse_program(x)
    if args.codegen:
        return
    blah = code_emit.process_node(ast_asm)
    asm_file_output = f'{file_basename}.s'
    asm_file_output = os.path.join(directory, f'{file_basename}.s')
    bin_file_output = os.path.join(directory, file_basename)

    with open(asm_file_output, 'w') as output:
        output.writelines(blah)

    gcc_command = ['gcc', '-o', bin_file_output, asm_file_output]

    result = subprocess.run(gcc_command,
                            capture_output=True,
                            text=True)

    if result.returncode != 0:
        err_msg = f'GCC failed to compile {asm_file_output}: {result.stderr}'
        raise RuntimeError(err_msg)


if __name__ == '__main__':
    handle_args()
