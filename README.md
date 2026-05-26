# Lesprima-python

[![PyPI version](https://img.shields.io/pypi/v/esprima.svg)](https://pypi.python.org/pypi/esprima)
[![Python 3.11+](https://img.shields.io/pypi/pyversions/esprima.svg)](https://pypi.python.org/pypi/esprima)


> Enhanced fork of [Kronuz/esprima-python](https://github.com/Kronuz/esprima-python) — fixes core AST bugs, Supports ES2018–ES2025 syntax.


## 特性

- **ES2018–ES2025 全覆盖** — async generators、optional chaining、nullish coalescing、private fields/methods、decorators、import attributes、using/await using 等
- **22 个上游 bug 修复** — 修复 jquery/esprima 仓库中确认的 parser 正确性问题（yield 上下文、cover grammar、scope validation 等）
- **ESTree 兼容 AST** — 输出格式遵循 [ESTree](https://github.com/estree/estree) 标准
- **JSX 支持** — 包含 Fragment `<></>` 语法
- **151+ 测试通过** — 覆盖新特性、bug 修复和回归验证
- **Python 3.11+** — 现代化代码，移除 Python 2.x 遗留兼容

## 安装

```bash
pip install esprima
```

## 快速开始

### 解析 JavaScript

```python
import esprima

# 解析脚本
tree = esprima.parseScript('const answer = 42')
print(tree.toDict())

# 解析模块
tree = esprima.parseModule('import { foo } from "bar"; export default foo;')

# 自动检测模式
tree = esprima.parse('const x = 1')
```

### Tokenize

```python
import esprima

tokens = esprima.tokenize('const answer = 42')
for token in tokens:
    print(f'{token.type}: {token.value}')
# Keyword: const
# Identifier: answer
# Punctuator: =
# NumericLiteral: 42
```

### 遍历 AST

```python
import esprima

tree = esprima.parseScript('function greet(name) { return "Hello, " + name; }')

# 使用 visitor
from esprima import visitor

class FunctionCollector(visitor.Visitor):
    def __init__(self):
        super().__init__()
        self.functions = []

    def visit_FunctionDeclaration(self, node):
        self.functions.append(node.id.name)
        return self.generic_visit(node)

collector = FunctionCollector()
collector.visit(tree)
print(collector.functions)  # ['greet']
```

## 支持的 ECMAScript 特性

| 版本 | 特性 |
|------|------|
| **ES2018** | Async generators, `for-await-of`, Template literal revision |
| **ES2019** | Optional catch binding |
| **ES2020** | `import.meta`, Nullish coalescing `??`, Optional chaining `?.` |
| **ES2021** | Numeric separators `1_000`, Logical assignment `&&=` `||=` `??=` |
| **ES2022** | Top-level await, Static class fields, Static init block, Private fields `#x` |
| **ES2023** | Hashbang grammar `#!` |
| **ES2025** | Import Attributes `with {}`, `using`/`await using`, Decorators `@expr` |
| **JSX** | Fragment `<></>`, elements, expressions |

## API

### `esprima.parse(code, options)`

解析 JavaScript 代码，自动判断 script/module 模式。

```python
tree = esprima.parse(code, {
    'sourceType': 'module',   # 'script' | 'module'
    'jsx': True,              # 启用 JSX 解析
    'loc': True,              # 包含位置信息
    'range': True,            # 包含起止索引
    'comment': True,          # 包含注释
    'tolerant': True,         # 容错模式
    'classProperties': True,  # 类属性（默认开启）
})
```

### `esprima.parseScript(code, options)` / `esprima.parseModule(code, options)`

显式指定模式解析。

### `esprima.tokenize(code, options)`

返回 token 列表。

## 与上游的区别

Lesprima-python 基于 [Kronuz/esprima-python](https://github.com/Kronuz/esprima-python)（ES2017），进行了以下改进：

1. **ES2018–ES2025 语法支持** — 新增 18 个语法特性
2. **22 个 bug 修复** — 修复来自 [jquery/esprima#issues](https://github.com/jquery/esprima/issues) 的确认 bug
3. **Python 3.11+ 兼容** — 移除 Python 2.x 兼容代码，修复 `async`/`await` 关键字冲突
4. **CI/CD** — GitHub Actions 自动化测试（Python 3.11/3.12/3.13）

## 开发

```bash
# 克隆仓库
git clone https://github.com/LoRexxar/Lesprima-python.git
cd Lesprima-python

# 安装依赖
pip install -e .

# 运行测试
python -m pytest tests/ -v
```

## 许可证

BSD — 详见 [LICENSE](LICENSE)。

## 致谢

- [Ariya Hidayat](https://twitter.com/ariyahidayat) — esprima 原作者
- [German Mendez Bravo (Kronuz)](https://twitter.com/germbravo) — Python 移植
- [jquery/esprima](https://github.com/jquery/esprima) 贡献者
