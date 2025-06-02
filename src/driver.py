#! /bin/python
import argparse
import os
import lexer
import parser as p


def handle_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--lex', action='store_true')
    group.add_argument('--parse', action='store_true')
    group.add_argument('--codegen', action='store_true')

    parser.add_argument('filepath', type=str)

    args = parser.parse_args()

    if not os.path.isfile(args.filepath):
        print(f'File not found {args.filepath}')
        return

    if args.lex:
        print(f'lexing {args.filepath}')
        result = lexer.tokenize_file(args.filepath)
    elif args.parse:
        result = lexer.tokenize_file(args.filepath)
        x = p.parse_program(result, 0)
        if x is None:
            raise ValueError("Failed to parse a program")
        elif len(result) > x[1]:
            raise ValueError("Extra code after parsing")

    elif args.codegen:
        print(f'codegen {args.filepath}')
    else:
        print('Reaching this should not be possible')

 
if __name__ == '__main__':
    handle_args()
