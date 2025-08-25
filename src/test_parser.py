import parser
import unittest

import lexer


class TestConstantParser(unittest.TestCase):

    def test_parse_constant(self):
        TOKENS = [lexer.TkConstant('42')]
        print(repr(TOKENS[0]))
        print(type(TOKENS[0]))

        ret = parser.parse_constant(TOKENS, 0)
        self.assertFalse(ret is None)

    def test_parse_identifier(self):
        TOKENS = [lexer.TkIdentifier('What')]
        ret = parser.parse_identifier(TOKENS, 0)
        self.assertFalse(ret is None)

    def test_parse_return(self):
        TOKENS = [lexer.TkReturn(),
                  lexer.TkConstant('42'),
                  lexer.TkSemicolon()]
        ret = parser.parse_return(TOKENS, 0)
        self.assertFalse(ret is None)

    def test_parse_function(self):
        TOKENS = [lexer.TkInt(),
                  lexer.TkIdentifier('What'),
                  lexer.TkOpenParenthesis(),
                  lexer.TkVoid(),
                  lexer.TkCloseParenthesis(),
                  lexer.TkOpenBrace(),
                  lexer.TkReturn(),
                  lexer.TkConstant('42'),
                  lexer.TkSemicolon(),
                  lexer.TkCloseBrace()]
        ret = parser.parse_function(TOKENS, 0)
        self.assertFalse(ret is None)

    def test_parse_program(self):
        TOKENS = [lexer.TkInt(),
                  lexer.TkIdentifier('What'),
                  lexer.TkOpenParenthesis(),
                  lexer.TkVoid(),
                  lexer.TkCloseParenthesis(),
                  lexer.TkOpenBrace(),
                  lexer.TkReturn(),
                  lexer.TkConstant('42'),
                  lexer.TkSemicolon(),
                  lexer.TkCloseBrace()]
        ret = parser.parse_program(TOKENS, 0)
        self.assertFalse(ret is None)

    def test_end_before_parse(self):
        # based on the test case from Nora Sandler's book
        CODE = """int main(void)  {return"""
        TOKENS = lexer.tokenize_string(CODE)
        ret = parser.parse_program(TOKENS, 0)
        self.assertTrue(ret is None)

    def test_binary_basic(self):
        LEFT = parser.Constant('1')
        RIGHT = parser.Constant('2')
        TABLE = (('1 + 2', parser.Binary(parser.Bin_Op.ADD,
                                         LEFT,
                                         RIGHT)),
                 ('1 - 2', parser.Binary(parser.Bin_Op.SUBTRACT,
                                         LEFT,
                                         RIGHT)),
                 ('1 * 2', parser.Binary(parser.Bin_Op.MULTIPLY,
                                         LEFT,
                                         RIGHT)),
                 ('1 / 2', parser.Binary(parser.Bin_Op.DIVIDE,
                                         LEFT,
                                         RIGHT)),
                 ('1 % 2', parser.Binary(parser.Bin_Op.REMAINDER,
                                         LEFT,
                                         RIGHT)))

        for x, y in TABLE:
            with self.subTest(x=x, y=y):
                tokens = lexer.tokenize_string(x)
                result, _ = parser.parse_expr(tokens, 0)
                self.assertEqual(result, y)

    def test_nested_basic(self):
        c_code = 'int main(void) { return 3 + 4 + 5; }'
        should_be = parser.Program(
            parser.Function(parser.Identifier("main"),
                            parser.Return(
                                parser.Binary(parser.Bin_Op.ADD,
                                              parser.Binary(
                                                  parser.Bin_Op.ADD,
                                                  parser.Constant("3"),
                                                  parser.Constant("4")),
                                              parser.Constant("5")))))
        tokens = lexer.tokenize_string(c_code)
        result = parser.parse_program(tokens, 0)

        self.assertEqual(result, should_be)

    def test_nested_associative(self):
        # based on the test case from Nora Sandler's book
        # Pg. 55 Precedence Climbing in Action
        c_code = '1 * 2 - 3 * (4 + 5)'
        parens = parser.Binary(parser.Bin_Op.ADD,
                               parser.Constant('4'),
                               parser.Constant('5'))
        should_be = parser.Binary(parser.Bin_Op.SUBTRACT,
                                  parser.Binary(parser.Bin_Op.MULTIPLY,
                                                parser.Constant('1'),
                                                parser.Constant('2')),
                                  parser.Binary(parser.Bin_Op.MULTIPLY,
                                                parser.Constant('3'),
                                                parens))
        tokens = lexer.tokenize_string(c_code)
        result, _ = parser.parse_expr(tokens, 0)

        self.assertEqual(result, should_be)
