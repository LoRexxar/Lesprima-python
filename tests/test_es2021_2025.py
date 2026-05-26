# -*- coding: utf-8 -*-
"""
Tests for ES2021-ES2025 syntax features added to Lesprima-python.

Features tested:
- ES2021: Hashbang grammar (#!)
- ES2021: Numeric Separators (1_000_000)
- ES2021: Logical Assignment Operators (&&=, ||=, ??=)
- ES2022: Static Class Fields
- ES2022: Static Initialization Block
- ES2022: Private Fields (#x)
- ES2022: Private Methods (#method())
- ES2025: using declaration
- ES2025: await using declaration
- ES2025: Import Attributes (with { type: "json" })
- ES2025+: Decorators (@expr)
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from esprima import parse, Error as EsprimaError


# ============================================================
# ES2021 Features
# ============================================================

class TestHashbang(unittest.TestCase):
    """ES2021: Hashbang grammar (#! /usr/bin/env node)."""

    def test_hashbang_basic(self):
        r = parse('#! /usr/bin/env node\nconsole.log(1);')
        self.assertEqual(len(r.body), 1)
        # hashbang is consumed by scanner, body starts after it
        self.assertEqual(r.body[0].type, 'ExpressionStatement')

    def test_hashbang_with_code(self):
        r = parse('#!/usr/bin/env node\nlet x = 1;')
        self.assertEqual(len(r.body), 1)
        self.assertEqual(r.body[0].type, 'VariableDeclaration')

    def test_hashbang_not_in_module(self):
        """Hashbang should work in script mode."""
        r = parse('#! /bin/bash\n1;')
        self.assertEqual(len(r.body), 1)

    def test_no_hashbang(self):
        """Normal code without hashbang still works."""
        r = parse('let x = 1;')
        self.assertEqual(r.body[0].type, 'VariableDeclaration')


class TestNumericSeparators(unittest.TestCase):
    """ES2021: Numeric Separators (1_000_000)."""

    def test_integer_separator(self):
        r = parse('let x = 1_000_000;')
        self.assertEqual(r.body[0].declarations[0].init.value, 1000000)

    def test_binary_separator(self):
        r = parse('let x = 0b1010_1010;')
        self.assertEqual(r.body[0].declarations[0].init.value, 0b10101010)

    def test_hex_separator(self):
        r = parse('let x = 0xFF_FF;')
        self.assertEqual(r.body[0].declarations[0].init.value, 0xFFFF)

    def test_octal_separator(self):
        r = parse('let x = 0o77_77;')
        self.assertEqual(r.body[0].declarations[0].init.value, 0o7777)

    def test_float_separator(self):
        r = parse('let x = 1_000.000_1;')
        self.assertAlmostEqual(r.body[0].declarations[0].init.value, 1000.0001)

    def test_multiple_separators(self):
        r = parse('let x = 1_2_3_4;')
        self.assertEqual(r.body[0].declarations[0].init.value, 1234)

    def test_no_separator(self):
        """Normal numbers still work."""
        r = parse('let x = 1234;')
        self.assertEqual(r.body[0].declarations[0].init.value, 1234)


class TestLogicalAssignment(unittest.TestCase):
    """ES2021: Logical Assignment Operators (&&=, ||=, ??=)."""

    def test_and_assignment(self):
        r = parse('x &&= 1;')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'AssignmentExpression')
        self.assertEqual(expr.operator, '&&=')

    def test_or_assignment(self):
        r = parse('x ||= 1;')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'AssignmentExpression')
        self.assertEqual(expr.operator, '||=')

    def test_nullish_assignment(self):
        r = parse('x ??= 1;')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'AssignmentExpression')
        self.assertEqual(expr.operator, '??=')

    def test_logical_assignment_with_expression(self):
        r = parse('obj.prop &&= getValue();')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'AssignmentExpression')
        self.assertEqual(expr.operator, '&&=')
        self.assertEqual(expr.left.type, 'MemberExpression')

    def test_all_three(self):
        r = parse('a &&= 1; b ||= 2; c ??= 3;')
        self.assertEqual(r.body[0].expression.operator, '&&=')
        self.assertEqual(r.body[1].expression.operator, '||=')
        self.assertEqual(r.body[2].expression.operator, '??=')

    def test_normal_assignment_unchanged(self):
        r = parse('x = 1;')
        expr = r.body[0].expression
        self.assertEqual(expr.operator, '=')


# ============================================================
# ES2022 Features
# ============================================================

class TestStaticClassFields(unittest.TestCase):
    """ES2022: Static class fields and public instance fields."""

    def test_static_field_basic(self):
        r = parse('class A { static x = 1; }')
        prop = r.body[0].body.body[0]
        self.assertEqual(prop.type, 'ClassProperty')
        self.assertEqual(prop.key.name, 'x')
        self.assertTrue(prop.static)

    def test_static_field_with_expression(self):
        r = parse('class A { static x = foo(); }')
        prop = r.body[0].body.body[0]
        self.assertEqual(prop.value.type, 'CallExpression')

    def test_instance_field(self):
        r = parse('class A { x = 1; }')
        prop = r.body[0].body.body[0]
        self.assertEqual(prop.type, 'ClassProperty')
        self.assertEqual(prop.key.name, 'x')
        self.assertFalse(prop.static)

    def test_static_field_multiple(self):
        r = parse('class A { static x = 1; static y = 2; }')
        self.assertEqual(len(r.body[0].body.body), 2)
        self.assertTrue(r.body[0].body.body[0].static)
        self.assertTrue(r.body[0].body.body[1].static)


class TestStaticInitializationBlock(unittest.TestCase):
    """ES2022: Static initialization block (static { ... })."""

    def test_static_block_basic(self):
        r = parse('class A { static { console.log(1); } }')
        block = r.body[0].body.body[0]
        self.assertEqual(block.type, 'StaticBlock')
        self.assertEqual(len(block.body), 1)

    def test_static_block_multiple_statements(self):
        r = parse('class A { static { let x = 1; console.log(x); } }')
        block = r.body[0].body.body[0]
        self.assertEqual(block.type, 'StaticBlock')
        self.assertEqual(len(block.body), 2)

    def test_static_block_with_class_fields(self):
        r = parse('class A { static x = 1; static { this.y = 2; } }')
        body = r.body[0].body.body
        self.assertEqual(body[0].type, 'ClassProperty')
        self.assertEqual(body[1].type, 'StaticBlock')

    def test_static_block_empty(self):
        r = parse('class A { static {} }')
        block = r.body[0].body.body[0]
        self.assertEqual(block.type, 'StaticBlock')
        self.assertEqual(len(block.body), 0)


class TestPrivateFields(unittest.TestCase):
    """ES2022: Private class fields (#x)."""

    def test_private_field_declaration(self):
        r = parse('class A { #x = 1; }')
        prop = r.body[0].body.body[0]
        # #x fields are parsed as ClassProperty with key.name '#x'
        self.assertEqual(prop.type, 'ClassProperty')
        self.assertEqual(prop.key.name, '#x')

    def test_private_field_access(self):
        r = parse('class A { #x = 1; get() { return this.#x; } }')
        body = r.body[0].body.body
        self.assertEqual(body[0].type, 'ClassProperty')
        self.assertEqual(body[0].key.name, '#x')
        # Method should have access to #x
        self.assertEqual(body[1].type, 'ClassMethod')

    def test_private_field_static(self):
        r = parse('class A { static #x = 1; }')
        prop = r.body[0].body.body[0]
        self.assertEqual(prop.type, 'ClassProperty')
        self.assertTrue(prop.static)

    def test_private_field_no_init(self):
        r = parse('class A { #x; }')
        prop = r.body[0].body.body[0]
        self.assertEqual(prop.type, 'ClassProperty')
        self.assertEqual(prop.key.name, '#x')


class TestPrivateMethods(unittest.TestCase):
    """ES2022: Private class methods (#method())."""

    def test_private_method_basic(self):
        r = parse('class A { #method() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertEqual(method.key.name, '#method')

    def test_private_getter(self):
        r = parse('class A { get #x() { return 1; } }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertEqual(method.kind, 'get')
        self.assertEqual(method.key.name, '#x')

    def test_private_setter(self):
        r = parse('class A { set #x(v) { this._v = v; } }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertEqual(method.kind, 'set')
        self.assertEqual(method.key.name, '#x')

    def test_private_method_static(self):
        r = parse('class A { static #method() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertTrue(method.static)
        self.assertEqual(method.key.name, '#method')

    def test_private_method_with_public(self):
        r = parse('class A { #private() {} public() {} }')
        body = r.body[0].body.body
        self.assertEqual(body[0].key.name, '#private')
        self.assertEqual(body[1].key.name, 'public')


# ============================================================
# ES2025 Features
# ============================================================

class TestUsingDeclaration(unittest.TestCase):
    """ES2025: using declaration for explicit resource management."""

    def test_using_basic(self):
        r = parse('using x = getResource();')
        decl = r.body[0]
        self.assertEqual(decl.type, 'VariableDeclaration')
        self.assertEqual(decl.kind, 'using')
        self.assertEqual(decl.declarations[0].id.name, 'x')

    def test_using_multiple(self):
        r = parse('using a = foo(), b = bar();')
        decl = r.body[0]
        self.assertEqual(decl.kind, 'using')
        self.assertEqual(len(decl.declarations), 2)

    def test_using_inside_block(self):
        r = parse('{ using x = foo(); }')
        decl = r.body[0].body[0]
        self.assertEqual(decl.type, 'VariableDeclaration')
        self.assertEqual(decl.kind, 'using')

    def test_using_inside_function(self):
        r = parse('function f() { using x = foo(); }')
        decl = r.body[0].body.body[0]
        self.assertEqual(decl.kind, 'using')

    def test_using_with_complex_expression(self):
        r = parse('using conn = await getConnection();', sourceType='module')
        decl = r.body[0]
        self.assertEqual(decl.kind, 'using')
        self.assertEqual(decl.declarations[0].init.type, 'AwaitExpression')


class TestAwaitUsingDeclaration(unittest.TestCase):
    """ES2025: await using declaration for async disposable resources."""

    def test_await_using_basic(self):
        r = parse('await using x = getResource();', sourceType='module')
        decl = r.body[0]
        self.assertEqual(decl.type, 'VariableDeclaration')
        self.assertEqual(decl.kind, 'using')
        self.assertEqual(decl.declarations[0].id.name, 'x')

    def test_await_using_inside_block(self):
        r = parse('{ await using x = foo(); }', sourceType='module')
        decl = r.body[0].body[0]
        self.assertEqual(decl.kind, 'using')

    def test_await_using_inside_function(self):
        r = parse('async function f() { await using x = foo(); }')
        decl = r.body[0].body.body[0]
        self.assertEqual(decl.kind, 'using')

    def test_await_expression_not_confused_with_await_using(self):
        """Ensure 'await expr;' in async function is NOT parsed as 'await using'."""
        r = parse('async function foo() { await bar(); }')
        stmt = r.body[0].body.body[0]
        self.assertEqual(stmt.type, 'ExpressionStatement')
        self.assertEqual(stmt.expression.type, 'AwaitExpression')

    def test_await_normal_in_async(self):
        """Normal await expression still works in async functions."""
        r = parse('async function foo() { const x = await bar(); }')
        stmt = r.body[0].body.body[0]
        self.assertEqual(stmt.type, 'VariableDeclaration')


class TestImportAttributes(unittest.TestCase):
    """ES2025: Import Attributes (import ... with { type: "json" })."""

    def test_import_attribute_basic(self):
        r = parse('import data from "./data.json" with { type: "json" };', sourceType='module')
        decl = r.body[0]
        self.assertEqual(decl.type, 'ImportDeclaration')
        self.assertIsNotNone(decl.attributes)
        self.assertEqual(len(decl.attributes), 1)
        self.assertEqual(decl.attributes[0].key.name, 'type')
        self.assertEqual(decl.attributes[0].value.value, 'json')

    def test_import_attribute_multiple(self):
        r = parse('import data from "./data.json" with { type: "json", source: "local" };',
                   sourceType='module')
        decl = r.body[0]
        self.assertEqual(len(decl.attributes), 2)

    def test_import_attribute_string_key(self):
        r = parse('import data from "./data.json" with { "type": "json" };',
                   sourceType='module')
        decl = r.body[0]
        self.assertEqual(decl.attributes[0].key.value, 'type')

    def test_import_without_attributes(self):
        """Normal import still works without attributes."""
        r = parse('import foo from "./foo.js";', sourceType='module')
        decl = r.body[0]
        self.assertEqual(decl.type, 'ImportDeclaration')
        self.assertIsNone(decl.attributes)

    def test_import_namespace_with_attributes(self):
        r = parse('import * as data from "./data.json" with { type: "json" };',
                   sourceType='module')
        decl = r.body[0]
        self.assertEqual(decl.type, 'ImportDeclaration')
        self.assertIsNotNone(decl.attributes)

    def test_import_named_with_attributes(self):
        r = parse('import { foo } from "./foo.js" with { type: "javascript" };',
                   sourceType='module')
        decl = r.body[0]
        self.assertEqual(decl.type, 'ImportDeclaration')
        self.assertIsNotNone(decl.attributes)


class TestDecorators(unittest.TestCase):
    """ES2025+: Decorator syntax (@expr) for classes and class elements."""

    # --- Class-level decorators ---

    def test_class_decorator_simple(self):
        r = parse('@log class A {}')
        cls = r.body[0]
        self.assertEqual(cls.type, 'ClassDeclaration')
        self.assertEqual(len(cls.decorators), 1)
        self.assertEqual(cls.decorators[0].type, 'Decorator')
        self.assertEqual(cls.decorators[0].expression.name, 'log')

    def test_class_decorator_multiple(self):
        r = parse('@log @sealed class A {}')
        cls = r.body[0]
        self.assertEqual(len(cls.decorators), 2)
        self.assertEqual(cls.decorators[0].expression.name, 'log')
        self.assertEqual(cls.decorators[1].expression.name, 'sealed')

    def test_class_decorator_factory(self):
        r = parse('@decoratorFactory("arg") class A {}')
        dec = r.body[0].decorators[0]
        self.assertEqual(dec.expression.type, 'CallExpression')
        self.assertEqual(dec.expression.callee.name, 'decoratorFactory')

    def test_class_decorator_member_expression(self):
        r = parse('@decorators.log class A {}')
        dec = r.body[0].decorators[0]
        self.assertEqual(dec.expression.type, 'MemberExpression')
        self.assertEqual(dec.expression.object.name, 'decorators')
        self.assertEqual(dec.expression.property.name, 'log')

    def test_class_decorator_chained_member(self):
        r = parse('@a.b.c class A {}')
        dec = r.body[0].decorators[0]
        self.assertEqual(dec.expression.type, 'MemberExpression')

    def test_class_decorator_with_extends(self):
        r = parse('@log class A extends B {}')
        cls = r.body[0]
        self.assertEqual(len(cls.decorators), 1)
        self.assertIsNotNone(cls.superClass)

    # --- Class expression decorators ---

    def test_class_expression_decorator(self):
        r = parse('const A = @log class {};')
        cls = r.body[0].declarations[0].init
        self.assertEqual(cls.type, 'ClassExpression')
        self.assertEqual(len(cls.decorators), 1)
        self.assertEqual(cls.decorators[0].expression.name, 'log')

    # --- Method decorators ---

    def test_method_decorator_simple(self):
        r = parse('class A { @readonly method() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertEqual(len(method.decorators), 1)
        self.assertEqual(method.decorators[0].expression.name, 'readonly')

    def test_method_decorator_multiple(self):
        r = parse('class A { @bound @log arrow() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(len(method.decorators), 2)
        self.assertEqual(method.decorators[0].expression.name, 'bound')
        self.assertEqual(method.decorators[1].expression.name, 'log')

    def test_method_decorator_factory(self):
        r = parse('class A { @debounce(100) method() {} }')
        method = r.body[0].body.body[0]
        dec = method.decorators[0]
        self.assertEqual(dec.expression.type, 'CallExpression')
        self.assertEqual(dec.expression.callee.name, 'debounce')

    # --- Property decorators ---

    def test_property_decorator(self):
        r = parse('class A { @log x = 1; }')
        prop = r.body[0].body.body[0]
        self.assertEqual(prop.type, 'ClassProperty')
        self.assertEqual(len(prop.decorators), 1)
        self.assertEqual(prop.decorators[0].expression.name, 'log')

    # --- Getter/setter decorators ---

    def test_getter_decorator(self):
        r = parse('class A { @log get x() { return 1; } }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertEqual(method.kind, 'get')
        self.assertEqual(len(method.decorators), 1)

    def test_setter_decorator(self):
        r = parse('class A { @validate set x(v) { this._x = v; } }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.kind, 'set')
        self.assertEqual(len(method.decorators), 1)

    # --- Static method decorators ---

    def test_static_method_decorator(self):
        r = parse('class A { @log static method() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(method.type, 'ClassMethod')
        self.assertTrue(method.static)
        self.assertEqual(len(method.decorators), 1)

    # --- Mixed decorators ---

    def test_class_and_method_decorators(self):
        r = parse('@log class A { @readonly method() {} }')
        cls = r.body[0]
        method = cls.body.body[0]
        self.assertEqual(len(cls.decorators), 1)
        self.assertEqual(len(method.decorators), 1)

    # --- No decorators ---

    def test_no_decorator_class(self):
        r = parse('class A { method() {} }')
        cls = r.body[0]
        self.assertEqual(len(cls.decorators), 0)

    def test_no_decorator_method(self):
        r = parse('class A { method() {} }')
        method = r.body[0].body.body[0]
        self.assertEqual(len(method.decorators), 0)


if __name__ == '__main__':
    unittest.main()
