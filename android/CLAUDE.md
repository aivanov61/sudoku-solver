# CLAUDE.md (Android app)

This folder is the Android Studio project for an Android user interface to the sudoku game. The game itself is
the Python package `game/` one level up, and the working preferences in `../CLAUDE.md` apply here too. Read it
first, together with `../DesignDoc.md` (especially the user interface port, section 4.4).

## A note from the Claude who set this up (in VS Code, 2026-11-09)

Anton wants to explore an Android app as the next big thing. We agreed on this approach:

- **The game stays in Python, unchanged**, and runs inside the app through Chaquopy, version 17.2.0. Chaquopy's
  own version table says it supports Python 3.10–3.15 and Android Gradle plugin 7.3–9.5. The app uses Python
  3.15, the same as the PC; the game needs 3.14 or later because of lazy annotations and `type` aliases.
- **The UI is native Kotlin with Jetpack Compose.**
- **A Python adapter, `ui/android/`, beside `ui/terminal/`,** will implement the `UserInterface` port
  (`game/user_interface.py`) and pass each call on to Kotlin. The player's actions come back the other way as
  `puzzle.handle(action, digit, position)`; a tap on a cell is `Action.SELECT` with its `(row, col)` position. It belongs in the repo's `ui/` so the repo's tests, ruff and pyright cover it.
- **Dialogs stay synchronous**, which is Anton's earlier decision. `confirm()`, `ask_file_name()`,
  `configure()` and `walk_through()` block until the player answers, so the game runs on its own thread. A
  dialog posts its request to the UI thread and waits on a queue for the answer. Never block the UI thread.
- **Touch takes the place of keys.** The game already works in `Action`s (`game/actions.py`), so taps map to
  actions: tap a cell to select it, use a digit pad for values and guesses, and buttons for the commands. The
  screen design is Anton's call; ask him.

### What is here now

- A plain Compose app, `io.github.aivanov61.sudoku`, copied from the setup of Anton's BowlingPots project:
  - AGP 9.5.1 with its built-in Kotlin
  - Kotlin 2.4.21
  - Compose BOM 2026.09.00
  - Gradle 9.9.0
  - compileSdk and targetSdk 37, minSdk 24
- The `syncGamePython` task in `app/build.gradle.kts` copies `../game` (without its tests) into
  `app/build/game-python/` before each build, and Chaquopy packages it from there. So the app always runs the same
  game code as the terminal. Never edit the copy.
- `MainActivity` is only a smoke test. It starts Python, builds `Board3x3`, and shows the Python version and
  the board's cell count. If that screen shows 81 cells, Python and the game load.

### The first step: a spike, on a branch

Prove the two risky parts before designing the whole UI:

1. Show the board: a 9x9 grid drawn from the cells the port's `show_board()` and `cell_changed()` report.
2. Let a tap select a cell and the digit pad enter a value. This goes through `puzzle.handle(...)` on the game
   thread, with the change coming back to the grid through `cell_changed()`.
3. Give one blocking dialog (`confirm()`, for example on quit) a real answer through the queue, to prove the
   threading.

Keep the spike small. Once it works, plan the full UI with Anton before building it: the screen layout, the
commands panel, marks, highlights, `w`, and saving and restoring.

### Working with Anton

The lasting preferences are in the memory folder of the parent project. If you started in this folder, you
don't have them as your own, so read them:
`C:\Users\aivan\.claude\projects\c--Users-aivan-PythonProjects-sudoku\memory\` (start with `MEMORY.md`).
In short:

- Plan first, and ask when a request has open questions.
- Work on a branch.
- Commit only after he has tried it by hand and says so.
- Fast-forward main, push and delete branches only when he says to.
- Commit messages are one descriptive sentence, ending with the Co-Authored-By line.
- Working files use CRLF, except `gradlew`, which must stay LF (see `.gitattributes`).
