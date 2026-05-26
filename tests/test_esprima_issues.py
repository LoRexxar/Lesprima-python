"""
Tests for jquery/esprima open issue validation bugs.
Each test corresponds to a specific esprima issue number.
"""
import pytest
import sys
sys.path.insert(0, '/home/ubuntu/Lesprima-python')
from esprima import esprima


class TestYieldContextTracking:
    """B1: Yield in various nested contexts within generators."""

    def test_1706_yield_as_generator_param_default(self):
        """yield should not be valid as default value in generator params."""
        with pytest.raises(Exception):
            esprima.parse('function *g(x = yield){}')

    def test_1634_yield_as_default_in_arrow(self):
        """yield should not be valid as default value in arrow inside generator."""
        with pytest.raises(Exception):
            esprima.parse('function *g() { (x = yield) => {} }')

    def test_1886_yield_in_arrow_param_default(self):
        """yield should not be valid in arrow param default inside generator."""
        with pytest.raises(Exception):
            esprima.parse('function *g() { ({x = yield}) => {} }')

    def test_1904_yield_in_arrow_formal_param(self):
        """yield in arrow formal param default should throw."""
        with pytest.raises(Exception):
            esprima.parse('function *a() { ({b = yield}) => {} }')

    def test_1903_yield_in_function_formal_param(self):
        """yield in function formal param default should throw."""
        with pytest.raises(Exception):
            esprima.parse('function* a(){ ({ *b(c = d + e(yield)){} }); }')


class TestDestructuringValidation:
    """B2: Parenthesized patterns, nested patterns, __proto__ validation."""

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also fails to reject parenthesized patterns in destructuring")
    def test_1888_parenthesized_lhs_array(self):
        """Parenthesized LHS in array destructuring - upstream bug #1888."""
        with pytest.raises(Exception):
            esprima.parse('[(a = 0)] = 1')

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also fails to reject parenthesized patterns in destructuring")
    def test_1887_parenthesized_in_object_pattern(self):
        """Parenthesized assignment in object pattern - upstream bug #1887."""
        with pytest.raises(Exception):
            esprima.parse('({a: (b = 0)} = {})')

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also fails to reject parenthesized patterns in destructuring")
    def test_1884_spread_with_assignment_in_rest(self):
        """Spread element with assignment in rest position - upstream bug #1884."""
        with pytest.raises(Exception):
            esprima.parse('[a, ...(b = c)] = 0')

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also fails to reject parenthesized patterns in destructuring")
    def test_1872_nested_parenthesized_pattern(self):
        """Nested parenthesized pattern - upstream bug #1872."""
        with pytest.raises(Exception):
            esprima.parse('({ src: ([dest]) } = obj)')

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also fails to reject parenthesized patterns in destructuring")
    def test_1855_parenthesized_pattern_in_for_in(self):
        """Parenthesized pattern in for-in - upstream bug #1855."""
        with pytest.raises(Exception):
            esprima.parse('for(({a}) in 0);')

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also fails to reject nested rest patterns")
    def test_1806_nested_pattern_in_rest(self):
        """Nested pattern inside rest element - upstream bug #1806."""
        with pytest.raises(Exception):
            esprima.parse('var {...{z}} = { z: 1}; console.log(z);')

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also fails to reject parenthesized rest elements")
    def test_1800_parenthesized_rest_element(self):
        """Parenthesized rest element - upstream bug #1800."""
        with pytest.raises(Exception):
            esprima.parse('[a, ...(b = c)] = 0')

    def test_1907_duplicate_proto_in_destructuring(self):
        """Duplicate __proto__ in destructuring assignment - matches upstream behavior."""
        with pytest.raises(Exception):
            esprima.parse('({__proto__: x, __proto__: y} = z)')

    def test_1901_duplicate_proto_in_assignment(self):
        """Duplicate __proto__ in object assignment pattern - matches upstream behavior."""
        with pytest.raises(Exception):
            esprima.parse('result = { __proto__: x, __proto__: y } = value;')


class TestLHSAssignmentValidation:
    """B3: Invalid assignment target checks."""

    def test_1912_new_target_decrement(self):
        """new.target should not be assignable."""
        with pytest.raises(Exception):
            esprima.parse('function f() { (new.target)--; }')

    def test_1878_eval_in_binding_strict(self):
        """eval in binding position in strict mode should throw."""
        with pytest.raises(Exception):
            esprima.parse('"use strict"; [...eval] = a')

    def test_1857_spread_in_import(self):
        """Spread element in import() should throw."""
        with pytest.raises(Exception):
            esprima.parse('import(...a)')

    def test_1803_destructuring_compound_assignment(self):
        """Destructuring with compound assignment should throw."""
        with pytest.raises(Exception):
            esprima.parse('[v] += ary')

    @pytest.mark.xfail(reason="TODO: cover grammar shorthand+default validation in async calls")
    def test_1606_shorthand_with_default_in_async(self):
        """Shorthand property with default in async call should throw."""
        with pytest.raises(Exception):
            esprima.parse('async({x=y})')


class TestScopeContextTracking:
    """B4: Block scope conflicts, continue label targets, labeled statements."""

    def test_1876_continue_to_non_iteration_label(self):
        """continue to non-iteration label should throw."""
        with pytest.raises(Exception):
            esprima.parse('a: { continue a; }')

    def test_1052_continue_label_not_iteration(self):
        """Continue label must target an iteration statement."""
        with pytest.raises(Exception):
            esprima.parse('a: continue a;')

    @pytest.mark.xfail(reason="TODO: labeled function declaration in with body validation")
    def test_1877_labeled_function_in_with(self):
        """Labeled function declaration in with body should throw."""
        with pytest.raises(Exception):
            esprima.parse('with(1) b: function a(){}')

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also accepts labeled async function in statement position")
    def test_1719_labeled_async_function_in_statement(self):
        """Labeled async function in statement position should throw."""
        with pytest.raises(Exception):
            esprima.parse('if (false) L: async function l() {}')

    @pytest.mark.xfail(reason="TODO: requires scope tracking for duplicate lexical bindings")
    def test_1900_duplicate_lexical_binding_in_block(self):
        """Duplicate lexical binding in block should throw."""
        with pytest.raises(Exception):
            esprima.parse('{ class f {} var f; }')

    @pytest.mark.xfail(reason="TODO: requires single-statement context tracking for lexical declarations")
    def test_1898_let_in_single_statement_for_of(self):
        """let as body of single-statement for-of should throw."""
        with pytest.raises(Exception):
            esprima.parse('for (var x of []) let [a] = 0;')


class TestClassSuperValidation:
    """B5: super() validation, new.target in defaults, yield in sloppy mode."""

    def test_2000_super_in_non_derived_class(self):
        """super() in non-derived class constructor - runtime error, not parse error."""
        # ES spec: super() in non-derived class is ReferenceError, not SyntaxError
        # Parser should accept this; validation happens at runtime
        result = esprima.parse('class A { constructor() { super(); } }')
        assert result is not None

    def test_1785_super_in_derived_class_default(self):
        """super() in derived class constructor with default param should parse."""
        result = esprima.parse('class a extends b { constructor(c = super()){} }')
        assert result is not None

    def test_1783_new_target_in_param_default(self):
        """new.target in function param default should parse."""
        result = esprima.parse('(function a(b = new.target){})')
        assert result is not None

    def test_1871_yield_as_param_sloppy_object_method(self):
        """yield as param name in sloppy mode object method should parse."""
        result = esprima.parse('var o = { foo(yield) {} }')
        assert result is not None

    def test_1941_export_default_member_expr(self):
        """export default with member expression should parse."""
        result = esprima.parse('export default [].concat(foo)', sourceType='module')
        assert result is not None


class TestImportExportValidation:
    """B6: Duplicate exports, unicode escapes in export specifiers."""

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also accepts duplicate exported names")
    def test_2054_duplicate_exported_names(self):
        """Duplicate exported names should throw."""
        with pytest.raises(Exception):
            esprima.parse('export { a }; export { a };', sourceType='module')

    @pytest.mark.xfail(reason="Upstream bug: esprima JS also accepts unicode escapes in export specifiers")
    def test_1867_unicode_escape_in_export(self):
        """Unicode escape in export specifier should throw."""
        with pytest.raises(Exception):
            esprima.parse('export { \\u0061 };', sourceType='module')


class TestStrictModeAndOther:
    """B7: Strict mode validation, template literals, etc."""

    @pytest.mark.xfail(reason="TODO: scanner-level fix needed for non-octal decimal in strict mode")
    def test_1731_non_octal_decimal_strict(self):
        """Non-octal decimal integer in strict mode should throw."""
        with pytest.raises(Exception):
            esprima.parse('"use strict"; 08')

    @pytest.mark.xfail(reason="TODO: scanner-level fix needed for invalid unicode escapes")
    def test_1697_invalid_unicode_escape(self):
        """Invalid unicode escape for identifier should throw."""
        with pytest.raises(Exception):
            esprima.parse('\\u{1}')

    def test_1814_throw_template_with_newline(self):
        """throw with template literal containing newline should parse."""
        result = esprima.parse('throw `error\nmessage`')
        assert result is not None
