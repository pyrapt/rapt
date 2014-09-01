import functools

from rapt.rapt import Rapt
from rapt.transformers.sql import sql_translator
from rapt.treebrd.grammars import CoreGrammar
from rapt.treebrd.grammars.extended_grammar import ExtendedGrammar
from rapt.treebrd.treebrd import TreeBRD

from tests.transformers.test_transfomer import TestTransformer


class TestSQLSequence(TestTransformer):
    grammar = CoreGrammar()

    def setUp(self):
        self.translate = self.translate_func(functools.partial(Rapt(
            grammar='Extended Grammar').to_sql_sequence,
            use_bag_semantics=True))
        self.translate_set = self.translate_func(functools.partial(Rapt(
            grammar='Extended Grammar').to_sql_sequence))


class TestRelation(TestSQLSequence):
    def test_single_relation(self):
        ra = 'Alpha;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_single_relation_set(self):
        ra = 'Alpha;'
        expected = [['SELECT DISTINCT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha']]
        actual = self.translate_set(ra)
        self.assertEqual(expected, actual)

    def test_multiple_relations(self):
        ra = 'Alpha; Beta;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha'],
                    ['SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestSelect(TestSQLSequence):
    def test_single_select(self):
        ra = '\\select_{a1=a2} Alpha;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                     'SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                     'WHERE a1 = a2']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_select_with_multiple_conditions(self):
        ra = '\\select_{a1=2 or a1=1} \\select_{a2=2 or a2=1} Alpha;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                     'SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                     'WHERE a2 = 2 or a2 = 1',
                     'SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                     'WHERE (a2 = 2 or a2 = 1) AND (a1 = 2 or a1 = 1)']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestProject(TestSQLSequence):
    def test_simple(self):
        ra = '\\project_{a1, a2} Alpha;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                     'SELECT Alpha.a1, Alpha.a2 FROM Alpha']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestRename(TestSQLSequence):
    def test_relation(self):
        ra = '\\rename_{Apex} Alpha;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                    'SELECT Apex.a1, Apex.a2, Apex.a3 '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Apex(a1, a2, a3)']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_attributes(self):
        ra = '\\rename_{(a, b, c)} Alpha;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                    'SELECT Alpha.a, Alpha.b, Alpha.c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Alpha(a, b, c)']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_all(self):
        ra = '\\rename_{Apex(a, b, c)} Alpha;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                    'SELECT Apex.a, Apex.b, Apex.c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Apex(a, b, c)']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestAssignment(TestSQLSequence):
    def test_relation(self):
        ra = 'NewAlpha := Alpha;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                      'CREATE TEMPORARY TABLE NewAlpha(a1, a2, a3) AS '
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestJoin(TestSQLSequence):
    def test_relation(self):
        ra = 'Alpha \\join Beta;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                     'SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta',
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3, '
                    'Beta.b1, Beta.b2, Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_three_relations(self):
        self.maxDiff = None
        ra = 'Alpha \\join Beta \\join Gamma;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                     'SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta',

                     'SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                     'Beta.b3 FROM '
                     '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                     'CROSS JOIN '
                     '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta',

                     'SELECT Gamma.g1, Gamma.g2 FROM Gamma',

                     'SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                     'Beta.b3, Gamma.g1, Gamma.g2 FROM '
                     '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                     'CROSS JOIN '
                     '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                     'CROSS JOIN '
                     '(SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS Gamma']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestNaturalJoin(TestSQLSequence):
    grammar = ExtendedGrammar()

    def test_relation_simple(self):
        ra = 'Alpha \\natural_join AlphaTwin;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                     'SELECT AlphaTwin.a1, AlphaTwin.a2, AlphaTwin.a3 FROM AlphaTwin',
                     'SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM '
                     '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                     'NATURAL JOIN '
                     '(SELECT AlphaTwin.a1, AlphaTwin.a2, AlphaTwin.a3 '
                     'FROM AlphaTwin) AS AlphaTwin']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestThetaJoin(TestSQLSequence):
    grammar = ExtendedGrammar()

    def test_relation(self):
        ra = 'Alpha \\join_{a1 = b1} Beta;'
        expected = [['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                    'SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta',
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3, '
                    'Beta.b1, Beta.b2, Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                    'WHERE a1 = b1']]
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestSet:
    def test_simple(self):
        ra = 'Gamma {operator} GammaTwin;'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0])
        root_list = root_list[0].post_order()
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma',
                     'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin',
                     'SELECT g1, g2 FROM ('
                     'SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                     '{operator} ALL '
                     'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                     'AS _{name}'.format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_simple_multiple(self):
        ra = 'Gamma {operator} GammaTwin {operator} GammaPrime;'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        root_name = id(root_list[0])
        child_name = id(root_list[0].left)
        root_list = root_list[0].post_order()
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT Gamma.g1, Gamma.g2 FROM Gamma',
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin',

                    'SELECT g1, g2 FROM (SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    '{operator} ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) AS _{name1}'
                        .format(operator=self.sql_operator, name1=child_name, name2=root_name),

                    'SELECT GammaPrime.g1, GammaPrime.g2 FROM GammaPrime',

                    'SELECT g1, g2 FROM ('
                    'SELECT g1, g2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    '{operator} ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) AS _{name1} '
                    '{operator} ALL '
                    'SELECT GammaPrime.g1, GammaPrime.g2 FROM GammaPrime) AS _{name2}'
                        .format(operator=self.sql_operator, name1=child_name, name2=root_name)]
        self.assertEqual(expected, actual)


class TestUnion(TestSQLSequence, TestSet):
    ra_operator = '\\union'
    sql_operator = 'UNION'


class TestDifference(TestSQLSequence, TestSet):
    ra_operator = '\\difference'
    sql_operator = 'EXCEPT'


class TestIntersection(TestSQLSequence, TestSet):
    grammar = ExtendedGrammar()
    ra_operator = '\\intersect'
    sql_operator = 'INTERSECT'