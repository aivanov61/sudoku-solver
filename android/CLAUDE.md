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

`docs/architecture.md` draws it as Mermaid diagrams: an overview, then each feature (today the splash, the layouts
and the game) through the layers, with a sequence diagram for each. Update it at the end of each phase, marking what
the phase added and changed.

`MainActivity` hosts the screens in its composable `SudokuApp`, with Navigation 3: the back stack is a list of
`Route`s (`ui/Keys.kt`), saved through rotation and process death, and `NavDisplay` shows the last one.

Each entry gets its own ViewModels (`rememberViewModelStoreNavEntryDecorator()`). `SudokuApp` does the navigating,
replacing each route with the next, so Back leaves the app: the splash, then the game on the saved game's layout,
or else when there is exactly one layout that can be picked, else the layout picker, then the game on the layout
picked.

The game in progress is auto-saved to the app's own storage (`filesDir/autosave.json`, an ordinary save file):
the `Game` entry saves it whenever the app is stopped (`LifecycleEventEffect(ON_STOP)`), since Android may then end
the process without calling it, and the game restores itself from it when it starts. So a game survives Home, Back,
and process death, after which Nav 3 reopens straight on `Route.Game`.

The Kotlin code, in three packages, wired together by the app's container:

- **Dependency injection by hand** (Google's manual DI). `SudokuApplication`, which the manifest names, is made
  once per process before any screen, and makes the one `AppContainer` (`DefaultAppContainer`).

  The container owns the app-long coroutine scope, and the `GameRepository` of the game in play, through
  `gameRepository(layout)`. It makes the game with the `newGame` it is given (`{ layout -> PythonGame(this,
  layout, autoSave) }`), when first asked for, and makes a new one for another layout or once the game is over, so the app
  never reopens on a finished game.

  It also makes the `LayoutRepository` (`{ PythonLayoutRepository(this) }`) and the `SavedGameRepository`
  (`{ PythonSavedGameRepository(this, autoSave) }`), each when first asked for. `SudokuApplication` names the
  auto-save file and gives it to both.

  It also makes the `CopyrightRepository`, with the `newCopyrightRepository` it is given
  (`{ AssetCopyrightRepository(assets) }`), when first asked for. Taking ways to make things, rather than Android
  objects, keeps the container testable.

  ViewModel factories ask the container for what their ViewModels need, rather than making it themselves.

- **`game/` is the data source**: the game as the app sees it. `Game` is an interface whose `events` is a `Flow`
  of typed `GameEvent`s, and which takes typed `GameAction`s.

  `PythonGame` implements it, on the board of a layout it is given by name, auto-saved to the file it is given.
  Collecting `events` starts the game on
  the game thread (off the UI thread), and `callbackFlow` turns the game's reports into the flow, which ends when
  the game is over.

  An error that reaches `PythonGame`, while starting or later, ends the flow with `GameEvent.Failed`: the screen
  shows why in place of the board, and the container makes a new game when next asked. An error in one of the
  player's actions doesn't reach it: `AndroidUI` shows it as a warning, and play goes on.

  Only `game/` knows Chaquopy: `PythonGame`, `PythonLayoutRepository` (the layouts, from
  `ui/android/catalog.py`'s `Catalog`, which also makes a layout's board), `PythonSavedGameRepository` (the saved
  game's layout, from `ui/android/auto_save.py`'s `AutoSave`) and `AppPython`, which starts Python once for all of
  them, on first use (slow the first time after an install).

  `PythonScreen` implements the adapter's `Screen` (`ui/android/screen.py`), turning each call into a
  `GameEvent`. `GameNames.kt` maps the game's names (Action values, cell kinds, edges, message kinds) to Kotlin
  enums.

- **`data/` is the data layer.** `GameRepository` is the one way to the game: it folds the events into a
  `StateFlow<GameState>` that lives in an app-long scope.

  It runs `act()` and `answer()` on `Dispatchers.IO`, off the UI thread, one at a time
  (`limitedParallelism(1)`), so the game gets the player's actions in the order they were made.

  `save()` returns at once and launches the save in the app-long scope, on the same one-at-a-time dispatcher: Back
  clears the game's ViewModel right after `ON_STOP`, which would cancel a save in its `viewModelScope`.

  `GameState.after(event)` works out each event's effect; `GameState` holds only what the game reported.

  `CopyrightRepository` is the one way to the GNU GPL notice. `AssetCopyrightRepository` reads it from the app's
  assets (`copyright.txt`, packaged from the repository's `ui/copyright.txt`) on `Dispatchers.IO`, and reflows it
  (`String.reflow()` in `Reflow.kt`): the file breaks its lines for the terminal, so each paragraph's lines are joined,
  for the screen to wrap to its own width.

  `SavedGameRepository` is the one way to the saved game before a game is started: `savedLayout()`, the layout it is
  on, or null when there is none or it can't be read (the game then says why).

- **`ui/` holds the ViewModels and the screens.** `SudokuViewModel` turns the repository's state into one
  immutable `SudokuUiState` (the game's state plus what the screen works out, such as the mode switch) as a
  `StateFlow`.

  It implements `SudokuIntents` (`onDigit()`, `onCellTapped()`, ...), each launched in `viewModelScope`, and
  `onStopped()`, which the activity calls when the app is stopped, to have the game saved. `SudokuScreen` is
  stateless.

  `SplashViewModel` reads the notice; the layouts, then the saved game's layout (which starts Python behind the
  splash); and starts a 5-second timer, each in its own coroutine in `viewModelScope`; the timer or `onTap()` ends
  the splash. Once it has ended and the layouts and saved game are known, `SplashUiState.next` is the route that
  follows. `SplashScreen` is stateless:
  the title at the top, and the notice centred below it.

  `LayoutPickerViewModel` reads the layouts for the stateless `LayoutPickerScreen`, which says so when none can be
  picked. A pick is navigation, so it goes up to `SudokuApp` as a lambda, not to the ViewModel.

- **Unit tests** (`app/src/test`, `gradle :app:testDebugUnitTest`) cover `GameState`, the repository, the
  ViewModels and the container, over `FakeGame`, `FakeCopyrightRepository`, `FakeLayoutRepository` (which can
  hold the layouts back, as a slow start of Python would) and `FakeSavedGameRepository`, and `PythonScreen`;
  Python doesn't run in them.

  They use `kotlinx-coroutines-test`, and `MainDispatcherRule` stands in for the UI thread. The splash's timing
  is tested on virtual time (`advanceTimeBy`, `runCurrent`).

  Composables have no unit tests: Compose UI tests (`createComposeRule`) are planned for the redesigned game
  screen.

On the Python side, `ui/android/android_ui.py`'s `AndroidUI` is the port's adapter. `play()` runs on the game
thread, taking requests from one queue: the actions that `act()` puts there, and the saves that `save()` puts
there, so a save never lands in the middle of a move.

`ui/android/auto_save.py`'s `AutoSave` keeps the game in the auto-save file, through `SaveFile`: `play()` has it
restore the game first, and forget (delete) it once the game is over. A file it can't restore (damaged, from a
newer version, or on another layout) gets a warning, and is kept until the player has something to save, so they
can still install a newer version or keep the file.

`confirm()` waits on a second queue that `answer()` fills, then reports `questionAnswered()`.

Gaps against the guide, to close in the phases that need them:

- `inform()` doesn't wait yet, so a warning flashes and vanishes.

  The status line has no fixed height, so a wrapped message moves the buttons.

  Both are left for the MVP 1 screen redesign.

- The game screen doesn't adapt to the window: the board is sized to the full width, so in landscape it is taller
  than the screen, and the pad and buttons fall off the bottom.

  Left for the screen redesign (phases 7 and 8): the board sized to the smaller of width and height, and in
  landscape the message area, command palette and pad beside it. The orientation isn't locked, since Android
  ignores that on large screens.

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
| 3 | A second screen and its state (**pair**) | The splash screen with the copyright, shared with the terminal from `ui/copyright.txt` |
| 4 | Navigation 3 | Splash, the layout picker (shown only with several layouts) and the game, through a Python entry point in `ui/android/` |
| 5 | Lifecycle, app storage and process death | Auto-save and resume |
| 6 | Top app bar and menus | New puzzle |
| 7 | Compose layout and Material components | The message area, and `inform()` as a dialog |
| 8 | The same, continued | The command palette, with the value/guess switch |
| 9 | Derived UI state (**pair**) | The pad, dimmed and with counts |
| 10 | Building and installing an APK | Finishing touches, and the app on Tony's phone; tag `mvp1` |

Branches are named `mvp<n>-phase<m>-<topic>`, e.g. `mvp1-phase1-data-layer`.

### How a phase goes

1. Explain its concept, and plan it with Tony. **The architecture is a deliverable of planning:** as much of it as
   can be planned is drawn before coding starts, and planning isn't done until it is.
2. **Update `docs/architecture.md` first**, before any code: the phase's new and changed parts in green and amber,
   those not written yet marked `*`. Take each `*` off as its part gets written; none is left when the phase ends.

   A phase built in steps (4a, 4b, ...) keeps its colors for the whole phase; `*` marks what the step being built
   adds, and `*(4c)` what a later step does.

   Architecture comes first unless it isn't clear yet; then TDD lets it emerge, and the doc follows as it does.
3. Write failing tests first, then build it.
4. Try it on the emulator (and, once the app is far enough along, on the phone).
5. Commit once Tony has tried it and says so.
6. Fast-forward main and push only on his word, then delete the branch.

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

### Choosing a saved game to restore (decided 2026-11-19, built in MVP 3)

Restoring shows the saved files that can be restored, as a list, with a search field above it. Typing filters the
list the way VS Code's file picker does: a file matches when the letters typed appear in its name in order, not
necessarily side by side (`frs` matches `first-try`).

The matching letters are highlighted, and names whose matches form longer runs of letters, or start a word, come
first.

This takes the place of `ask_file_name()`'s typed name, which the terminal keeps.

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

- The `syncSharedAssets` task copies the repository's files the app shows as they are into its assets (read with
  `context.assets`): today the GNU GPL notice, `ui/copyright.txt`, which the terminal shows too. It is wired in
  with the Variant API (`addGeneratedSourceDirectory`), so every step that needs the assets runs it first.

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
- Temporary code, in the app or its tests, says so in its comment: "Temporary, deleted in phase N: ...", and why
  it shouldn't stay. Code that stays never reads as temporary.
- In Markdown, a list item longer than about two lines gets a paragraph break (a blank line, then indented text)
  at each change of idea, so no paragraph asks the reader to take in too much at once.
