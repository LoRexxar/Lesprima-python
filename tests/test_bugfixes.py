# -*- coding: utf-8 -*-
"""
Tests for pre-existing bug fixes in Lesprima-python.

Bugs fixed:
1. Token.NumericLiteral is int not tuple (typ in Token.NumericLiteral -> typ is Token.NumericLiteral)
2. Node.Property missing (added Property node class)
3. Syntax.Literal doesn't exist (replaced with Syntax.StringLiteral)
4. ClassMethod.__init__ missing id parameter (added id=None)
5. parseClassElement calling ClassMethod with wrong argument count
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from esprima import parse, Error as EsprimaError


class TestTokenNumericLiteralFix(unittest.TestCase):
    """Bug: typ in Token.NumericLiteral raised TypeError (int not iterable)."""

    def test_numeric_property_key(self):
        r = parse('({0: "zero"})')
        self.assertEqual(r.body[0].expression.type, 'ObjectExpression')

    def test_class_with_numeric_method_name(self):
        r = parse('class Foo { 1() {} }')
        self.assertEqual(r.body[0].body.body[0].type, 'ClassMethod')


class TestNodePropertyFix(unittest.TestCase):
    """Bug: Node.Property was missing, breaking object destructuring."""

    def test_object_destructuring(self):
        r = parse('const {a, b} = obj;')
        self.assertEqual(r.body[0].declarations[0].id.type, 'ObjectPattern')

    def test_object_destructuring_rename(self):
        r = parse('const {a: b} = obj;')
        pat = r.body[0].declarations[0].id
        self.assertEqual(pat.type, 'ObjectPattern')

    def test_object_shorthand_property(self):
        r = parse('const a = 1; const obj = {a};')
        self.assertEqual(r.body[1].declarations[0].init.type, 'ObjectExpression')


class TestSyntaxLiteralFix(unittest.TestCase):
    """Bug: Syntax.Literal doesn't exist in this project (split into StringLiteral etc)."""

    def test_class_constructor(self):
        r = parse('class Foo { constructor() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.kind, 'constructor')

    def test_class_with_string_constructor(self):
        r = parse('class Foo { "constructor"() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.kind, 'constructor')

    def test_use_strict_directive(self):
        r = parse('"use strict"; var x = 1;')
        self.assertEqual(r.body[0].type, 'ExpressionStatement')


class TestClassMethodFix(unittest.TestCase):
    """Bug: ClassMethod.__init__ missing id parameter, parseClassElement wrong arg count."""

    def test_class_method(self):
        r = parse('class Foo { method() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertEqual(method.kind, 'method')

    def test_class_async_method(self):
        r = parse('class Foo { async method() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertTrue(method.is_async)

    def test_class_generator_method(self):
        r = parse('class Foo { *gen() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertTrue(method.generator)

    def test_class_getter(self):
        r = parse('class Foo { get x() { return 1; } }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.kind, 'get')

    def test_class_setter(self):
        r = parse('class Foo { set x(v) { } }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.kind, 'set')

    def test_class_static_method(self):
        r = parse('class Foo { static bar() {} }')
        method = r.body[0].body.body[0]
        self.assertTrue(method.static)


class TestRegression(unittest.TestCase):
    """Ensure the original test suite doesn't regress after fixes."""

    def test_basic_variable(self):
        r = parse('var x = 1;')
        self.assertEqual(r.body[0].type, 'VariableDeclaration')

    def test_function_declaration(self):
        r = parse('function foo() { return 1; }')
        self.assertEqual(r.body[0].type, 'FunctionDeclaration')

    def test_object_expression(self):
        r = parse('const obj = {a: 1, b: 2};')
        self.assertEqual(r.body[0].declarations[0].init.type, 'ObjectExpression')

    def test_array_destructuring(self):
        r = parse('const [a, b] = [1, 2];')
        self.assertEqual(r.body[0].declarations[0].id.type, 'ArrayPattern')

    def test_template_literal(self):
        r = parse('`hello ${world}`')
        self.assertEqual(r.body[0].expression.type, 'TemplateLiteral')


if __name__ == '__main__':
    unittest.main()
