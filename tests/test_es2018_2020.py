# -*- coding: utf-8 -*-
"""
Tests for ES2018-ES2020 syntax features added to Lesprima-python.

Features tested:
- ES2019: Optional catch binding
- ES2020: import.meta
- ES2020: Nullish Coalescing (??)
- ES2018: Async generators
- ES2018: for-await-of
- ES2018: JSX Fragment (<></>)
- ES2020: Optional Chaining (?.)
- ES2018: Template Literal Revision
- Python 3.11+ compatibility (async/await keyword fixes)
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from esprima import parse, Error as EsprimaError


class TestOptionalCatchBinding(unittest.TestCase):
    """ES2019: catch without binding parameter."""

    def test_catch_without_param(self):
        r = parse('try { foo(); } catch { bar(); }')
        handler = r.body[0].handler
        self.assertIsNone(handler.param)

    def test_catch_with_param(self):
        r = parse('try { foo(); } catch(e) { bar(); }')
        handler = r.body[0].handler
        self.assertEqual(handler.param.name, 'e')

    def test_catch_finally_no_param(self):
        r = parse('try { a(); } catch { b(); } finally { c(); }')
        self.assertIsNone(r.body[0].handler.param)
        self.assertIsNotNone(r.body[0].finalizer)

    def test_catch_finally_with_param(self):
        r = parse('try { a(); } catch(e) { b(e); } finally { c(); }')
        self.assertEqual(r.body[0].handler.param.name, 'e')
        self.assertIsNotNone(r.body[0].finalizer)


class TestImportMeta(unittest.TestCase):
    """ES2020: import.meta expression."""

    def test_import_meta_url(self):
        r = parse('import.meta.url', sourceType='module')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'MemberExpression')
        self.assertEqual(expr.object.type, 'MetaProperty')

    def test_import_meta_assignment(self):
        r = parse('const x = import.meta.url;', sourceType='module')
        init = r.body[0].declarations[0].init
        self.assertEqual(init.type, 'MemberExpression')
        self.assertEqual(init.object.type, 'MetaProperty')

    def test_import_call_still_works(self):
        r = parse('import("module.js")', sourceType='module')
        self.assertEqual(r.body[0].expression.type, 'CallExpression')


class TestNullishCoalescing(unittest.TestCase):
    """ES2020: Nullish coalescing operator (??)."""

    def test_basic_nullish(self):
        r = parse('const x = a ?? b;')
        init = r.body[0].declarations[0].init
        self.assertEqual(init.type, 'BinaryExpression')
        self.assertEqual(init.operator, '??')

    def test_chained_nullish(self):
        r = parse('const x = a ?? b ?? c;')
        init = r.body[0].declarations[0].init
        self.assertEqual(init.operator, '??')
        self.assertEqual(init.left.operator, '??')

    def test_nullish_with_ternary(self):
        r = parse('const x = a ? b : c ?? d;')
        init = r.body[0].declarations[0].init
        self.assertEqual(init.type, 'ConditionalExpression')

    def test_nullish_mixed_or_with_parens(self):
        r = parse('const x = (a || b) ?? c;')
        init = r.body[0].declarations[0].init
        self.assertEqual(init.operator, '??')
        self.assertEqual(init.left.operator, '||')

    def test_nullish_mixed_and_with_parens(self):
        r = parse('const x = a ?? (b && c);')
        init = r.body[0].declarations[0].init
        self.assertEqual(init.operator, '??')
        self.assertEqual(init.right.operator, '&&')

    def test_nullish_mixed_without_parens_errors(self):
        with self.assertRaises(EsprimaError):
            parse('const x = a || b ?? c;')

    def test_nullish_mixed_and_without_parens_errors(self):
        with self.assertRaises(EsprimaError):
            parse('const x = a ?? b && c;')


class TestAsyncGenerators(unittest.TestCase):
    """ES2018: Async generator functions."""

    def test_async_generator_declaration(self):
        r = parse('async function* gen() { yield await 1; }')
        func = r.body[0]
        self.assertEqual(func.type, 'FunctionDeclaration')
        self.assertTrue(func.generator)

    def test_async_generator_expression(self):
        r = parse('let f = async function*() { yield 1; };')
        func = r.body[0].declarations[0].init
        self.assertEqual(func.type, 'FunctionExpression')
        self.assertTrue(func.generator)

    def test_normal_async_function_not_generator(self):
        r = parse('async function foo() { await bar(); }')
        func = r.body[0]
        self.assertEqual(func.type, 'FunctionDeclaration')
        self.assertFalse(func.generator)

    def test_normal_generator_not_async(self):
        r = parse('function* gen() { yield 1; }')
        func = r.body[0]
        self.assertEqual(func.type, 'FunctionDeclaration')
        self.assertTrue(func.generator)


class TestForAwaitOf(unittest.TestCase):
    """ES2018: for-await-of loop."""

    def test_for_await_of(self):
        r = parse('async function f() { for await (let x of stream) { } }')
        body = r.body[0].body.body[0]
        self.assertEqual(body.type, 'ForOfStatement')
        self.assertTrue(body.is_await)

    def test_for_of_not_await(self):
        r = parse('for (let x of arr) { }')
        body = r.body[0]
        self.assertEqual(body.type, 'ForOfStatement')
        self.assertFalse(body.is_await)

    def test_for_in_unchanged(self):
        r = parse('for (let x in obj) { }')
        self.assertEqual(r.body[0].type, 'ForInStatement')


class TestJSXFragment(unittest.TestCase):
    """JSX Fragment <></> support."""

    def test_empty_fragment(self):
        r = parse('<></>', jsx=True)
        el = r.body[0].expression
        self.assertEqual(el.type, 'JSXElement')
        self.assertEqual(el.openingElement.type, 'JSXOpeningFragment')
        self.assertEqual(el.closingElement.type, 'JSXClosingFragment')

    def test_fragment_with_children(self):
        r = parse('<>hello<div/></>', jsx=True)
        el = r.body[0].expression
        self.assertEqual(el.type, 'JSXElement')
        self.assertEqual(len(el.children), 2)

    def test_normal_jsx_unchanged(self):
        r = parse('<div>hello</div>', jsx=True)
        el = r.body[0].expression
        self.assertEqual(el.type, 'JSXElement')
        self.assertEqual(el.openingElement.type, 'JSXOpeningElement')


class TestOptionalChaining(unittest.TestCase):
    """ES2020: Optional chaining operator (?.)."""

    def test_optional_property(self):
        r = parse('a?.b')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'ChainExpression')
        self.assertEqual(expr.expression.type, 'MemberExpression')
        self.assertTrue(expr.expression.optional)

    def test_optional_computed(self):
        r = parse('a?.[0]')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'ChainExpression')
        self.assertEqual(expr.expression.type, 'MemberExpression')
        self.assertTrue(expr.expression.optional)
        self.assertTrue(expr.expression.computed)

    def test_optional_call(self):
        r = parse('a?.()')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'ChainExpression')
        self.assertEqual(expr.expression.type, 'CallExpression')
        self.assertTrue(expr.expression.optional)

    def test_optional_method_call(self):
        r = parse('a?.b()')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'ChainExpression')
        # .b is optional, () is not
        inner = expr.expression
        self.assertEqual(inner.type, 'CallExpression')
        self.assertFalse(inner.optional)
        self.assertEqual(inner.callee.type, 'MemberExpression')
        self.assertTrue(inner.callee.optional)

    def test_optional_chain_long(self):
        r = parse('a?.b?.c')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'ChainExpression')
        self.assertEqual(expr.expression.optional, True)
        self.assertEqual(expr.expression.object.optional, True)

    def test_normal_member_not_optional(self):
        r = parse('a.b')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'MemberExpression')
        self.assertFalse(expr.optional)

    def test_normal_call_not_optional(self):
        r = parse('a()')
        expr = r.body[0].expression
        self.assertEqual(expr.type, 'CallExpression')
        self.assertFalse(expr.optional)


class TestTemplateLiteralRevision(unittest.TestCase):
    """ES2018: Template literal revision (invalid escapes in tagged templates)."""

    def test_tagged_invalid_escape_cooked_null(self):
        r = parse('tag`hello \\1`')
        quasi = r.body[0].expression.quasi.quasis[0]
        self.assertIsNone(quasi.value.cooked)

    def test_tagged_invalid_hex_escape_cooked_null(self):
        r = parse('tag`hello \\x`')
        quasi = r.body[0].expression.quasi.quasis[0]
        self.assertIsNone(quasi.value.cooked)

    def test_nontagged_invalid_escape_errors(self):
        with self.assertRaises(EsprimaError):
            parse('`hello \\1`')

    def test_normal_template_still_works(self):
        r = parse('`hello ${world}`')
        self.assertEqual(r.body[0].expression.type, 'TemplateLiteral')

    def test_tagged_normal_template(self):
        r = parse('tag`hello ${world}`')
        self.assertEqual(r.body[0].expression.type, 'TaggedTemplateExpression')


class TestPython311Compat(unittest.TestCase):
    """Python 3.11+ compatibility: async/await are keywords."""

    def test_basic_parse(self):
        r = parse('var x = 1;')
        self.assertEqual(r.type, 'Program')

    def test_async_function(self):
        r = parse('async function foo() { await bar(); }')
        self.assertEqual(r.body[0].type, 'FunctionDeclaration')

    def test_arrow_function(self):
        r = parse('let f = (x) => x + 1;')
        self.assertEqual(r.body[0].type, 'VariableDeclaration')

    def test_async_arrow(self):
        r = parse('let f = async (x) => x;')
        self.assertEqual(r.body[0].type, 'VariableDeclaration')


if __name__ == '__main__':
    unittest.main()
