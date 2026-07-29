import parser
from dataclasses import replace
from functools import singledispatch

from utility import Identifier, make_temporary

# 1 find switch
# 2 if not in switch and case fail
# 3 On Switch collect cases
# 4 replace cases with labels
# 5 replace switch with chain of if


class CaseTable:
    def __init__(self) -> None:
        self.scope: list[dict] = list()
        self.switch_id: list[Identifier] = list()

    def push(self) -> None:
        self.scope.append({})
        id = make_temporary('switch')
        self.switch_id.append(id)

    def pop(self) -> None:
        self.scope.pop()
        self.switch_id.pop()

    def register(self, key: parser.Constant | str, val: Identifier) -> None:
        # string for default
        if key in self.scope[-1].keys():
            raise RuntimeError('Case already exists')
        self.scope[-1][key] = val

    def empty(self) -> bool:
        return not self.scope

    def top(self) -> dict:
        return self.scope[-1]

    def current_id(self) -> Identifier:
        return self.switch_id[-1]


@singledispatch
def on_switch(n, *args, **kwargs):
    raise NotImplementedError(f'type {type(n)} not handled')


@on_switch.register
def on_switch_prog(n: parser.Program,
                   t: CaseTable,
                   l: bool) -> parser.Program:
    funcs = [on_switch(f, t, l) for f in n.function_definition]
    return replace(n, function_definition=funcs)


@on_switch.register
def on_switch_func(n: parser.Function,
                   t: CaseTable,
                   l: bool) -> parser.Function:
    body = on_switch(n.body, t, l)
    return replace(n, body=body)


@on_switch.register
def on_switch_block(n: parser.Block,
                    t: CaseTable,
                    l: bool) -> parser.Block:
    items = [on_switch(x, t, l) for x in n.block_items]
    return replace(n, block_items=items)


@on_switch.register
def on_switch_block_item(n: parser.Block_Item,
                         t: CaseTable,
                         l: bool) -> parser.Block_Item:
    if isinstance(n, parser.D):
        return n
    new_s = on_switch(n.statement, t, l)
    return replace(n, statement=new_s)


@on_switch.register
def on_switch_return(n: parser.Return,
                     t: CaseTable,
                     l: bool) -> parser.Return:
    return n


@on_switch.register
def on_switch_expNode(n: parser.ExpNode,
                      t: CaseTable,
                      l: bool) -> parser.ExpNode:
    return n


@on_switch.register
def on_switch_if(n: parser.If,
                 t: CaseTable,
                 l: bool) -> parser.If:
    stm = on_switch(n.then, t, l)
    return replace(n, then=stm)


@on_switch.register
def on_switch_ifElse(n: parser.IfElse,
                     t: CaseTable,
                     l: bool) -> parser.IfElse:
    stm_then = on_switch(n.then, t, l)
    stm_otherwise = on_switch(n.otherwise, t, l)
    return replace(n, then=stm_then, otherwise=stm_otherwise)


@on_switch.register
def on_switch_null(n: parser.Null,
                   t: CaseTable,
                   l: bool) -> parser.Null:
    return n


@on_switch.register
def on_switch_label(n: parser.Label,
                    t: CaseTable,
                    l: bool) -> parser.Label:
    stm = on_switch(n.stm, t, l)
    return replace(n, stm=stm)


@on_switch.register
def on_switch_goto(n: parser.Goto,
                   t: CaseTable,
                   l: bool) -> parser.Goto:
    return n


@on_switch.register
def on_switch_fundecl(n: parser.FunDecl,
                      t: CaseTable,
                      l: bool) -> parser.FunDecl:
    func = on_switch(n.function_definition, t, l)
    return replace(n, function_definition=func)


@on_switch.register
def on_switch_none(n: None,
                   t: CaseTable,
                   l: bool) -> None:
    return None


@on_switch.register
def on_switch_compound(n: parser.Compound,
                       t: CaseTable,
                       l: bool) -> parser.Compound:
    blck = on_switch(n.block, t, l)
    return replace(n, block=blck)


@on_switch.register
def on_switch_break(n: parser.Break,
                    t: CaseTable,
                    l: bool) -> parser.Goto | parser.Break:
    # don't modify breaks in loops
    if l:
        return n
    # replace them with switch end label
    return parser.Goto(t.current_id())


@on_switch.register
def on_switch_continue(n: parser.Continue,
                       t: CaseTable,
                       l: bool) -> parser.Continue:
    return n


@on_switch.register
def on_switch_while(n: parser.While,
                    t: CaseTable,
                    l: bool) -> parser.While:
    stm = on_switch(n.body, t, True)
    return replace(n, body=stm)


@on_switch.register
def on_switch_dowhile(n: parser.DoWhile,
                      t: CaseTable,
                      l: bool) -> parser.DoWhile:
    stm = on_switch(n.body, t, True)
    return replace(n, body=stm)


@on_switch.register
def on_switch_for(n: parser.For,
                  t: CaseTable,
                  l: bool) -> parser.For:
    stm = on_switch(n.body, t, True)
    return replace(n, body=stm)


@on_switch.register
def on_switch_case(n: parser.Case,
                   t: CaseTable,
                   l: bool) -> parser.Label:
    if t.empty():
        raise RuntimeError('Case found outside of switch')
    if not isinstance(n.cond, parser.Constant):
        # TODO contant expressions like 1 + 4 are valid
        # and must be supported
        raise RuntimeError('Conditions in cases must be constant')
    target = make_temporary('switch_target')
    t.register(n.cond, target)
    stm = on_switch(n.stm, t, l)

    # the goal is to convert the cases to jump labels
    return parser.Label(target, stm)


@on_switch.register
def on_switch_default(n: parser.Default,
                      t: CaseTable,
                      l: bool) -> parser.Label:
    if t.empty():
        raise RuntimeError('Default used outside of switch')
    target = make_temporary('switch_target')
    t.register('default', target)
    stm = on_switch(n.stm, t, l)

    # convert this to a valid jump label
    return parser.Label(target, stm)


@on_switch.register
def on_switch_switch(n: parser.Switch,
                     t: CaseTable,
                     l: bool) -> parser.Compound:
    t.push()
    stm = on_switch(n.body, t, False)

    id = make_temporary('switch_var')

    ladder: list[parser.Block_Item] = list()

    ladder.append(
        parser.D(parser.VarDecl(parser.VariableDefinition(id, n.exp))))

    for key, value in t.top().items():
        if key == 'default':
            continue
        item = parser.S(
            parser.If(parser.Binary(parser.Bin_Op.EQUAL,
                                    key,
                                    parser.Var(id)),
                      parser.Goto(value)))
        ladder.append(item)

    if 'default' in t.top():
        ladder.append(parser.S(parser.Goto(t.top()['default'])))
    else:
        ladder.append(parser.S(parser.Goto(t.current_id())))

    ladder.append(parser.S(stm))
    ladder.append(parser.S(parser.Label(t.current_id(),
                                        parser.Null())))

    t.pop()
    return parser.Compound(parser.Block(ladder))


def lower_switch(n):
    table = CaseTable()
    return on_switch(n, table, True)
