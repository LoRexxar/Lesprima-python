# Lesprima-python

JavaScript parser (esprima) Python port, fork from Kronuz/esprima-python.

## Structure
- `esprima/parser.py` - Main parser logic (~3200 lines)
- `esprima/scanner.py` - Tokenizer/lexer
- `esprima/nodes.py` - AST node classes
- `esprima/syntax.py` - Syntax type constants
- `esprima/messages.py` - Error messages
- `esprima/token.py` - Token types

## Test & Run
- Venv: `/home/ubuntu/.hermes/hermes-agent/venv/`
- Python: `/home/ubuntu/.hermes/hermes-agent/venv/bin/python3`
- Run tests: `/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -m pytest tests/ -v`
- Run single: `/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -m pytest tests/test_esprima_issues.py -v`

## Convention
- Branch: `develop`, push to `origin develop`
- Commit message: Chinese description, no issue reference numbers like #4
