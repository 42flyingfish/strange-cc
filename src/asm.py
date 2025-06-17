from dataclasses import dataclass
import parser


@dataclass
class Imm():
    val: str


@dataclass
class Register():
    """ For now, we are going to use EAX for all values
    See Sandler's pg 18
    """
    pass


Operand = Imm | Register


@dataclass
class Ret():
    pass


@dataclass
class Mov():
    src: Operand
    dst: Operand


Instruction = Mov | Ret


@dataclass
class Function():
    name: str
    instructions: list[Instruction]


@dataclass
class Program():
    function_definition: Function


def parse_imm(x: parser.Constant) -> Imm:
    return Imm(val=x.val)


def parse_return(x: parser.Return) -> list[Instruction]:
    return [Mov(parse_imm(x.exp), Register()), Ret()]


def parse_function(x: parser.Function) -> Function:
    identifier = x.name.val
    statement = parse_return(x.body)
    return Function(name=identifier, instructions=statement)


def parse_program(x: parser.Program) -> Program:
    return Program(function_definition=parse_function(x.function_definition))
