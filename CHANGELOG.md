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

**测试**

- `tests/test_es2018_2020.py` — 40 个测试覆盖 ES2018-ES2020 全部 8 个新特性
- `tests/test_es2021_2025.py` — 67 个测试覆盖 ES2021-ES2025 全部新特性（含 Private Fields/Methods、Import Attributes、using/await using、Decorators）
- `tests/test_bugfixes.py` — 19 个测试覆盖 bug 修复 + 回归验证

**CI/CD**

- 添加 GitHub Actions CI（`.github/workflows/ci.yml`）
- Python 3.11 / 3.12 / 3.13 矩阵测试
- 自动运行新特性测试、bugfix 测试、legacy 测试套件

### Fixed

**6 个 pre-existing parser bug 修复**

1. `parseObjectPropertyKey` 中 `NumericLiteral` 分支后缺少 `elif`，导致数字属性键被 `else` 分支覆盖报错（如 `{0: "zero"}`、`class Foo { 1() {} }`）
2. `Node.Property` 类缺失，对象解构 `const {a, b} = obj` 无法解析
3. `Syntax.Literal` 不存在（项目将 Literal 拆分为 `StringLiteral`/`NumericLiteral` 等），`isPropertyKey` 和 `parseExpressionStatement` 中引用报错，替换为 `Syntax.StringLiteral`
4. `ClassMethod.__init__` 调用 `Function.__init__` 缺少 `id` 参数，传入 `id=None`
5. `parseClassElement` 调用 `ClassMethod` 参数数量不匹配（5 个 vs 9 个），展开函数属性
6. `parseClassElement` 中 `*` generator 方法分支只消费 token 未设置 `kind`/`key`/`value`，导致 `class Foo { *gen() {} }` 报错

**其他修复**

- Import Attributes 初始实现返回 plain dict，改用 `Node.ImportAttribute` 类
- 修复 `test_using_with_complex_expression` 需使用 module 模式

### Changed

- **Python 3.11+ 兼容性** — `async` → `is_async`、`await` → `allow_await`、`self.await` → `self.is_await` 全局替换，修复 Python 3.7+ 关键字冲突
- `setup.py` 添加 `python_requires='>=3.11'`，移除 Python 2.x / 3.3-3.6 classifier，添加 3.11-3.13 classifier

### Modified Files

| 文件 | 改动 |
|------|------|
| `esprima/parser.py` | ES2018-ES2025 全部新特性 parser 逻辑 + 6 个 bug 修复 + 逻辑赋值 + static block + private fields/methods + import attributes + using/await using + decorators |
| `esprima/scanner.py` | `??` token 识别 + `??=` 三字符 token + template literal revision (`notEscapeSequenceHead`) + hashbang 跳过 + numeric separators + `#` private identifier 扫描 |
| `esprima/nodes.py` | `ChainExpression`、`Property`、`StaticBlock`、`PrivateIdentifier`、`ImportAttribute` 节点类 + `ForOfStatement.is_await` + `ClassMethod` id 修复 + `ImportDeclaration.attributes` |
| `esprima/syntax.py` | `ChainExpression`、`StaticBlock`、`ClassProperty`、`PrivateIdentifier`、`ImportAttribute` 枚举常量 |
| `esprima/token.py` | 新增 `PrivateIdentifier` token type |
| `esprima/esprima.py` | `classProperties` 默认 `True` |
| `esprima/messages.py` | `NullishCoalescingNotAllowed`、`CannotUseImportMetaOutsideAModule`、`InvalidTaggedTemplateOnOptionalChain` |
| `esprima/jsx_syntax.py` | `JSXOpeningFragment`、`JSXClosingFragment` 枚举 |
| `esprima/jsx_nodes.py` | `JSXOpeningFragment`、`JSXClosingFragment` 节点类 |
| `esprima/jsx_parser.py` | Fragment 解析（`parseJSXOpeningElement`/`parseJSXBoundaryElement`/`parseComplexJSXElement`） |
| `setup.py` | `python_requires` + classifier 更新 |
| `.github/workflows/ci.yml` | 新增 CI 配置 |
| `tests/test_es2018_2020.py` | 新增 40 个测试 |
| `tests/test_es2021_2025.py` | 新增 67 个测试 |
| `tests/test_bugfixes.py` | 新增 19 个测试 |

### Test Results

- **126/126** pytest 通过（40 ES2018-2020 + 67 ES2021-2025 + 19 bugfix）
- **1346** legacy unittest（含 pre-existing 不相关失败）

---

## [4.0.0-dev.6] - Previous Release

- Based on Kronuz/esprima-python
- Babylon types support
- Class properties (experimental)
- Visitor pattern improvements
