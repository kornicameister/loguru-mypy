# Changelog

## [Unreleased](https://github.com/kornicameister/loguru-mypy/tree/HEAD)

[Full Changelog](https://github.com/kornicameister/loguru-mypy/compare/v0.0.4...HEAD)

**Fixed bugs:**

- Releases are not working [\#107](https://github.com/kornicameister/loguru-mypy/issues/107)

**Closed issues:**

- Cannot import loguru.Writable [\#130](https://github.com/kornicameister/loguru-mypy/issues/130)

## [v0.0.4](https://github.com/kornicameister/loguru-mypy/tree/v0.0.4) (2021-04-11)

[Full Changelog](https://github.com/kornicameister/loguru-mypy/compare/v0.0.3...v0.0.4)

**Implemented enhancements:**

- Use PAT for changelog operations [\#109](https://github.com/kornicameister/loguru-mypy/pull/109) ([kornicameister](https://github.com/kornicameister))
- Auto commit change log only if changes detected [\#104](https://github.com/kornicameister/loguru-mypy/pull/104) ([kornicameister](https://github.com/kornicameister))
- Add mypy==0.812 to CI matrix [\#103](https://github.com/kornicameister/loguru-mypy/pull/103) ([kornicameister](https://github.com/kornicameister))
- Enable push to protected branch [\#102](https://github.com/kornicameister/loguru-mypy/pull/102) ([kornicameister](https://github.com/kornicameister))
- Generate changelog for each commit [\#101](https://github.com/kornicameister/loguru-mypy/pull/101) ([kornicameister](https://github.com/kornicameister))

**Fixed bugs:**

- "Internal error" while logging non-string messages [\#49](https://github.com/kornicameister/loguru-mypy/issues/49)

**Merged pull requests:**

- Prevent circular updated for changelog [\#108](https://github.com/kornicameister/loguru-mypy/pull/108) ([kornicameister](https://github.com/kornicameister))
- Fetch entire history for release [\#106](https://github.com/kornicameister/loguru-mypy/pull/106) ([kornicameister](https://github.com/kornicameister))
- Revert "Auto commit change log only if changes detected \(\#104\)" [\#105](https://github.com/kornicameister/loguru-mypy/pull/105) ([kornicameister](https://github.com/kornicameister))
- \[refactor\] Pull out arguments unpacking to function [\#88](https://github.com/kornicameister/loguru-mypy/pull/88) ([kornicameister](https://github.com/kornicameister))
- Bump pytest to 6.2.2 [\#87](https://github.com/kornicameister/loguru-mypy/pull/87) ([kornicameister](https://github.com/kornicameister))
- Add mypy==0.800 [\#86](https://github.com/kornicameister/loguru-mypy/pull/86) ([kornicameister](https://github.com/kornicameister))
- Accept Any Single Argument [\#81](https://github.com/kornicameister/loguru-mypy/pull/81) ([ThibaultLemaire](https://github.com/ThibaultLemaire))
- Accept variables \(NameExpr\) in loguru calls [\#80](https://github.com/kornicameister/loguru-mypy/pull/80) ([ThibaultLemaire](https://github.com/ThibaultLemaire))
- Accept numbers \(int,float\) for loguru calls [\#79](https://github.com/kornicameister/loguru-mypy/pull/79) ([kornicameister](https://github.com/kornicameister))
- Typos fix by misspell-fixer [\#75](https://github.com/kornicameister/loguru-mypy/pull/75) ([github-actions[bot]](https://github.com/apps/github-actions))
- Bump pytest-randomly from 3.4.1 to 3.5.0 in /requirements/dev [\#69](https://github.com/kornicameister/loguru-mypy/pull/69) ([dependabot[bot]](https://github.com/apps/dependabot))

## [v0.0.3](https://github.com/kornicameister/loguru-mypy/tree/v0.0.3) (2020-12-28)

[Full Changelog](https://github.com/kornicameister/loguru-mypy/compare/v0.0.2...v0.0.3)

**Fixed bugs:**

- Support attribute references of positional/keyword arguments with string formatting [\#42](https://github.com/kornicameister/loguru-mypy/issues/42)

**Closed issues:**

- Test against 3 latest releases of mypy + hard pin in plugin hook na latest [\#47](https://github.com/kornicameister/loguru-mypy/issues/47)
- Add this to awesome-python-typing [\#39](https://github.com/kornicameister/loguru-mypy/issues/39)

**Merged pull requests:**

- Use ubuntu 20.04 instead of ubuntu-latest [\#71](https://github.com/kornicameister/loguru-mypy/pull/71) ([kornicameister](https://github.com/kornicameister))
- Bump pascalgn/automerge-action from v0.12.0 to v0.13.0 [\#70](https://github.com/kornicameister/loguru-mypy/pull/70) ([dependabot[bot]](https://github.com/apps/dependabot))
- Bump lxml from 4.6.1 to 4.6.2 in /requirements/dev [\#68](https://github.com/kornicameister/loguru-mypy/pull/68) ([dependabot[bot]](https://github.com/apps/dependabot))
- Add coverage calculation [\#65](https://github.com/kornicameister/loguru-mypy/pull/65) ([kornicameister](https://github.com/kornicameister))
- Setup requirements for automerge [\#64](https://github.com/kornicameister/loguru-mypy/pull/64) ([kornicameister](https://github.com/kornicameister))
- Be specific when tox runs [\#63](https://github.com/kornicameister/loguru-mypy/pull/63) ([kornicameister](https://github.com/kornicameister))
- New releases schema with changelog generator [\#62](https://github.com/kornicameister/loguru-mypy/pull/62) ([kornicameister](https://github.com/kornicameister))
- Add mypy compatibility note [\#61](https://github.com/kornicameister/loguru-mypy/pull/61) ([kornicameister](https://github.com/kornicameister))
- Test against several versions of mypy & loguru [\#59](https://github.com/kornicameister/loguru-mypy/pull/59) ([kornicameister](https://github.com/kornicameister))
- Leverage mypy to check str.format expressions [\#43](https://github.com/kornicameister/loguru-mypy/pull/43) ([ThibaultLemaire](https://github.com/ThibaultLemaire))

## [v0.0.2](https://github.com/kornicameister/loguru-mypy/tree/v0.0.2) (2020-07-06)

[Full Changelog](https://github.com/kornicameister/loguru-mypy/compare/v0.0.1...v0.0.2)

**Closed issues:**

- Draft first release [\#19](https://github.com/kornicameister/loguru-mypy/issues/19)

## [v0.0.1](https://github.com/kornicameister/loguru-mypy/tree/v0.0.1) (2020-07-05)

[Full Changelog](https://github.com/kornicameister/loguru-mypy/compare/111b7251fe8508015054ba9093885c95607042cb...v0.0.1)

**Closed issues:**

- Figure out possibility of tracking logger objects [\#6](https://github.com/kornicameister/loguru-mypy/issues/6)

**Merged pull requests:**

- Track if logger was lazy or not [\#7](https://github.com/kornicameister/loguru-mypy/pull/7) ([kornicameister](https://github.com/kornicameister))
- Port implementation from loguru PR [\#3](https://github.com/kornicameister/loguru-mypy/pull/3) ([kornicameister](https://github.com/kornicameister))
- Add basic CI based on tox [\#2](https://github.com/kornicameister/loguru-mypy/pull/2) ([kornicameister](https://github.com/kornicameister))
- Add action to upload to pypi [\#1](https://github.com/kornicameister/loguru-mypy/pull/1) ([kornicameister](https://github.com/kornicameister))



