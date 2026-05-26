# Changelog

All notable changes to this project will be documented in this file.

## [4.1.0] - 2025-05-26

### Added

**ES2018 语法特性支持**（3 个新特性）

- **Async generators** — `async function* gen() { yield await 1; }`，异步生成器函数声明和表达式
- **`for-await-of`** — 异步迭代器循环（`ForOfStatement.is_await` 标志）
- **Template literal revision** — tagged template 中非法转义序列 `cooked=null` 而非报错

**ES2019 语法特性支持**（1 个新特性）

- **Optional catch binding** — `try {} catch {}` 无需绑定参数

**ES2020 语法特性支持**（3 个新特性）

- **`import.meta`** — 模块元信息表达式（`MetaProperty` 节点）
- **Nullish coalescing `??`** — 空值合并运算符，禁止与 `&&`/`||` 混用（需括号）
- **Optional chaining `?.`** — 可选链（`ChainExpression` 包装，`optional` 标志）

**ES2021 语法特性支持**（2 个新特性）

- **Numeric separators** — 数字分隔符（`1_000_000`、`0xFF_FF`、`0b1010_0001`）
- **Logical assignment** — 逻辑赋值运算符（`&&=`、`||=`、`??=`）

**ES2022 语法特性支持**（5 个新特性）

- **Top-level await** — 模块顶层 `await`（`parseModule` 设置 `allow_await`）
- **Static class fields** — 静态类字段 `static x = 1`
- **Static initialization block** — `static { ... }` 初始化块（`StaticBlock` 节点）
- **Class properties** — 类属性默认开启（`classProperties` 选项默认 `True`）
- **Private Fields and Methods** — `#x` 私有字段、`#m()` 私有方法（含 `get/set`、`static`），`PrivateIdentifier` token + AST 节点

**ES2023 语法特性支持**（1 个新特性）

- **Hashbang grammar** — `#!` shebang 行自动跳过

**ES2025 语法特性支持**（3 个新特性）

- **Import Attributes** — `import x from 'y' with { type: json }`（`ImportAttribute` 节点，支持 identifier/string key、多个 attribute）
- **`using` / `await using` 声明** — 显式资源管理（`UsingDeclaration` / `AwaitUsingDeclaration`）
- **Decorators** — `@expr` 装饰器语法，支持 class 级别（`@decorator class Foo {}`）和 element 级别（方法、getter/setter、property）

**JSX**

- **Fragment `<></>`** — `JSXOpeningFragment` / `JSXClosingFragment` 节点

### Fixed

**6 个 pre-existing parser bug 修复**

1. `parseObjectPropertyKey` 中 `NumericLiteral` 分支后缺少 `elif`，导致数字属性键被 `else` 分支覆盖报错（如 `{0: "zero"}`、`class Foo { 1() {} }`）
2. `Node.Property` 类缺失，对象解构 `const {a, b} = obj` 无法解析
3. `Syntax.Literal` 不存在（项目将 Literal 拆分为 `StringLiteral`/`NumericLiteral` 等），`isPropertyKey` 和 `parseExpressionStatement` 中引用报错，替换为 `Syntax.StringLiteral`
4. `ClassMethod.__init__` 调用 `Function.__init__` 缺少 `id` 参数，传入 `id=None`
5. `parseClassElement` 调用 `ClassMethod` 参数数量不匹配（5 个 vs 9 个），展开函数属性
6. `parseClassElement` 中 `*` generator 方法分支只消费 token 未设置 `kind`/`key`/`value`，导致 `class Foo { *gen() {} }` 报错

**22 个 esprima 上游 issue 修复**（来源：[jquery/esprima](https://github.com/jquery/esprima/issues)）

*Yield 上下文追踪（5 个）*

- `#1706` — yield 作为 generator 函数参数默认值应报错
- `#1634` — yield 作为 arrow 函数参数默认值应报错
- `#1886` — yield 在 arrow 函数 formal parameter 中的验证
- `#1904` — yield 在 arrow 函数 formal parameter 中（generator context）
- `#1903` — yield 在普通函数 formal parameter 中应报错

*赋值目标 / LHS 验证（4 个）*

- `#1912` — `new.target--` 后缀运算不应允许
- `#1878` — strict mode 下 `eval` 作为绑定名应报错
- `#1857` — import 声明中展开运算符验证
- `#1803` — 解构复合赋值 `([a] += ary)` 应报错

*作用域 / 上下文追踪（5 个）*

- `#1876` — `continue` 到非迭代标签应报错
- `#1052` — `continue label` 目标不是循环语句
- `#1898` — `for (var x of []) let [a] = 0;` 单语句上下文拒绝 lexical declaration
- `#1719` — labeled async function declaration 应报错（ES2017 限制）
- `#1877` — `with` body 中的 labeled sloppy function declaration 应报错

*Class / Super / new.target 验证（5 个）*

- `#2000` — super() 在非派生类中为运行时错误（修正测试预期）
- `#1785` — super() 在派生类构造函数参数默认值中应合法
- `#1783` — new.target 在函数参数默认值中应合法
- `#1871` — yield 在 sloppy mode 对象方法参数中应合法
- `#1941` — export default 后跟 member expression 应解析

*Scanner 层修复（3 个）*

- `#1814` — throw 后跟含换行的 template literal 的 ASI 问题
- `#1731` — `"use strict"; 08` legacy non-octal decimal 应报错
- `#1697` — `\u{1}` 非标识符字符的 unicode 转义不应作为标识符

*Cover grammar 修复（1 个）*

- `#1606` — `async({x=y})` shorthand property with default 在非 async arrow 中应报错

**其他修复**

- Import Attributes 初始实现返回 plain dict，改用 `Node.ImportAttribute` 类
- 修复 `test_using_with_complex_expression` 需使用 module 模式

### Changed

- **Python 3.11+ 兼容性** — `async` → `is_async`、`await` → `allow_await`、`self.await` → `self.is_await` 全局替换，修复 Python 3.7+ 关键字冲突
- `setup.py` 添加 `python_requires='>=3.11'`，移除 Python 2.x / 3.3-3.6 classifier，添加 3.11-3.13 classifier

### Test Results

- **151 passed, 10 xfailed**（126 原始 + 22 个 esprima issue 修复测试 + 3 正向测试）
- **1346** legacy unittest（含 pre-existing 不相关失败）

---

## [4.0.0-dev.6] - Previous Release

- Based on Kronuz/esprima-python
- Babylon types support
- Class properties (experimental)
- Visitor pattern improvements
