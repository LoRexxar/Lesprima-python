# Lesprima-python 项目文档

> 基于源码扫描生成，涵盖架构、模块详解和数据流分析。

## 1. 项目概述

**Lesprima-python**（原名 esprima-python）是 [esprima](https://esprima.org/) JavaScript 解析器的 Python 移植版。它将 JavaScript 源代码解析为 ESTree 兼容的 AST（抽象语法树），支持 ES2020+ 语法和 JSX 扩展。

**核心功能**：
- 完整的 JavaScript 解析器（递归下降）
- ESTree 兼容 AST 输出
- ES6~ES2020+ 语法支持（arrow functions、async/await、class fields、optional chaining 等）
- JSX 语法扩展解析
- Tokenizer 模式（词法分析）
- 可选的注释收集
- Node delegate 回调机制（用于 AST 转换）

**原始上游**：https://github.com/Kronuz/esprima-python

## 2. 项目结构

```
Lesprima-python/
├── esprima/                    # 核心库
│   ├── __init__.py             # 包入口，导出公开 API
│   ├── __main__.py             # CLI 入口（python -m esprima）
│   ├── esprima.py              # 顶层 API（parse/parseModule/parseScript/tokenize）
│   ├── parser.py               # 主解析器（3084行，递归下降）
│   ├── scanner.py              # 词法扫描器（1197行）
│   ├── tokenizer.py            # Tokenizer 封装（185行）
│   ├── nodes.py                # AST 节点定义（946行，104个类）
│   ├── syntax.py               # Syntax 类型常量（81个）
│   ├── token.py                # Token 类型枚举
│   ├── jsx_parser.py           # JSX 扩展解析器（585行）
│   ├── jsx_nodes.py            # JSX AST 节点（11个类）
│   ├── jsx_syntax.py           # JSX Syntax 常量
│   ├── objects.py              # 基础 Object 类（dict-like）
│   ├── character.py            # Unicode 字符分类工具
│   ├── messages.py             # 错误消息常量
│   ├── error_handler.py        # 错误处理（Error + ErrorHandler）
│   ├── comment_handler.py      # 注释收集处理
│   ├── compat.py               # Python 2/3 兼容层
│   ├── utils.py                # 格式化工具
│   ├── visitor.py              # AST 访问者模式
│   └── xhtml_entities.py       # XHTML 实体映射
├── test/                       # 测试套件
│   ├── __init__.py
│   ├── __main__.py
│   ├── 3rdparty/               # 第三方 JS 库（jQuery、Angular、Backbone 等）
│   └── fixtures/               # 测试用例（1593个 .js + 对应 .json）
├── examples/
│   └── visitor.py              # Visitor 使用示例
├── setup.py                    # 构建脚本
├── pyproject.toml              # 项目元数据
├── setup.cfg                   # wheel 配置
├── README.rst                  # 说明文档
└── ChangeLog                   # 变更日志
```

**代码规模**：核心库 7592 行 Python，测试 249 行驱动代码 + 1593 个 JS 测试用例。

## 3. 核心模块详解

### 3.1 esprima.py — 顶层 API

入口模块，提供 5 个公开函数：

| 函数 | 功能 |
|------|------|
| `parse(code, options)` | 通用解析（自动判断 script/module） |
| `parseModule(code, options)` | 解析为 ES Module |
| `parseScript(code, options)` | 解析为 Script |
| `tokenize(code, options)` | 仅词法分析，返回 token 列表 |
| `proxyDelegate(...)` | 代理 delegate 回调 |

**解析选项**（Config 对象）：
- `range` — 在节点中包含 `[start, end]` 字符范围
- `loc` — 在节点中包含 `SourceLocation`（行号/列号）
- `source` — 源文件名（嵌入 location 中）
- `tokens` — 返回 token 列表
- `comment` — 收集注释
- `tolerant` — 容错模式（不抛出错误，收集到 errors 列表）
- `jsx` — 启用 JSX 解析

**内部类 `Tokens`**：预解析一段 JS 代码（`"let x = 42"`）来检测运行时 esprima 版本是否支持 `let`。

### 3.2 parser.py — 主解析器（核心，3084行）

这是整个项目最核心的模块，实现了完整的 JavaScript 递归下降解析器。

**内部数据类**：

| 类 | 用途 |
|----|------|
| `Value` | 包装值（type/value/etc） |
| `Params` | 函数参数解析状态（simple/message/stricted 等） |
| `Config` | 解析配置选项 |
| `Context` | 解析上下文（strict mode、inFunctionBody、inIteration 等） |
| `Marker` | 位置标记（index/line/column），用于构建节点的 loc/range |
| `TokenEntry` | Token 条目 |

**核心类 `Parser`**（99+ 个方法）：

解析方法按语法层级组织：

```
parseModule / parseScript
  └─ parseStatement / parseStatementListItem
       ├─ parseExpressionStatement
       ├─ parseIfStatement
       ├─ parseDoWhileStatement / parseWhileStatement / parseForStatement
       ├─ parseReturnStatement
       ├─ parseSwitchStatement
       ├─ parseTryStatement
       ├─ parseWithStatement
       ├─ parseVariableStatement
       ├─ parseFunctionDeclaration
       ├─ parseClassDeclaration
       ├─ parseExportDeclaration / parseImportDeclaration
       └─ parseBlock
            └─ parseStatement (递归)

parseExpression
  └─ parseAssignmentExpression
       └─ parseConditionalExpression
            └─ parseBinaryExpression
                 └─ parseUnaryExpression
                      └─ parseUpdateExpression
                           └─ parseLeftHandSideExpressionAllowCall
                                ├─ parseNewExpression
                                └─ parseCallExpression / parseMemberExpression
                                     └─ parsePrimaryExpression
                                          ├─ parseArrayInitializer
                                          ├─ parseObjectInitializer
                                          ├─ parseTemplateLiteral
                                          ├─ parseFunctionExpression
                                          ├─ parseClassExpression
                                          └─ parseIdentifier
```

**关键辅助方法**：

| 方法 | 功能 |
|------|------|
| `createNode/startNode/finalize` | 节点位置追踪（构建 range/loc） |
| `expect/expectCommaSeparator/expectKeyword` | 消费特定 token |
| `match/matchKeyword/matchContextualKeyword` | 前瞻匹配 |
| `collectComments` | 收集注释（行注释/块注释） |
| `nextToken` | 从 scanner 获取下一个 token |
| `isolateCoverGrammar` | 在隔离上下文中解析（重置 cover grammar 状态） |
| `inheritCoverGrammar` | 在继承上下文中解析 |
| `reinterpretExpressionAsPattern` | 将表达式重新解释为解构模式 |

### 3.3 scanner.py — 词法扫描器（1197行）

负责将源代码字符串拆分为 token 流。

**数据类**：

| 类 | 用途 |
|----|------|
| `RegExp` | 正则表达式（pattern/flags） |
| `Position` | 行列位置（line/column） |
| `SourceLocation` | 源码位置（start/end + source） |
| `Comment` | 注释（type/value/slice/range/loc） |
| `RawToken` | 原始 token（type/value/regex/lineno/etc） |
| `ScannerState` | 扫描器快照（用于状态保存/恢复） |
| `Octal` | 八进制常量（octal/loc） |
| `Scanner` | 扫描器主类 |

**Scanner 核心方法**：

| 方法 | 功能 |
|------|------|
| `getNextToken()` | 获取下一个 token（主入口） |
| `scanIdentifier()` | 扫描标识符/关键字 |
| `scanPunctuator()` | 扫描运算符/标点 |
| `scanNumericLiteral()` | 扫描数字字面量 |
| `scanStringLiteral()` | 扫描字符串字面量 |
| `scanTemplate()` | 扫描模板字符串 |
| `scanRegExp()` | 扫描正则表达式 |
| `skipSingleLineComment()` | 跳过单行注释 |
| `skipMultiLineComment()` | 跳过多行注释 |
| `skipComment()` | 跳过注释（统一入口） |
| `saveState/restoreState` | 保存/恢复扫描器状态 |

### 3.4 tokenizer.py — Tokenizer 模式

对 Scanner 的封装，提供纯词法分析功能。当调用 `esprima.tokenize()` 时使用。

**核心类**：

| 类 | 用途 |
|----|------|
| `BufferEntry` | 缓冲区条目（type/value/regex/range/loc） |
| `Reader` | 读取器（封装 scanner 的位置追踪） |
| `Config` | Tokenizer 配置 |
| `Tokenizer` | Tokenizer 主类 |

**Tokenizer.getNextToken()**：使用有限状态机处理 regex 与除法的歧义（`/` 可能是除法或正则开头），通过 `beforeFunctionExpression` + `isRegexStart` 判断。

### 3.5 nodes.py — AST 节点体系（946行，104个类）

所有 AST 节点继承自 `Node(Object)`，`Object` 提供类 dict 接口。

**节点继承体系**：

```
Node (→ Object)
├── Expression                    # 表达式基类
│   ├── ArrayExpression           # [1, 2, 3]
│   ├── ArrowFunctionExpression   # (x) => x + 1
│   ├── AsyncArrowFunctionExpression
│   ├── AsyncFunctionExpression
│   ├── AssignmentExpression      # x = 1
│   ├── AwaitExpression           # await x
│   ├── BinaryExpression          # x + y
│   ├── LogicalExpression         # x && y
│   ├── CallExpression            # foo()
│   ├── NewExpression (→CallExpr) # new Foo()
│   ├── ClassExpression           # class { ... }
│   ├── ConditionalExpression     # x ? a : b
│   ├── DoExpression              # do { ... }
│   ├── FunctionExpression
│   ├── Identifier                # x
│   ├── PrivateName               # #field
│   ├── Literal                   # 42, "str"
│   │   ├── RegExpLiteral         # /regex/
│   │   ├── NullLiteral           # null
│   │   ├── StringLiteral         # "hello"
│   │   ├── BooleanLiteral        # true/false
│   │   ├── NumericLiteral        # 42
│   │   └── DirectiveLiteral      # "use strict"
│   ├── ObjectExpression         # {key: value}
│   ├── SequenceExpression       # a, b, c
│   ├── StaticMemberExpression   # a.b
│   ├── ComputedMemberExpression # a[b]
│   ├── BindExpression           # ::method
│   ├── TaggedTemplateExpression # tag`...`
│   ├── TemplateLiteral          # `hello ${name}`
│   ├── ThisExpression           # this
│   ├── UnaryExpression          # -x, !x, typeof x
│   ├── UpdateExpression         # x++, ++x
│   └── YieldExpression          # yield x
│
├── Statement                     # 语句基类
│   ├── BlockStatement            # { ... }
│   ├── BreakStatement            # break
│   ├── ContinueStatement        # continue
│   ├── DebuggerStatement        # debugger
│   ├── DoWhileStatement         # do {} while ()
│   ├── EmptyStatement           # ;
│   ├── ExpressionStatement      # expr;
│   ├── ForInStatement           # for (x in obj)
│   ├── ForOfStatement           # for (x of arr)
│   ├── ForStatement             # for (;;) {}
│   ├── IfStatement              # if () {} else {}
│   ├── LabeledStatement         # label: ...
│   ├── ReturnStatement          # return x
│   ├── SwitchStatement          # switch () {}
│   ├── ThrowStatement           # throw x
│   ├── TryStatement             # try {} catch {}
│   ├── WhileStatement           # while () {}
│   ├── WithStatement            # with () {}
│   └── Declaration
│       ├── FunctionDeclaration
│       ├── AsyncFunctionDeclaration
│       ├── ExportAllDeclaration
│       ├── ExportDefaultDeclaration
│       ├── ExportNamedDeclaration
│       └── VariableDeclaration
│
├── Pattern                       # 解构模式基类
│   ├── ArrayPattern              # [a, b] = arr
│   ├── AssignmentPattern         # {x = 1} = obj
│   └── ObjectPattern             # {a, b} = obj
│
├── Function                      # 函数基类
├── Class                         # 类基类
│   ├── ClassBody
│   ├── ClassDeclaration
│   ├── ClassMethod
│   ├── ClassProperty
│   └── ClassPrivateProperty
│
├── ModuleDeclaration             # import/export
├── ModuleSpecifier
│   ├── ExportSpecifier
│   ├── ImportDefaultSpecifier
│   ├── ImportNamespaceSpecifier
│   └── ImportSpecifier
│
├── CatchClause                   # catch (e) {}
├── Directive                     # "use strict"
├── Import                        # import()
├── MetaProperty                  # import.meta / new.target
├── RestElement                   # ...args
├── SpreadElement                 # [...arr]
├── Super                         # super
├── SwitchCase                    # case x:
├── TemplateElement              # 模板字符串片段
├── VariableDeclarator           # let x = 1
├── ArrowParameterPlaceHolder
├── AsyncArrowParameterPlaceHolder
├── BlockComment
├── LineComment
├── ObjectMember
│   ├── ObjectProperty
│   │   └── AssignmentProperty
│   └── ObjectMethod
├── Decorator                     # @decorator
├── Script                        # 脚本根节点
└── Module                        # 模块根节点
```

### 3.6 jsx_parser.py — JSX 解析器（585行）

JSX 扩展解析器，在 `jsx=True` 选项时启用。

**核心类**：

| 类 | 用途 |
|----|------|
| `MetaJSXElement` | JSX 元素元数据 |
| `JSXToken` | JSX token |
| `RawJSXToken` | 原始 JSX token |
| `JSXParser` | JSX 解析器（继承并扩展主 Parser 的 token 消费逻辑） |

**JSX AST 节点**（jsx_nodes.py，11个类）：

`JSXElement`, `JSXOpeningElement`, `JSXClosingElement`, `JSXText`, `JSXExpressionContainer`, `JSXEmptyExpression`, `JSXIdentifier`, `JSXMemberExpression`, `JSXAttribute`, `JSXSpreadAttribute`, `JSXNamespacedName`

### 3.7 visitor.py — AST 访问者

提供 `NodeVisitor` 类，实现经典的 Visitor 模式遍历 AST。

```python
class NodeVisitor:
    def visit(self, node)        # 递归访问节点
    def generic_visit(self, node) # 默认处理
    def delegate(self, node)     # 委托处理（可返回变换后的节点）
```

支持节点变换（transform）：delegate 方法可返回新的节点来替换原节点。

### 3.8 辅助模块

| 模块 | 功能 |
|------|------|
| `objects.py` | `Object` 基类，提供 `__getattr__`/`__setattr__` + dict-like 接口（keys/items） |
| `character.py` | `Character` 类，Unicode 字符分类（isIdentifierStart/isIdentifierPart/isWhiteSpace 等） |
| `messages.py` | `Messages` 类，81 条错误消息常量（如 `UnexpectedToken`、`InvalidLHSInAssignment`） |
| `error_handler.py` | `ErrorHandler` 收集容错模式下的错误；`Error` 自定义异常 |
| `comment_handler.py` | `CommentHandler` 在解析过程中收集注释 |
| `syntax.py` | `Syntax` 类，81 个 AST 节点类型字符串常量 |
| `token.py` | `Token` 类，token 类型常量（BooleanLiteral/EOF/Identifier 等） |
| `compat.py` | Python 2/3 兼容（basestring/unicode/regexp） |
| `utils.py` | `format()` 字符串格式化工具 |
| `xhtml_entities.py` | 282 行的 XHTML 实体名称→字符映射表 |

## 4. 数据流

### 4.1 解析流程

```
JavaScript 源代码 (string)
        │
        ▼
   esprima.parse(code, options)
        │
        ▼
   Parser.__init__(code, options, delegate)
   ├─ 创建 ErrorHandler
   ├─ 创建 Scanner(code, handler)
   └─ 创建 Context(isModule)
        │
        ▼
   Parser.parseModule() / parseScript()
   ├─ nextToken()  ←── Scanner.scanIdentifier/scanPunctuator/...
   ├─ collectComments()
   ├─ parseStatementListItem()  ←── 递归下降
   │   ├─ parseExpression()
   │   ├─ parseIfStatement()
   │   ├─ parseForStatement()
   │   ├─ ...
   │   └─ parseBlock() → parseStatement() (递归)
   │
   │  每个解析方法：
   │  1. startNode(token)  → 记录位置
   │  2. expect/match      → 消费 token
   │  3. 创建 AST 节点      → nodes.XxxStatement/XxxExpression
   │  4. finalize(marker)   → 填充 range/loc
   │
   ▼
   AST (Node tree)
   ├─ type: "Program" (Script | Module)
   ├─ body: [Statement | ModuleDeclaration, ...]
   ├─ sourceType: "script" | "module"
   └─ 可选: tokens[], comments[], errors[]
```

### 4.2 Tokenize 流程

```
JavaScript 源代码 (string)
        │
        ▼
   esprima.tokenize(code, options)
        │
        ▼
   Tokenizer(code, options)
   ├─ 创建 Scanner(code, handler)
   └─ 循环调用 getNextToken()
       ├─ Scanner 扫描 token
       ├─ 处理 regex/divide 歧义
       └─ 返回 TokenEntry[]
```

### 4.3 JSX 解析流程

```
JSX 代码 (string, jsx=True)
        │
        ▼
   Parser + JSXParser
   ├─ 主 Parser 正常解析到 '<'
   ├─ JSXParser 接管，解析 JSX 标签
   │   ├─ parseJSXElement()
   │   ├─ parseJSXOpeningElement()
   │   ├─ parseJSXChildren()
   │   └─ parseJSXClosingElement()
   └─ 返回 JSXElement AST 节点
```

## 5. 模块依赖关系

```
esprima.py ──→ parser.py ──→ scanner.py
    │              │              │
    │              ├─→ nodes.py ←─┤
    │              ├─→ syntax.py  │
    │              ├─→ token.py ←─┘
    │              ├─→ error_handler.py
    │              ├─→ comment_handler.py
    │              ├─→ messages.py
    │              ├─→ compat.py
    │              └─→ utils.py
    │
    ├─→ tokenizer.py ──→ scanner.py
    └─→ jsx_parser.py ──→ jsx_nodes.py
                        └─→ jsx_syntax.py

objects.py ←── nodes.py, esprima.py, parser.py
character.py ←── scanner.py
visitor.py ←── (独立，遍历 AST 输出)
xhtml_entities.py ←── jsx_parser.py
```

## 6. 扩展点

### 6.1 Delegate 回调

`parse()` 接受 `delegate` 参数，每创建一个 AST 节点时调用。可用于：
- AST 变换（返回修改后的节点）
- 节点收集/过滤
- 自定义分析

### 6.2 Visitor 模式

`NodeVisitor` 类提供结构化的 AST 遍历：
```python
class MyVisitor(NodeVisitor):
    def visit_FunctionDeclaration(self, node):
        # 处理函数声明
        return self.generic_visit(node)
```

### 6.3 容错模式

`tolerant=True` 时，解析错误不会抛异常，而是收集到 `errors` 列表，解析继续进行。

## 7. 测试体系

- **1593 个 .js 测试用例**，每个用例有对应的 `.tree.json`（期望 AST）或 `.failure.json`（期望错误）
- **3rdparty 测试**：用 jQuery 1.9.1、Angular 1.2.5、Backbone 1.1.0、Underscore 1.5.2、MooTools 1.4.5、YUI 3.12.0 等真实大型 JS 库做回归测试
- **按 ES 版本组织**：`fixtures/ES6/`、`fixtures/ES2016/`、`fixtures/ES2018/`、`fixtures/esnext/`
- **测试类型**：
  - `*.tree.json` — 解析结果验证
  - `*.failure.json` — 错误场景验证
  - `*.tokens.json` — tokenizer 输出验证
  - `*.source.js` — 带源码映射的测试
