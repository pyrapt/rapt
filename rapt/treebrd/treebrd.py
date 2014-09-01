from rapt.treebrd.schema import Schema
from .utility import flatten
from .node import SelectNode, ProjectNode, RenameNode, \
    AssignNode, CrossJoinNode, NaturalJoinNode, UnionNode, DifferenceNode, \
    IntersectNode, ThetaJoinNode, RelationNode


class TreeBRD:
    """
    A Tree Builder for Relational (Algebra) Data. TreeBRD is a factory class
    that builds forests of relational algebra syntax trees. STARBuilder
    """

    def __init__(self, grammar):
        self.grammar = grammar

    def build(self, instring, schema):
        ra = self.grammar.parse(instring).asList()
        _schema = Schema(schema)
        result = []
        for statement in ra[:]:
            result.append(self.to_node(statement, _schema))
            _schema.clear_temporary()
        return result

    def to_node(self, exp, schema):
        """
        Return a Node that is the root of the parse tree for the the specified
        expression.

        :param exp: A list that represents a relational algebra expression.
        Assumes that this list was generated by pyparsing.
        :param schema: A dictionary of relation names to attribute names used
        for verification and generating attributes.
        :return: A Node.
        """
        # A relation node.
        if len(exp) == 1 and isinstance(exp[0], str):
            node = RelationNode(name=exp[0], schema=schema)

        # An expression.
        elif len(exp) == 1 and isinstance(exp[0], list):
            node = self.to_node(exp[0], schema)

        # Unary operators.
        elif isinstance(exp[0], str) and self.grammar.is_unary(exp[0]):
            child = self.to_node(exp[2:], schema)
            node = self.create_unary_node(operator=exp[0], child=child,
                                          param=exp[1], schema=schema)

        # Assignment.
        elif exp[1] is self.grammar.syntax.assign_op:
            child = self.to_node(exp[2:], schema)
            node = self.create_unary_node(operator=exp[1], child=child,
                                          param=exp[0], schema=schema)

        # Binary operators.
        elif self.grammar.is_binary(exp[1]):
            # Build from right to left, to create the correct syntax tree.
            left = self.to_node(exp[:-2], schema)
            right = self.to_node(exp[-1], schema)
            node = self.create_binary_node(operator=exp[-2], left=left,
                                           right=right)

        elif self.grammar.is_binary_with_params(exp[1]):
            left = self.to_node(exp[0], schema)
            right = self.to_node(exp[3:], schema)
            node = self.create_binary_node(operator=exp[1], left=left,
                                           right=right, param=exp[2])

        else:
            raise ValueError

        return node

    def create_unary_node(self, operator, child, param=None, schema=None):
        """
        Return a Unary Node whose type depends on the specified operator.

        :param schema:
        :param child:
        :param operator: A relational algebra operator (see constants.py)
        :param param: A list of parameters for the operator.
        :return: A Unary Node.
        """

        if operator == self.grammar.syntax.select_op:
            conditions = ' '.join(flatten(param))
            node = SelectNode(child, conditions)

        elif operator == self.grammar.syntax.project_op:
            node = ProjectNode(child, param)

        elif operator == self.grammar.syntax.rename_op:
            name = None
            attributes = []
            if isinstance(param[0], str):
                name = param.pop(0)
            if param:
                attributes = param[0]
            node = RenameNode(child, name, attributes, schema)

        elif operator == self.grammar.syntax.assign_op:
            name = param[0]
            attributes = [] if len(param) < 2 else param[1]
            node = AssignNode(child, name, attributes, schema)

        else:
            raise ValueError

        return node

    def create_binary_node(self, operator, left, right, param=None):
        """
        Return a Node whose type depends on the specified operator.

        :param operator: A relational algebra operator (see constants.py)
        :return: A Node.
        """

        # Join operators
        if operator == self.grammar.syntax.join_op:
            node = CrossJoinNode(left, right)

        elif operator == self.grammar.syntax.natural_join_op:
            node = NaturalJoinNode(left, right)

        elif operator == self.grammar.syntax.theta_join_op:
            conditions = ' '.join(flatten(param))
            node = ThetaJoinNode(left, right, conditions)

        # Set operators
        elif operator == self.grammar.syntax.union_op:
            node = UnionNode(left, right)

        elif operator == self.grammar.syntax.difference_op:
            node = DifferenceNode(left, right)

        elif operator == self.grammar.syntax.intersect_op:
            node = IntersectNode(left, right)

        else:
            raise ValueError

        return node
