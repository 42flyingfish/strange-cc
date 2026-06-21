import parser
from dataclasses import replace
from functools import singledispatch

from utility import Identifier, make_temporary


@singledispatch
def label_loop(n,
               current_label: Identifier | None,
               s: bool):
    raise NotImplementedError(f'type {type(n)} not handled')


@label_loop.register
def label_loop_program(n: parser.Program,
                       current_label: Identifier | None,
                       s: bool) -> parser.Program:
    func_nodes = [label_loop(f, current_label, s)
                  for f in n.function_definition]
    return replace(n, function_definition=func_nodes)


@label_loop.register
def label_loop_func(n: parser.Function,
                    current_label: Identifier | None,
                    s: bool) -> parser.Function:
    new_body = label_loop(n.body, current_label, s)
    return replace(n, body=new_body)


@label_loop.register
def label_loop_block(n: parser.Block,
                     current_label: Identifier | None,
                     s: bool) -> parser.Block:
    items = [label_loop(x, current_label, s) for x in n.block_items]
    return replace(n, block_items=items)


@label_loop.register
def label_loop_s(n: parser.S,
                 current_label: Identifier | None,
                 s: bool) -> parser.S:
    stm = label_loop(n.statement, current_label, s)
    return replace(n, statement=stm)


@label_loop.register
def label_loop_d(n: parser.D,
                 current_label: Identifier | None,
                 s: bool) -> parser.D:
    return n


@label_loop.register
def label_loop_none(n: None,
                    current_label: Identifier | None,
                    s: bool) -> None:
    return None


@label_loop.register
def label_loop_null(n: parser.Null,
                    current_label: Identifier | None,
                    s: bool) -> parser.Null:
    return n


@label_loop.register
def label_loop_return(n: parser.Return,
                      current_label: Identifier | None,
                      s: bool) -> parser.Return:
    return n


@label_loop.register
def label_loop_ExpNode(n: parser.ExpNode,
                       current_label: Identifier | None,
                       s: bool) -> parser.ExpNode:
    return n


@label_loop.register
def label_loop_if(n: parser.If,
                  current_label: Identifier | None,
                  s: bool) -> parser.If:
    stm = label_loop(n.then, current_label, s)
    return replace(n, then=stm)


@label_loop.register
def label_loop_ifelse(n: parser.IfElse,
                      current_label: Identifier | None,
                      s: bool) -> parser.IfElse:
    first = label_loop(n.then, current_label, s)
    second = label_loop(n.otherwise, current_label, s)
    return replace(n, then=first, otherwise=second)


@label_loop.register
def label_loop_label(n: parser.Label,
                     current_label: Identifier | None,
                     s: bool) -> parser.Label:
    labeled_stm = label_loop(n.stm, current_label, s)
    return replace(n, stm=labeled_stm)


@label_loop.register
def label_loop_goto(n: parser.Goto,
                    current_label: Identifier | None,
                    s: bool) -> parser.Goto:
    return n


@label_loop.register
def lablel_loop_funcall(n: parser.FunctionCall,
                        current_label: Identifier | None,
                        s: bool) -> parser.FunctionCall:
    return n


@label_loop.register
def lablel_loop_fundecl(n: parser.FunDecl,
                        current_label: Identifier | None,
                        s: bool) -> parser.FunDecl:
    func = label_loop(n.function_definition, current_label, s)
    return replace(n, function_definition=func)


@label_loop.register
def label_loop_compound(n: parser.Compound,
                        current_label: Identifier | None,
                        s: bool) -> parser.Compound:
    new_blck = label_loop(n.block, current_label, s)
    return replace(n, block=new_blck)


@label_loop.register
def label_loop_break(n: parser.Break,
                     current_label: Identifier | None,
                     s: bool) -> parser.Break:
    if current_label is None:
        # Don't crash if there is a switch ctx
        if s:
            return n
        raise RuntimeError('Break used outside of loop ctx')
    return replace(n, label=current_label)


@label_loop.register
def label_loop_continue(n: parser.Continue,
                        current_label: Identifier | None,
                        s: bool) -> parser.Continue:
    if current_label is None:
        raise RuntimeError('Continue used outised of loop ctx')
    return replace(n, label=current_label)


@label_loop.register
def label_loop_while(n: parser.While,
                     current_label: Identifier | None,
                     s: bool) -> parser.While:
    tmp = make_temporary('while')
    new_body = label_loop(n.body, tmp, s)
    return replace(n, body=new_body, label=tmp)


@label_loop.register
def label_loop_Dowhile(n: parser.DoWhile,
                       current_label: Identifier | None,
                       s: bool) -> parser.DoWhile:
    tmp = make_temporary('dowhile')
    new_body = label_loop(n.body, tmp, s)
    return replace(n, body=new_body, label=tmp)


@label_loop.register
def label_loop_For(n: parser.For,
                   current_label: Identifier | None,
                   s: bool) -> parser.For:
    tmp = make_temporary('For')
    new_body = label_loop(n.body, tmp, s)
    return replace(n, body=new_body, label=tmp)


@label_loop.register
def label_loop_switch(n: parser.Switch,
                      current_label: Identifier | None,
                      s: bool) -> parser.Switch:
    stm = label_loop(n.body, current_label, True)
    return replace(n, body=stm)


@label_loop.register
def label_loop_case(n: parser.Case,
                    current_label: Identifier | None,
                    s: bool) -> parser.Case:
    stm = label_loop(n.stm, current_label, s)
    return replace(n, stm=stm)


@label_loop.register
def label_loop_default(n: parser.Default,
                       current_label: Identifier | None,
                       s: bool) -> parser.Default:
    stm = label_loop(n.stm, current_label, s)
    return replace(n, stm=stm)


def resolve_program(p: parser.Program) -> parser.Program:
    ast = label_loop(p, None, False)
    return ast
