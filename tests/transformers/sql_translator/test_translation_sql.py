import functools

from rapt.rapt import Rapt
from rapt.transformers.sql import sql_translator
from rapt.treebrd.grammars import CoreGrammar
from rapt.treebrd.grammars.extended_grammar import ExtendedGrammar
from rapt.treebrd.errors import AttributeReferenceError
from rapt.treebrd.treebrd import TreeBRD

from tests.transformers.test_transfomer import TestTransformer


class TestSQL(TestTransformer):
    grammar = CoreGrammar()

    def setUp(self):
        self.translate = self.translate_func(functools.partial(Rapt(
            grammar='Extended Grammar').to_sql, use_bag_semantics=True))
        self.translate_set = self.translate_func(functools.partial(Rapt(
            grammar='Extended Grammar').to_sql))


class TestRelation(TestSQL):
    def test_single_relation(self):
        ra = 'Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_single_relation_set(self):
        ra = 'Alpha;'
        expected = ['SELECT DISTINCT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha']
        actual = self.translate_set(ra)
        self.assertEqual(expected, actual)

    def test_multiple_relations(self):
        ra = 'Alpha; Beta;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha',
                    'SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestSelect(TestSQL):
    def test_single_select(self):
        ra = '\\select_{a1=a2} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 '
                    'FROM Alpha WHERE a1 = a2']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_single_select_set(self):
        ra = '\\select_{a1=a2} Alpha;'
        expected = ['SELECT DISTINCT Alpha.a1, Alpha.a2, Alpha.a3 '
                    'FROM Alpha WHERE a1 = a2']
        actual = self.translate_set(ra)
        self.assertEqual(expected, actual)

    def test_single_select_with_relation(self):
        ra = '\\select_{Alpha.a1=a2} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE Alpha.a1 = a2']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_selects(self):
        ra = '\\select_{a1=1} \\select_{a2=2} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE (a2 = 2) AND (a1 = 1)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_select_with_precedence(self):
        ra = '\\select_{a2=a3} (\\select_{a1=a2} Alpha);'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE (a1 = a2) AND (a2 = a3)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_select_with_multiple_conditions(self):
        ra = '\\select_{a1=2 or a1=1} \\select_{a2=2 or a2=1} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE (a2 = 2 or a2 = 1) AND (a1 = 2 or a1 = 1)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_single_select_wrong_attrs(self):
        ra = '\\select_{b1=bee_one} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)

    def test_multiple_selects_wrong_attrs(self):
        ra = '\\select_{b1=1} \\select_{bee_two=2} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)

    def test_multiple_selects_wrong_attrs_both(self):
        ra = '\\select_{bee_one=1} \\select_{a_two=2} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)


class TestProject(TestSQL):
    def test_simple(self):
        ra = '\\project_{a1, a2, a3} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_prefixed(self):
        ra = '\\project_{Alpha.a1, Alpha.a2, Alpha.a3} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_subset(self):
        ra = '\\project_{a1, Alpha.a2} Alpha;'
        expected = ['SELECT Alpha.a1, Alpha.a2 FROM Alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_not_a_subset(self):
        ra = '\\project_{b} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)

    def test_not_a_subset2(self):
        ra = '\\project_{Alpha.a1, b} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)

    def test_not_a_subset3(self):
        ra = '\\project_{a1, Alpha.b} Alpha;'
        self.assertRaises(AttributeReferenceError, self.translate, ra)


class TestRename(TestSQL):
    def test_relation(self):
        ra = '\\rename_{Apex} Alpha;'
        expected = ['SELECT Apex.a1, Apex.a2, Apex.a3 '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Apex(a1, a2, a3)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_attributes(self):
        ra = '\\rename_{(a, b, c)} Alpha;'
        expected = ['SELECT Alpha.a, Alpha.b, Alpha.c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Alpha(a, b, c)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_all(self):
        ra = '\\rename_{Apex(a, b, c)} Alpha;'
        expected = ['SELECT Apex.a, Apex.b, Apex.c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Apex(a, b, c)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_with_select(self):
        ra = '\\rename_{Apex(a, b, c)} \\select_{a1 = a2} Alpha;'
        expected = ['SELECT Apex.a, Apex.b, Apex.c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha '
                    'WHERE a1 = a2) AS Apex(a, b, c)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_rename_is_projected(self):
        ra = '\\project_{a, c} \\rename_{Apex(a, b, c)} Alpha;'
        expected = ['SELECT Apex.a, Apex.c '
                    'FROM (SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) '
                    'AS Apex(a, b, c)']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestAssignment(TestSQL):
    def test_relation(self):
        ra = 'NewAlpha := Alpha;'
        expected = ['CREATE TEMPORARY TABLE NewAlpha(a1, a2, a3) AS '
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_relation_with_attributes(self):
        ra = 'NewAlpha(a, b, c) := Alpha;'
        expected = ['CREATE TEMPORARY TABLE NewAlpha(a, b, c) AS '
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_relation_with_ambiguous_attributes(self):
        ra = 'NewAlpha(a, b, c) := Ambiguous;'
        expected = ['CREATE TEMPORARY TABLE NewAlpha(a, b, c) AS '
                    'SELECT Ambiguous.a, Ambiguous.a, Ambiguous.b '
                    'FROM Ambiguous']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select(self):
        ra = 'Niche := \select_{b1=1} Beta;'
        expected = ['CREATE TEMPORARY TABLE Niche(b1, b2, b3) AS '
                    'SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta '
                    'WHERE b1 = 1']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select_with_attributes(self):
        ra = 'Niche(a, b, c) := \select_{b1=1} Beta;'
        expected = ['CREATE TEMPORARY TABLE Niche(a, b, c) AS '
                    'SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta '
                    'WHERE b1 = 1']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_project(self):
        ra = 'Bilk := \\project_{b1, b2} Beta;'
        expected = ['CREATE TEMPORARY TABLE Bilk(b1, b2) AS '
                    'SELECT Beta.b1, Beta.b2 FROM Beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_project_with_attributes(self):
        ra = 'Bilk(a, b) := \\project_{b1, b2} Beta;'
        expected = ['CREATE TEMPORARY TABLE Bilk(a, b) AS '
                    'SELECT Beta.b1, Beta.b2 FROM Beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_project_select(self):
        ra = 'Combine := \\project_{b1, b2} \\select_{b1 = 1} Beta;'
        expected = ['CREATE TEMPORARY TABLE Combine(b1, b2) AS '
                    'SELECT Beta.b1, Beta.b2 FROM Beta '
                    'WHERE b1 = 1']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_join(self):
        ra = 'Bound := Alpha \\join Beta;'
        expected = ['CREATE TEMPORARY TABLE Bound(a1, a2, a3, b1, b2, b3) AS '
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_join_with_attributes(self):
        ra = 'Bound(a, b, c, d, e, f) := Alpha \\join Beta;'
        expected = ['CREATE TEMPORARY TABLE Bound(a, b, c, d, e, f) AS '
                    'SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestJoin(TestSQL):
    def test_relation(self):
        ra = 'Alpha \\join Beta;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, '
                    'Beta.b1, Beta.b2, Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_three_relations(self):
        self.maxDiff = None
        ra = 'Alpha \\join Beta \\join Gamma;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3, Gamma.g1, Gamma.g2 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                    'CROSS JOIN '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS Gamma']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_multiple_relations(self):
        ra = 'Alpha \\join Beta \\join Gamma \\join Delta;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3, Gamma.g1, Gamma.g2, Delta.d1, Delta.d2 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                    'CROSS JOIN '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS Gamma '
                    'CROSS JOIN '
                    '(SELECT Delta.d1, Delta.d2 FROM Delta) AS Delta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_right_join_first(self):
        ra = 'Alpha \\join (Beta \\join Gamma);'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, Beta.b1, Beta.b2, '
                    'Beta.b3, Gamma.g1, Gamma.g2 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                    'CROSS JOIN '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS Gamma']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select_right(self):
        ra = 'Delta \\join \\select_{g1 = g2} Gamma;'
        expected = ['SELECT Delta.d1, Delta.d2, Gamma.g1, Gamma.g2 FROM '
                    '(SELECT Delta.d1, Delta.d2 FROM Delta) AS Delta '
                    'CROSS JOIN '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'WHERE g1 = g2) AS Gamma']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select_left(self):
        ra = '\\select_{g1 = g2} Gamma \\join  Delta;'
        expected = ['SELECT Gamma.g1, Gamma.g2, Delta.d1, Delta.d2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    'WHERE g1 = g2) AS Gamma '
                    'CROSS JOIN '
                    '(SELECT Delta.d1, Delta.d2 FROM Delta) AS Delta']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_select_on_join(self):
        ra = '\\select_{g1 = g2} (Gamma \\join Delta);'
        translation = self.translate(ra)
        expected = ['SELECT Gamma.g1, Gamma.g2, Delta.d1, Delta.d2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS Gamma '
                    'CROSS JOIN '
                    '(SELECT Delta.d1, Delta.d2 FROM Delta) AS Delta '
                    'WHERE g1 = g2']
        actual = translation
        self.assertEqual(expected, actual)

    def test_join_with_rename(self):
        ra = '\\rename_{G} Gamma \\join \\rename_{H} Gamma;'
        translation = self.translate(ra)
        expected = ['SELECT G.g1, G.g2, H.g1, H.g2 FROM '
                    '(SELECT G.g1, G.g2 FROM (SELECT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS G(g1, g2)) AS G '
                    'CROSS JOIN '
                    '(SELECT H.g1, H.g2 FROM (SELECT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS H(g1, g2)) AS H']
        actual = translation
        self.assertEqual(expected, actual)

    def test_join_with_rename_set(self):
        ra = '\\rename_{G} Gamma \\join \\rename_{H} Gamma;'
        translation = self.translate_set(ra)
        expected = ['SELECT DISTINCT G.g1, G.g2, H.g1, H.g2 FROM '
                    '(SELECT DISTINCT G.g1, G.g2 '
                    'FROM (SELECT DISTINCT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS G(g1, g2)) AS G '
                    'CROSS JOIN '
                    '(SELECT DISTINCT H.g1, H.g2 '
                    'FROM (SELECT DISTINCT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS H(g1, g2)) AS H']
        actual = translation
        self.assertEqual(expected, actual)

    def test_join_with_rename_attributes(self):
        ra = '\\rename_{G(a, b)} Gamma \\join \\rename_{H(a, b)} Gamma;'
        translation = self.translate(ra)
        expected = ['SELECT G.a, G.b, H.a, H.b FROM '
                    '(SELECT G.a, G.b FROM (SELECT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS G(a, b)) AS G '
                    'CROSS JOIN '
                    '(SELECT H.a, H.b FROM (SELECT Gamma.g1, Gamma.g2 '
                    'FROM Gamma) AS H(a, b)) AS H']
        actual = translation
        self.assertEqual(expected, actual)


class TestNaturalJoin(TestSQL):
    grammar = ExtendedGrammar()

    def test_relation_simple(self):
        ra = 'Alpha \\natural_join AlphaTwin;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'NATURAL JOIN '
                    '(SELECT AlphaTwin.a1, AlphaTwin.a2, AlphaTwin.a3 '
                    'FROM AlphaTwin) AS AlphaTwin']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)

    def test_three_relations(self):
        ra = 'Alpha \\natural_join AlphaTwin \\natural_join AlphaPrime;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, AlphaPrime.a4, '
                    'AlphaPrime.a5 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'NATURAL JOIN '
                    '(SELECT AlphaTwin.a1, AlphaTwin.a2, AlphaTwin.a3 '
                    'FROM AlphaTwin) AS AlphaTwin '
                    'NATURAL JOIN '
                    '(SELECT AlphaPrime.a1, AlphaPrime.a4, AlphaPrime.a5 '
                    'FROM AlphaPrime) AS AlphaPrime']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestThetaJoin(TestSQL):
    grammar = ExtendedGrammar()

    def test_relation(self):
        ra = 'Alpha \\join_{a1 = b1} Beta;'
        expected = ['SELECT Alpha.a1, Alpha.a2, Alpha.a3, '
                    'Beta.b1, Beta.b2, Beta.b3 FROM '
                    '(SELECT Alpha.a1, Alpha.a2, Alpha.a3 FROM Alpha) AS Alpha '
                    'CROSS JOIN '
                    '(SELECT Beta.b1, Beta.b2, Beta.b3 FROM Beta) AS Beta '
                    'WHERE a1 = b1']
        actual = self.translate(ra)
        self.assertEqual(expected, actual)


class TestSet:
    def test_simple(self):
        ra = 'Gamma {operator} GammaTwin;'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0])
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT g1, g2 FROM ('
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
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT g1, g2 FROM ('
                    'SELECT g1, g2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    '{operator} ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) AS _{name1} '
                    '{operator} ALL '
                    'SELECT GammaPrime.g1, GammaPrime.g2 FROM GammaPrime) AS _{name2}'
                        .format(operator=self.sql_operator, name1=child_name, name2=root_name)]
        self.assertEqual(expected, actual)

    def test_select_simple(self):
        ra = '\\select_{{g1 = g2}} (Gamma {operator} GammaTwin);'.format(operator=self.ra_operator)
        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0].child)
        actual = sql_translator.translate(root_list, use_bag_semantics=True)
        expected = ['SELECT g1, g2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    '{operator} ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                    'AS _{name} WHERE g1 = g2'
                        .format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_project_simple(self):
        ra = '\\project_{{g2}} (Gamma {operator} GammaTwin);'.format(operator=self.ra_operator)
        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0].child)
        actual = sql_translator.translate(root_list, use_bag_semantics=True)
        expected = ['SELECT g2 FROM '
                    '(SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    '{operator} ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                    'AS _{name}'
                        .format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_project_left(self):
        ra = '\\project_{{g1, g2}} GammaPrime {operator} Gamma;'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0])
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT g1, g2 FROM '
                    '(SELECT GammaPrime.g1, GammaPrime.g2 FROM GammaPrime '
                    '{operator} ALL '
                    'SELECT Gamma.g1, Gamma.g2 FROM Gamma) AS _{name}'
                        .format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_rename_simple(self):
        ra = '\\rename_{{G}} (Gamma {operator} GammaTwin);'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0].child)
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT G.g1, G.g2 FROM '
                    '(SELECT g1, g2 FROM (SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    '{operator} ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) '
                    'AS _{name}) AS G(g1, g2)'
                        .format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)

    def test_rename_attributes(self):
        ra = '\\rename_{{G(a, b)}} (Gamma {operator} GammaTwin);'.format(operator=self.ra_operator)

        root_list = TreeBRD(self.grammar).build(instring=ra, schema=self.schema)
        name = id(root_list[0].child)
        actual = sql_translator.translate(root_list, use_bag_semantics=True)

        expected = ['SELECT G.a, G.b FROM '
                    '(SELECT g1, g2 FROM (SELECT Gamma.g1, Gamma.g2 FROM Gamma '
                    '{operator} ALL '
                    'SELECT GammaTwin.g1, GammaTwin.g2 FROM GammaTwin) AS _{name}) '
                    'AS G(a, b)'.format(operator=self.sql_operator, name=name)]
        self.assertEqual(expected, actual)


class TestUnion(TestSQL, TestSet):
    ra_operator = '\\union'
    sql_operator = 'UNION'


class TestDifference(TestSQL, TestSet):
    ra_operator = '\\difference'
    sql_operator = 'EXCEPT'


class TestIntersection(TestSQL, TestSet):
    grammar = ExtendedGrammar()
    ra_operator = '\\intersect'
    sql_operator = 'INTERSECT'