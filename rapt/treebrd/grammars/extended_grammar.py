from pyparsing import *

from .core_grammar import CoreGrammar


class ExtendedGrammar(CoreGrammar):
    """
    A parser that recognizes an extended relational algebra grammar.

    The rules are annotated with their BNF equivalents. For a complete
    specification refer to the associated grammar file.
    """

    # Grammar Rules

    # natural_join_expr ::= expression natural_join expression

    # theta_join_expr ::= expression join
    # param_start conditions param_stop expression

    #
    @property
    def natural_join(self):
        """
        natural_join_expr ::= expression natural_join expression
        """
        return CaselessKeyword(self.syntax.natural_join_op)

    @property
    def theta_join(self):
        """
        select_expr ::= select param_start conditions param_stop expression
        """
        return self.parametrize(self.syntax.join_op, self.conditions). \
            setParseAction(self.theta_parse_action)

    #todo: remove replacement of theta_join_op
    def theta_parse_action(self, s, l, t):
        t[0] = self.syntax.theta_join_op
        return t

    @property
    def binary_op_p1(self):
        return super().binary_op_p1 ^ self.natural_join ^ self.theta_join

    @property
    def intersect(self):
        """
        intersect_op ::= intersect_name
        """
        return CaselessKeyword(self.syntax.intersect_op)

    @property
    def binary_op_p2(self):
        return super().binary_op_p2 | self.intersect

    def is_unary(self, operator):
        return operator in {self.syntax.select_op,
                            self.syntax.project_op,
                            self.syntax.rename_op}

    def is_binary(self, operator):
        return (operator in {self.syntax.intersect_op,
                             self.syntax.natural_join_op} or
                super().is_binary(operator))

    def is_binary_with_params(self, operator):
        return operator in {self.syntax.theta_join_op}