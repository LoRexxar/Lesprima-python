# Changelog

All notable changes to this project will be documented in this file.

## [4.1.0] - 2025-05-25

### Added

**ES2018-ES2020 语法特性支持**（8 个新特性）

- **ES2019: Optional catch binding** — `try {} catch {}` 无需绑定参数
- **ES2020: `import.meta`** — 模块元信息表达式（`MetaProperty` 节点）
- **ES2020: Nullish coalescing `??`** — 空值合并运算符，禁止与 `&&`/`||` 混用（需括号）
- **ES2018: Async generators** — `async function* gen() { yield await 1; }`
- **ES2018: `for-await-of`** — 异步迭代器循环（`ForOfStatement.is_await`）
- **JSX Fragment `<></>`** — `JSXOpeningFragment` / `JSXClosingFragment` 节点
- **ES2020: Optional chaining `?.`** — 可选链（`ChainExpression` 包装，`optional` 标志）
- **ES2018: Template literal revision** — tagged template 中非法转义序列 `cooked=null` 而非报错

**测试**

- `tests/test_es2018_2020.py` — 40 个测试覆盖全部 8 个新特性
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

### Changed

- **Python 3.11+ 兼容性** — `async` → `is_async`、`await` → `allow_await`、`self.await` → `self.is_await` 全局替换，修复 Python 3.7+ 关键字冲突
- `setup.py` 添加 `python_requires='>=3.11'`，移除 Python 2.x / 3.3-3.6 classifier，添加 3.11-3.13 classifier

### Modified Files

| 文件 | 改动 |
|------|------|
| `esprima/parser.py` | 8 个新特性 parser 逻辑 + 6 个 bug 修复 |
| `esprima/scanner.py` | `??` token 识别 + template literal revision (`notEscapeSequenceHead`) |
| `esprima/nodes.py` | `ChainExpression`、`Property` 节点类 + `ForOfStatement.is_await` + `ClassMethod` id 修复 |
| `esprima/syntax.py` | `ChainExpression` 常量 |
| `esprima/messages.py` | `NullishCoalescingNotAllowed`、`CannotUseImportMetaOutsideAModule`、`InvalidTaggedTemplateOnOptionalChain` |
| `esprima/jsx_syntax.py` | `JSXOpeningFragment`、`JSXClosingFragment` 枚举 |
| `esprima/jsx_nodes.py` | `JSXOpeningFragment`、`JSXClosingFragment` 节点类 |
| `esprima/jsx_parser.py` | fragment 解析（`parseJSXOpeningElement`/`parseJSXBoundaryElement`/`parseComplexJSXElement`） |
| `setup.py` | `python_requires` + classifier 更新 |
| `.github/workflows/ci.yml` | 新增 CI 配置 |
| `tests/test_es2018_2020.py` | 新增 40 个测试 |
| `tests/test_bugfixes.py` | 新增 19 个测试 |

### Test Results

- **59/59** pytest 通过
- **1346** legacy unittest（含 pre-existing 不相关失败）

---

## [4.0.0-dev.6] - Previous Release

- Based on Kronuz/esprima-python
- Babylon types support
- Class properties (experimental)
- Visitor pattern improvements
