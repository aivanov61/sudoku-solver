# CLAUDE.md (Android app)

This folder is the Android Studio project for an Android user interface to the sudoku game. The game itself is
the Python package `game/` one level up, and the working preferences in `../CLAUDE.md` apply here too.

Read it first, together with `../DesignDoc.md` (especially the user interface port, section 4.4).

## Goals

- **Play on Tony's own phone.** Publishing on the Play Store is parked: it may be explored after MVP 3.

- **Modern Android App Architecture is a key goal that drives the development**, together with clean-code MVVM
  (see Architecture).

  New work follows Google's guide to app architecture; where the code falls short of it, say so and plan the step
  that closes the gap.

- **A modern app design**: Material 3, with menus, settings and keypads as a phone user expects them.

  Tony isn't picky about display elements: choose them from Material 3, the de facto standards of sudoku apps and
  best known methods, and present them as recommendations with the reason. Ask only where it is really his call.

- **Tony learns app development as the app grows.** He is a senior software engineer and architect, but new to
  apps, and wants to be able to maintain the app without AI.

So each phase introduces about one Android concept, explained before the code (what it is, why it is the
standard, a link to the official guide), in a diff small enough to read in one sitting.

Explain how Android does things, not general engineering.

## Approach (agreed 2026-11-09)

- **The game stays in Python, unchanged**, and runs inside the app through Chaquopy, version 17.2.0.

  Chaquopy's own version table says it supports Python 3.10–3.15 and Android Gradle plugin 7.3–9.5. The app uses
  Python 3.15, the same as the PC; the game needs 3.14 or later because of lazy annotations and `type` aliases.

- **The UI is native Kotlin with Jetpack Compose.**

- **A Python adapter, `ui/android/`, beside `ui/terminal/`,** implements the `UserInterface` port
  (`game/user_interface.py`) and passes each call on to Kotlin. It belongs in the repo's `ui/` so the repo's
  tests, ruff and pyright cover it.

  The player's actions come back the other way as `puzzle.handle(action, digit, position)`; a tap on a cell is
  `Action.SELECT` with its `(row, col)` position.

- **Dialogs stay synchronous**, which is Tony's earlier decision. `confirm()`, `ask_file_name()`, `configure()`
  and `walk_through()` block until the player answers, so the game runs on its own thread.

  A dialog posts its request to the UI thread and waits on a queue for the answer. Never block the UI thread.

- **Touch takes the place of keys.** The game already works in `Action`s (`game/actions.py`), so taps map to
  actions.

## Architecture

Modern Android App Architecture, as Google's guide describes it:

- **Separation of concerns, in layers.** The UI layer is Compose screens plus ViewModels, which hold the UI state.
  The data layer is repositories, each the one way to its data, over data sources.

  A domain layer (use cases) is added only when logic is shared between ViewModels.

- **A single source of truth for each kind of data.** The Python game is it for the puzzle: the app never keeps
  game rules or game state of its own, only what the game last reported.

  DataStore is it for app-only settings.

- **Unidirectional data flow.** State flows down as an immutable UI state (`StateFlow`); the player's intents flow
  up as calls on the ViewModel. Composables are stateless: they show the state and pass taps on.

- **Recommended practices.** Kotlin coroutines and `Flow`, lifecycle-aware collection, dependency injection, and
  unit tests for each layer with fakes in place of the real data sources.

Clean-code MVVM is how the UI layer does this, and `../CLAUDE.md`'s preferences (TDD, small focused functions,
no dead code, DRY, open/closed) apply to the Kotlin code as much as to the Python.

### Where the code is now

`docs/architecture.md` draws it as Mermaid diagrams: the layers, and one tap end to end. Update it at the end of
each phase, marking what the phase added and changed.

The Kotlin code, in three packages, wired together by the app's container:

- **Dependency injection by hand** (Google's manual DI). `SudokuApplication`, which the manifest names, is made
  once per process before any screen, and makes the one `AppContainer` (`DefaultAppContainer`).

  The container owns the app-long coroutine scope, and the `GameRepository` of the game in play. It makes the
  game with the `newGame` it is given (`{ PythonGame(this) }`), when first asked for, and makes a new one once the
  game is over, so the app never reopens on a finished game.

  ViewModel factories ask the container for what their ViewModels need, rather than making it themselves.

- **`game/` is the data source**: the game as the app sees it. `Game` is an interface whose `events` is a `Flow`
  of typed `GameEvent`s, and which takes typed `GameAction`s.

  `PythonGame` implements it, and is the only code that knows Chaquopy. Collecting `events` starts Python and the
  game on the game thread (off the UI thread, as the first start takes seconds), and `callbackFlow` turns the
  game's reports into the flow, which ends when the game is over.

  `PythonScreen` implements the adapter's `Screen` (`ui/android/screen.py`), turning each call into a
  `GameEvent`. `GameNames.kt` maps the game's names (Action values, cell kinds, edges, message kinds) to Kotlin
  enums.

- **`data/` is the data layer.** `GameRepository` is the one way to the game: it folds the events into a
  `StateFlow<GameState>` that lives in an app-long scope.

  It runs `act()` and `answer()` on `Dispatchers.IO`, off the UI thread, one at a time
  (`limitedParallelism(1)`), so the game gets the player's actions in the order they were made.

  `GameState.after(event)` works out each event's effect; `GameState` holds only what the game reported.

- **`ui/` holds the ViewModel and the view.** `SudokuViewModel` turns the repository's state into one immutable
  `SudokuUiState` (the game's state plus what the screen works out, such as the mode switch) as a `StateFlow`.

  It implements `SudokuIntents` (`onDigit()`, `onCellTapped()`, ...), each launched in `viewModelScope`.
  `SudokuScreen` is stateless.

- **Unit tests** (`app/src/test`, `gradle :app:testDebugUnitTest`) cover `GameState`, the repository, the
  ViewModel and the container over `FakeGame`, and `PythonScreen`; Python doesn't run in them.

  They use `kotlinx-coroutines-test`, and `MainDispatcherRule` stands in for the UI thread.

On the Python side, `ui/android/android_ui.py`'s `AndroidUI` is the port's adapter. `play()` runs on the game
thread, taking actions from a queue that `act()` fills.

`confirm()` waits on a second queue that `answer()` fills, then reports `questionAnswered()`.

Gaps against the guide, to close in the phases that need them:

- `inform()` doesn't wait yet, so a warning flashes and vanishes.

  The status line has no fixed height, so a wrapped message moves the buttons.

  Both are left for the MVP 1 screen redesign.

## Stages and phases

The app is built in MVP stages. **An MVP is a milestone**, tagged in git when its last phase lands (`mvp1`,
`mvp2`, ...).

**Each MVP is built in phases**: each a slice Tony can try by hand, on its own branch off main, merged to main
when done.

- **MVP 1, play a puzzle on the phone from start to finish.**

  Starting: a splash screen with the copyright, then the latest game in progress. With none, the layout choice
  (only when there are several layouts, as in the terminal), then a new puzzle in setup.

  A redesigned modern game screen: a top app bar with the app-level menu (New puzzle, later Settings and About),
  the board, a message area of fixed height, a command palette with every game-play button, and a pad that is
  entered cell first (tap a cell, then a digit).

  The pad dims a digit once all its places are filled, but keeps it pressable, and shows how many of each are
  left.

  Play: setup of the givens, values and guesses (a value/guess switch in place of Shift, guess-depth shading),
  erase, undo, rewind, conflicts, dead ends and completion; `inform()` as a dialog with OK.

  Auto-save, so a game survives the app going to the background and Android ending it. No Quit button: Android
  apps are left with Back or Home.

  Installed on Tony's phone from Android Studio or as an APK.

- **MVP 2, the solving help:** `n` and `a` with their hints and highlights, `w`'s walk through the removals, tags,
  "must be" marks (Snyder notation) and ruled-out values.

  A configuration screen built from the game's `ConfigOption`s.

- **MVP 3, more puzzles and games:** a list of saved games (new, resume, delete), and sharing save files with
  the PC.

- **Parked:** the Play Store (adaptive layouts, release signing, store listing, privacy, the GPL's source offer).

  Ideas such as entering a puzzle with the camera, or a puzzle generator.

### MVP 1's phases

Each phase is one Android concept. **Pair** marks the phases Tony writes himself, pair programming with Claude
(see below); Tony may move others to pair programming at any time.

| # | Concept | What it brings |
|---|---|---|
| 1 | Coroutines and `Flow`; the data layer (a repository) | `GameRepository` in front of the game; calls into Python off the UI thread |
| 2 | Dependency injection by hand (Google's manual DI); Hilt may follow later | An app container that builds the repository and the ViewModels |
| 3 | A second screen and its state (**pair**) | The splash screen with the copyright, shared with the terminal from `ui/copyright.py` |
| 4 | Navigation 3 | Splash, the layout picker (shown only with several layouts) and the game, through a Python entry point in `ui/android/` |
| 5 | Lifecycle, app storage and process death | Auto-save and resume |
| 6 | Top app bar and menus | New puzzle |
| 7 | Compose layout and Material components | The message area, and `inform()` as a dialog |
| 8 | The same, continued | The command palette, with the value/guess switch |
| 9 | Derived UI state (**pair**) | The pad, dimmed and with counts |
| 10 | Building and installing an APK | Finishing touches, and the app on Tony's phone; tag `mvp1` |

Branches are named `mvp<n>-phase<m>-<topic>`, e.g. `mvp1-phase1-data-layer`.

### How a phase goes

1. Explain its concept, and plan it with Tony.
2. Write failing tests first, then build it.
3. Try it on the emulator (and, once the app is far enough along, on the phone).
4. Commit once Tony has tried it and says so.
5. Fast-forward main and push only on his word, then delete the branch.

Every phase that touches `game/` keeps the terminal working: its tests pass and Tony checks it by hand.

**Pair programming:** in a **pair** phase Tony writes the code and Claude directs. Claude explains the next small
step, Tony writes it and asks questions, and Claude reviews what he wrote.

Claude sees Tony's edits only when he sends a message (the IDE passes the changes along, and Tony's editor saves
on losing focus), so Tony checks in at small steps. Claude doesn't edit the files in a pair phase unless Tony
asks.

**Phase 0, the foundation**, is on main (`d2db627`..`09339dc`): the project with Chaquopy, `Action.SELECT`, the
adapter and the MVVM structure.

It proved the board, a tap and a digit through `puzzle.handle()` on the game thread, and a blocking `confirm()`
answered through the queue.

## Design decisions

### An empty cell's small digits (decided 2026-11-13, built in MVP 2)

The terminal shows two rows of small digits in an empty cell: the marks on the middle line (Snyder marks, or
what a tagged cell must be) and the possible values on the bottom line, with the values removed as ruled out in
red before them. It runs out of room at 5 digits and shows `.....`.

The two rows are really one set of digits, each in a state: every mark is also a possible value (`cell.py`: Snyder
marks come from the candidates left after removals, and "must be" marks from those left after everything ruled
out). So the app shows them in **one 3x3 grid, each digit in its own place** (1 top left, 9 bottom right):

| A digit that is | is drawn |
|---|---|
| not possible | not at all |
| possible | small and gray |
| a mark (Snyder, or "must be" in a tagged cell) | bold, with a circle behind it |
| removed as ruled out | red, struck through |

The app keeps the terminal's meanings and colors, so a cell reads the same on the PC and the phone:

- A tagged cell's small digits are light sky blue; that is also how a "must be" mark is told from a Snyder mark.
- The values removed as ruled out are red.
- When a cell has lost values, its remaining possible values are yellow, drawing the eye to that cell.
- An `n` hint or `w` step colors the digits it points at, in their own places: yellow where a value can still go,
  red where it can't.

What the grid does better than the terminal: all nine digits always fit, so nothing becomes `.....`; every
removed value shows, not only the lowest few; and each digit stays in its place, so a row or column can be
scanned by position.

For this, `showCell()` (`ui/android/screen.py`) will also pass the cell's marks, its removed values and whether it
looks tagged, and `CellState` will carry them.

## Save files and configuration

- **Save files are interchangeable with the PC version.** The app reads and writes them only through the game
  (`game/save_file.py`, `GameFile`), never with Kotlin code of its own, so the format stays the game's.

  The game's settings (such as the "must be" marks) travel inside the save file, as on the PC.

  A setting that save files don't hold yet is a change to the save format, made in `game/` with a new format
  version, so the PC keeps reading the files.

- **App-only configuration** (things only the app has, such as theme, keypad layout or haptics) is stored on the
  phone with Jetpack DataStore, and never written into a save file.

- **Auto-save** (MVP 1) writes an ordinary save file into the app's own storage; MVP 3 adds the list of games and
  sharing without changing the format.

## Building

- The project was copied from the setup of Tony's BowlingPots project: AGP 9.5.1 with its built-in Kotlin,
  Kotlin 2.4.21, Compose BOM 2026.09.00, Gradle 9.9.0, compileSdk and targetSdk 37, minSdk 24.

- The `syncAppPython` task in `app/build.gradle.kts` copies `../game` and, of `../ui`, only `__init__.py`,
  `error_log.py` and `android/` (all without their tests) into `app/build/app-python/` before each build.

  Chaquopy packages them from there, so the app always runs the same game code as the terminal. Never edit the
  copy.

- The emulator is `Pixel_5` (x86_64). The first start after an install takes several seconds, while Chaquopy
  unpacks Python.

## Working with Tony

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
- He approves many commands by hand, so a command that times out may only be waiting for him.
- In Markdown, a list item longer than about two lines gets a paragraph break (a blank line, then indented text)
  at each change of idea, so no paragraph asks the reader to take in too much at once.
