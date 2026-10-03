import re

with open('pyproject.toml', 'r') as f:
    text = f.read()

# restore PyYAML
text = text.replace('"PyYAML; python_version < \\"3.15\\"",', '"PyYAML",')

# restore pytest and mypy
text = text.replace('commands = [\n    ["bash", "-c", "pytest --cov=src --cov-append --cov-report=term-missing --cov-branch || true"]\n]\nallowlist_externals = ["bash"]', 'commands = [\n    ["pytest", "--cov=src", "--cov-append", "--cov-report=term-missing", "--cov-branch"]\n]')
text = text.replace('commands = [\n    ["bash", "-c", "mypy src test || true"]\n]\nallowlist_externals = ["bash"]', 'commands = [\n    ["mypy", "src", "test"]\n]')

with open('pyproject.toml', 'w') as f:
    f.write(text)
