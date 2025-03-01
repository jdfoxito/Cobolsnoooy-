# GADYR: Python web app for refunds

```toml
[tool.poetry]
name = "gadyr"
version = "0.1.0"
description = "Devoluciones de cadenas de IVA, STANDAR De los objetos con PEP 8"
description = "Revisado con pycodestyle --max-line-length=240 --first __init__.py"

license = "SRI"

authors = [
    Jimmy Gonzalez "<jagonzaj@sri.gob.ec>"
]

repository = ""
homepage = "https://gadyr/papeles/validarpapelito"

# README file(s) are used as the package description
readme = ["README.md", "LICENSE"]

# Keywords (translated to tags on the package index)
keywords = ["packaging", "poetry"]

[tool.poetry.dependencies]
# Compatible Python versions
python = ">=3.11.5"
# Standard dependency with semver constraints
aiohttp = "^3.8.1"
# Dependency with extras
requests = { version = "^2.28", extras = ["security"] }
# Version-specific dependencies with prereleases allowed
tomli = { version = "^2.0.1", python = "<3.11", allow-prereleases = true }

# Dependency groups are supported for organizing your dependencies
[tool.poetry.group.dev.dependencies]
pytest = "^7.1.2"
pytest-cov = "^3.0"

# ...and can be installed only when explicitly requested
[tool.poetry.group.docs]
optional = true
[tool.poetry.group.docs.dependencies]
Sphinx = "^5.1.1"

# Python-style entrypoints and scripts are easily expressed
[tool.poetry.scripts]
my-script = "my_package:main"
```

