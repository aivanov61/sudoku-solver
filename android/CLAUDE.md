# CLAUDE.md (Android app)

This folder is the Android Studio project for an Android user interface to the sudoku game. The game itself is
the Python package `game/` one level up, and the working preferences in `../CLAUDE.md` apply here too. Read it
first, together with `../DesignDoc.md` (especially the user interface port, section 4.4).

## Goals

- **Play on Tony's own phone.** Publishing on the Play Store is parked: it may be explored after MVP 3.
- **Modern Android App Architecture is a key goal that drives the development**, together with clean-code MVVM
  (see Architecture). New work follows Google's guide to app architecture; where the code falls short of it, say
  so and plan the step that closes the gap.
- **A modern app design**: Material 3, with menus, settings and keypads as a phone user expects them. The screen
  design is Tony's call; propose, and ask him.

## Approach (agreed 2026-11-09)

- **The game stays in Python, unchanged**, and runs inside the app through Chaquopy, version 17.2.0. Chaquopy's
  own version table says it supports Python 3.10–3.15 and Android Gradle plugin 7.3–9.5. The app uses Python
  3.15, the same as the PC; the game needs 3.14 or later because of lazy annotations and `type` aliases.
- **The UI is native Kotlin with Jetpack Compose.**
- **A Python adapter, `ui/android/`, beside `ui/terminal/`,** implements the `UserInterface` port
  (`game/user_interface.py`) and passes each call on to Kotlin. The player's actions come back the other way as
  `puzzle.handle(action, digit, position)`; a tap on a cell is `Action.SELECT` with its `(row, col)` position. It
  belongs in the repo's `ui/` so the repo's tests, ruff and pyright cover it.
- **Dialogs stay synchronous**, which is Tony's earlier decision. `confirm()`, `ask_file_name()`,
  `configure()` and `walk_through()` block until the player answers, so the game runs on its own thread. A
  dialog posts its request to the UI thread and waits on a queue for the answer. Never block the UI thread.
- **Touch takes the place of keys.** The game already works in `Action`s (`game/actions.py`), so taps map to
  actions.

## Architecture

Modern Android App Architecture, as Google's guide describes it:

- **Separation of concerns, in layers.** The UI layer is Compose screens plus ViewModels, which hold the UI state.
  The data layer is repositories, each the one way to its data, over data sources. A domain layer (use cases) is
  added only when logic is shared between ViewModels.
- **A single source of truth for each kind of data.** The Python game is it for the puzzle: the app never keeps
  game rules or game state of its own, only what the game last reported. DataStore is it for app-only settings.
- **Unidirectional data flow.** State flows down as an immutable UI state (`StateFlow`); the player's intents flow
  up as calls on the ViewModel. Composables are stateless: they show the state and pass taps on.
- **Recommended practices.** Kotlin coroutines and `Flow`, lifecycle-aware collection, dependency injection,
  and unit tests for each layer with fakes in place of the real data sources.

Clean-code MVVM is how the UI layer does this, and `../CLAUDE.md`'s preferences (TDD, small focused functions,
no dead code, DRY, open/closed) apply to the Kotlin code as much as to the Python.

### Where the code is now

The Kotlin code, in two packages:

- `game/` is the model as the app sees it. `Game` is an interface that reports typed `GameEvent`s and takes
  typed `GameAction`s. `PythonGame` implements it, and is the only code that knows Chaquopy: it starts Python and
  the game on the game thread (off the UI thread, as the first start takes seconds). `PythonScreen` implements
  the adapter's `Screen` (`ui/android/screen.py`), turning each call into a `GameEvent`. `GameNames.kt` maps the
  game's names (Action values, cell kinds, edges, message kinds) to Kotlin enums.
- `ui/` holds the ViewModel and the view. `SudokuViewModel` exposes one immutable `SudokuUiState` as a
  `StateFlow`, and implements `SudokuIntents` (`onDigit()`, `onCellTapped()`, ...). `SudokuUiState.after(event)`
  works out each event's effect on the state. `SudokuScreen` is stateless.
- Unit tests (`app/src/test`, `gradle :app:testDebugUnitTest`) cover the state, the ViewModel with a fake
  `Game`, and `PythonScreen`; Python doesn't run in them.

On the Python side, `ui/android/android_ui.py`'s `AndroidUI` is the port's adapter. `play()` runs on the game
thread, taking actions from a queue that `act()` fills; `confirm()` waits on a second queue that `answer()` fills.

Gaps against the guide, to close in the phases that need them:

- There is no data layer yet: the ViewModel talks to `Game` directly. A `GameRepository` that exposes the game
  as a `Flow` belongs in front of it once a second consumer or auto-save arrives.
- Dependency injection is a hand-made `ViewModelProvider.Factory`. Choose with Tony between Hilt and a small
  hand-made container before the second ViewModel or repository.
- The game reports through callbacks on its own thread rather than a `Flow`; `callbackFlow` would bring it in line.
- Kotlin's calls into Python (`act`, `answer`) wait for the GIL, so the UI thread can stall while the game
  computes (e.g. a long `a`, in MVP 2). Before that, move the calls off the UI thread or use a Java-side queue.
- `inform()` doesn't wait yet, so a warning flashes and vanishes; the status line has no fixed height, so a
  wrapped message moves the buttons. Both are left for the MVP 1 screen redesign.

## Stages and phases

The app is built in MVP stages. **An MVP is a milestone**, tagged in git when its last phase lands (`mvp1`,
`mvp2`, ...). **Each MVP is built in phases**: each a slice Tony can try by hand, on its own branch off main,
merged to main when done.

- **MVP 1, play a puzzle on the phone from start to finish:** a redesigned modern screen (board, keypad, a
  toolbar or menu for commands), setup of the givens, play with values and guesses (a value/guess switch in place
  of Shift, guess-depth shading), clear, undo, rewind, conflicts, dead ends and completion; `inform()` and the
  status area done properly; and auto-save, so a game survives the app going to the background and Android ending
  it. Installed on Tony's phone from Android Studio or as an APK.
- **MVP 2, the solving help:** `n` and `a` with their hints and highlights, `w`'s walk through the removals, tags,
  "must be" marks (Snyder notation) and ruled-out values, and a configuration screen built from the game's
  `ConfigOption`s.
- **MVP 3, more puzzles and games:** a list of saved games (new, resume, delete), the layout picker from the
  puzzle catalog, and sharing save files with the PC.
- **Parked:** the Play Store (adaptive layouts, release signing, store listing, privacy, the GPL's source offer),
  and ideas such as entering a puzzle with the camera or a puzzle generator.

A phase goes: plan it with Tony, write failing tests first, build it, try it on the emulator (and, once the app
is far enough along, on the phone), commit once Tony has tried it and says so, then fast-forward main and push
only on his word, and delete the branch. Every phase that touches `game/` keeps the terminal working: its tests
pass and Tony checks it by hand.

**Phase 0, the foundation**, is the branch `android-app`: the project with Chaquopy, `Action.SELECT`, the
adapter and the MVVM structure. It proved the board, a tap and a digit through `puzzle.handle()` on the game
thread, and a blocking `confirm()` answered through the queue.

## Save files and configuration

- **Save files are interchangeable with the PC version.** The app reads and writes them only through the game
  (`game/save_file.py`, `GameFile`), never with Kotlin code of its own, so the format stays the game's. The
  game's settings (such as the "must be" marks) travel inside the save file, as on the PC. A setting that save
  files don't hold yet is a change to the save format, made in `game/` with a new format version, so the PC keeps
  reading the files.
- **App-only configuration** (things only the app has, such as theme, keypad layout or haptics) is stored on the
  phone with Jetpack DataStore, and never written into a save file.
- **Auto-save** (MVP 1) writes an ordinary save file into the app's own storage; MVP 3 adds the list of games and
  sharing without changing the format.

## Building

- The project was copied from the setup of Tony's BowlingPots project: AGP 9.5.1 with its built-in Kotlin,
  Kotlin 2.4.21, Compose BOM 2026.09.00, Gradle 9.9.0, compileSdk and targetSdk 37, minSdk 24.
- The `syncAppPython` task in `app/build.gradle.kts` copies `../game` and, of `../ui`, only `__init__.py`,
  `error_log.py` and `android/` (all without their tests) into `app/build/app-python/` before each build, and
  Chaquopy packages them from there. So the app always runs the same game code as the terminal. Never edit the copy.
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
