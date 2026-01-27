import parser
from dataclasses import replace
from functools import singledispatch

from utility import Identifier, make_temporary


@singledispatch
def label_loop(n, current_label: Identifier | None = None):
    raise NotImplementedError(f'type {type(n)} not handled')


@label_loop.register
def label_loop_program(n: parser.Program,
                       current_label: Identifier | None) -> parser.Program:
    func_node = label_loop(n.function_definition, current_label)
    return replace(n, function_definition=func_node)


@label_loop.register
def label_loop_func(n: parser.Function,
                    current_label: Identifier | None) -> parser.Function:
    new_body = label_loop(n.body, current_label)
    return replace(n, body=new_body)


@label_loop.register
def label_loop_block(n: parser.Block,
                     current_label: Identifier | None) -> parser.Block:
    items = [label_loop(x, current_label) for x in n.block_items]
    return replace(n, block_items=items)


@label_loop.register
def label_loop_s(n: parser.S,
                 current_label: Identifier | None) -> parser.S:
    stm = label_loop(n.statement, current_label)
    return replace(n, statement=stm)


@label_loop.register
def label_loop_d(n: parser.D,
                 current_label: Identifier | None) -> parser.D:
    return n


@label_loop.register
def label_loop_none(n: None,
                    current_label: Identifier | None) -> None:
    return None


@label_loop.register
def label_loop_null(n: parser.Null,
                    current_label: Identifier | None) -> parser.Null:
    return n


@label_loop.register
def label_loop_return(n: parser.Return,
                      current_label: Identifier | None) -> parser.Return:
    return n


@label_loop.register
def label_loop_ExpNode(n: parser.ExpNode,
                       current_label: Identifier | None) -> parser.ExpNode:
    return n


@label_loop.register
def label_loop_if(n: parser.If,
                  current_label: Identifier | None) -> parser.If:
    stm = label_loop(n.then, current_label)
    return replace(n, then=stm)


@label_loop.register
def label_loop_ifelse(n: parser.IfElse,
                      current_label: Identifier | None) -> parser.IfElse:
    first = label_loop(n.then, current_label)
    second = label_loop(n.otherwise, current_label)
    return replace(n, then=first, otherwise=second)


@label_loop.register
def label_loop_label(n: parser.Label,
                     current_label: Identifier | None) -> parser.Label:
    labeled_stm = label_loop(n.stm, current_label)
    return replace(n, stm=labeled_stm)


@label_loop.register
def label_loop_goto(n: parser.Goto,
                    current_label: Identifier | None) -> parser.Goto:
    return n


@label_loop.register
def label_loop_compound(n: parser.Compound,
                        current_label: Identifier | None) -> parser.Compound:
    new_blck = label_loop(n.block, current_label)
    return replace(n, block=new_blck)


@label_loop.register
def label_loop_break(n: parser.Break,
                     current_label: Identifier | None) -> parser.Break:
    if current_label is None:
        raise RuntimeError('Break used outside of loop ctx')
    return replace(n, label=current_label)


@label_loop.register
def label_loop_continue(n: parser.Continue,
                        current_label: Identifier | None) -> parser.Continue:
    if current_label is None:
        raise RuntimeError('Continue used outised of loop ctx')
    return replace(n, label=current_label)


@label_loop.register
def label_loop_while(n: parser.While,
                     current_label: Identifier | None) -> parser.While:
    tmp = make_temporary('while')
    new_body = label_loop(n.body, tmp)
    return replace(n, body=new_body, label=tmp)


@label_loop.register
def label_loop_Dowhile(n: parser.DoWhile,
                       current_label: Identifier | None) -> parser.DoWhile:
    tmp = make_temporary('dowhile')
    new_body = label_loop(n.body, tmp)
    return replace(n, body=new_body, label=tmp)


@label_loop.register
def label_loop_For(n: parser.For,
                   current_label: Identifier | None) -> parser.For:
    tmp = make_temporary('For')
    new_body = label_loop(n.body, tmp)
    return replace(n, body=new_body, label=tmp)


def resolve_program(p: parser.Program) -> parser.Program:
    ast = label_loop(p, None)
    return ast
