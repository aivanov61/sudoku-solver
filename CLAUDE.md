# CLAUDE.md

## Working preferences

- **Clean code**: favor clear names, small focused functions, and no dead or duplicated code.
- **TDD**: write or update a failing test in `tests/` first, then make it pass, then refactor.
- **Follow existing norms**: match the naming, structure, comment style, and idioms already used in this code base rather than introducing new conventions.
- **Method order**: place a called method as close as possible after the method that calls it, while keeping it in its own section (interface or private). Reading top to bottom, called methods then appear in the order they are used. When several callers share a method, place it after the first one. When adding or moving a method, check that its callees still follow it.
- **Constants first**: put class constants at the top of the class, right after the docstring and before any methods or other class state. If there is a docstring, put a blank line before the constant(s), otherwise no blank line. The exceptions are a constant built from a nested class, which Python requires to be defined first (e.g. `DisplayAttrs.ATTRS_PRIMARY` uses `FgBgAttr`), and a long table of data constants (e.g. `Display`'s drawing characters), which goes at the end of the class so it doesn't push the class's logic down a page.
- **Layers**: the puzzle knows only its block layout and routes each request from a block to every block; only a block decides which of its own cells are affected, because in other puzzle types the blocks may not form a regular grid. Put new cross-cell logic in the block. The one exception: the puzzle may reach a cell by position for cursor navigation and the selected cell, since a sudoku's outer edge is always rectangular.
- **Line endings**: working files use CRLF (Windows; `core.autocrlf=true` stores LF in git). Editing tools often write LF, so convert new or rewritten files and check with `git ls-files --eol` or by counting `\r` bytes, not with `grep $'\r$'` (Git Bash's grep hides carriage returns).
- **Sudoku solver**: keep in mind the rules of a basic 9x9 sudoku puzzle: the grid is divided into nine 3x3 boxes (three across and three down), and each row, each column, and each box must contain the digits 1–9 exactly once.
