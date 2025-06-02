import unittest
import lexer
import parser


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
        TOKENS = [lexer.TkReturn(), lexer.TkConstant('42'), lexer.TkSemicolon()]
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
