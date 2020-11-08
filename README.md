# loguru-mypy

A fancy plugin to boost up your logging with [loguru](https://github.com/Delgan/loguru)

![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/kornicameister/loguru-mypy/CI/master)
[![Open Source Helpers](https://www.codetriage.com/kornicameister/loguru-mypy/badges/users.svg)](https://www.codetriage.com/kornicameister/loguru-mypy)
![PyPI](https://img.shields.io/pypi/v/loguru-mypy)
![PyPI - Downloads](https://img.shields.io/pypi/dm/loguru-mypy)
[![time tracker](https://wakatime.com/badge/github/kornicameister/loguru-mypy.svg)](https://wakatime.com/badge/github/kornicameister/loguru-mypy)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

## mypy compatibility

`logoru-mypy` should compatible with `mypy==0.770` and upwards.

## Installation

Simply execute:

```sh
pip install loguru-mypy
```

And later on modify your `mypy.ini` configuration file with

```ini
[mypy]
plugins = loguru_mypy
```

That is all, your code is now ready to be linted.

## What is included?

`loguru-mypy` is obviously a [mypy](https://github.com/python/mypy) plugin that allows to avoid
some of those little _runtime_ trickeries :).
Here is a short attempt to list some of those:

### Lazy loggers

`logger.opt(lazy=True)` in facts returns a `logger` that we call _lazy_. Lazy loggers accept only
`typing.Callable[[], t.Any]` in place of positional or named arguments. Passing a callable that
accepts even a **single** argument thus results in runtime error. `loguru-mypy` detects that fact
and lets you know before your runtime reaches that portion of a code.
