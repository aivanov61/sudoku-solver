# The Android app's architecture

How the app's code maps onto MVVM and Modern Android App Architecture, and how the parts talk to each other.
Updated at the start of each phase and as it goes; this is **MVP 1, phase 5** (lifecycle, app storage and process
death).

Phase 5 is built in three steps:

- 5a, in Python: `AutoSave` saves the game to the app's storage when asked, restores it when the game starts, and
  deletes it once the game is over.
- 5b: the game screen asks for the save when the app is stopped (`ON_STOP`), through the ViewModel and the
  repository.
- 5c: the splash reads which layout the auto-save is on, through a `SavedGameRepository`, and resumes that game.

The app is drawn as an overview, then one section per feature (a screen with its ViewModel and data), each
through the same layers. Features share only the app's container and the activity that hosts their screens.

Colors: green is new in phase 5, amber is changed in phase 5, uncolored is unchanged. The colors cover the whole
phase, through all its steps, so 5a's parts stay colored.

Marks: none are left, as all three steps are written. While a phase is built, * marks what the step being built
adds but hasn't written yet, and *(5c) what a later step does.

Arrows: solid arrows are calls; dotted arrows are data flowing back, or a class implementing an interface.

## Overview

```mermaid
flowchart TB
    subgraph App["App · dependency injection by hand"]
        direction LR
        SudokuApplication --> AppContainer
    end

    subgraph Host["View · the activity that hosts the screens"]
        direction LR
        MainActivity["MainActivity"] --> NavDisplay["NavDisplay · back stack of Routes"]
    end

    subgraph Splash["Splash feature: Route.Splash"]
        SplashFeature["SplashScreen · SplashViewModel · CopyrightRepository · SavedGameRepository"]
    end

    subgraph Layouts["Layouts feature: Route.LayoutPicker"]
        LayoutsFeature["LayoutPickerScreen · LayoutPickerViewModel · LayoutRepository"]
    end

    subgraph Game["Game feature: Route.Game(layout)"]
        GameFeature["SudokuScreen · SudokuViewModel · GameRepository · AutoSave"]
    end

    subgraph Storage["App storage · filesDir"]
        AutoSaveFile["autosave.json"]
    end

    NavDisplay -- "first" --> SplashFeature
    SplashFeature -- "a saved game, or one layout, which can be picked: replaced by" --> GameFeature
    SplashFeature -- "otherwise: replaced by" --> LayoutsFeature
    LayoutsFeature -- "a pick: replaced by" --> GameFeature
    AppContainer -- "copyrightRepository, layoutRepository, savedGameRepository" --> SplashFeature
    AppContainer -- "layoutRepository" --> LayoutsFeature
    AppContainer -- "gameRepository(layout)" --> GameFeature
    GameFeature -- "saves, restores, deletes" --> AutoSaveFile
    SplashFeature -- "reads its layout" --> AutoSaveFile

    classDef new fill:#2e7d32,stroke:#a5d6a7,stroke-width:2px,color:#ffffff
    classDef changed fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff
    class AutoSaveFile new
    class SudokuApplication,AppContainer,MainActivity,SplashFeature,GameFeature changed
```

| Class | What it does |
|---|---|
| `SudokuApplication` | Made by Android once per process, before any screen (the manifest names it); makes the one `AppContainer`, giving it `newGame` (a `PythonGame` on the layout named), `newLayoutRepository`, `newCopyrightRepository` and `newSavedGameRepository`. It names the auto-save file, `filesDir/autosave.json`, and gives it to both the game and the saved game's repository |
| `AppContainer` | The app's dependencies (`DefaultAppContainer`): the app-long scope; `gameRepository(layout)`, the game in play, made when first asked for and anew for another layout or once the game has ended (over, or failed: `GameState.hasEnded`, so reopening the app tries again); and the `LayoutRepository`, `CopyrightRepository` and `SavedGameRepository`, each made when first asked for |
| `MainActivity` | Its composable `SudokuApp` holds the back stack (`rememberNavBackStack(Route.Splash)`, kept through rotation and process death) and shows it with `NavDisplay`; `rememberViewModelStoreNavEntryDecorator()` gives each entry its own ViewModels, which live as long as its route is on the stack. Each entry is a small composable (`Splash`, `LayoutPicker`, `Game`) that gets its ViewModel and shows its screen. `SudokuApp` does the navigating (`replaceLast`): it replaces the splash with the splash's `next` route once there is one, and the picker with `Route.Game(layout)` when the player picks one; the game's entry closes the app once the game is over, and has the game saved whenever the app is stopped (`LifecycleEventEffect(ON_STOP)`) |
| `Route` | `ui/Keys.kt`: Navigation 3's keys, one per screen, in a sealed interface (so `Route.Game` doesn't clash with the `Game` interface): `Route.Splash`, `Route.LayoutPicker` and `Route.Game(layout)`, each a `@Serializable` `NavKey`. Each step replaces the route before it, so Back from the picker or the game leaves the app. After process death the stack comes back as it was, so the app reopens on `Route.Game(layout)` without the splash, and the game restores itself from the auto-save |
| `autosave.json` | The game in progress, in app-specific internal storage (`filesDir`: no permission needed, private to the app, deleted on uninstall). It is an ordinary save file, written and read only by the game (`game/save_file.py`), so it is interchangeable with the PC's |

### Where the app's state lives

| Where | Survives | Holds |
|---|---|---|
| ViewModel | rotation | each screen's UI state |
| Saved instance state (the Nav 3 back stack) | rotation and process death; not Back, or a swipe from Recents | the `Route`s |
| App storage (`filesDir`) | everything, until the app is uninstalled | the game in progress, `autosave.json` |

Android may end a stopped app's process at any time, without calling it, so the game is saved when the app is
stopped (`ON_STOP`): on Home, Back, a switch to another app, and a rotation.

## The splash feature

```mermaid
flowchart TB
    subgraph View["View · Compose · UI thread"]
        SplashScreen
    end

    subgraph VM["ViewModel"]
        direction LR
        SplashViewModel --- SplashUiState
    end

    subgraph DataLayer["Model · data layer · data/"]
        direction LR
        AssetCopyrightRepository -. implements .-> CopyrightRepository["«interface» CopyrightRepository"]
        FakeCopyrightRepository["FakeCopyrightRepository (tests)"] -. implements .-> CopyrightRepository
        SavedGameRepository["«interface» SavedGameRepository"]
        FakeSavedGameRepository["FakeSavedGameRepository (tests)"] -. implements .-> SavedGameRepository
    end

    subgraph DataSource["Model · data source"]
        Assets["app assets: copyright.txt"]
        PythonSavedGameRepository["PythonSavedGameRepository (game/)"]
    end

    subgraph Python["Python"]
        AutoSave["AutoSave (ui/android)"]
    end

    SplashScreen -- "onTap" --> SplashViewModel
    SplashViewModel -. "StateFlow‹SplashUiState›" .-> SplashScreen
    SplashViewModel -- "notice()" --> CopyrightRepository
    SplashViewModel -- "layouts(), see the layouts feature" --> LayoutRepository["LayoutRepository"]
    SplashViewModel -- "savedLayout()" --> SavedGameRepository
    AssetCopyrightRepository -- "reads, on Dispatchers.IO" --> Assets
    PythonSavedGameRepository -. implements .-> SavedGameRepository
    PythonSavedGameRepository -- "Chaquopy, on Dispatchers.IO" --> AutoSave

    classDef new fill:#2e7d32,stroke:#a5d6a7,stroke-width:2px,color:#ffffff
    classDef changed fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff
    class SavedGameRepository,FakeSavedGameRepository,PythonSavedGameRepository,AutoSave new
    class SplashViewModel changed
```

The notice's one copy is the repository's `ui/copyright.txt`: the build packages it as an asset
(`syncSharedAssets`), and the terminal reads it too.

| Layer | Class | What it does |
|---|---|---|
| View | `SplashScreen` | Stateless: the title at the top, the notice centred in the space below (a `Column` with a weighted `Box`); the whole screen reports a tap with `onTap` |
| ViewModel | `SplashViewModel` | Reads the notice from the `CopyrightRepository` and starts a 5-second timer, both in `viewModelScope`; `onTap()` ends the splash at once; its state lives in a `MutableStateFlow`; its `Factory` gets the repositories from the app's container. It also reads the layouts (which starts Python behind the splash) and the saved game's layout, and once the splash has ended and both are known, gives the route that replaces it: `Route.Game(layout)` for the saved game's layout when it can be picked, else for the only layout when there is exactly one and it can be picked, as the terminal plays it, otherwise `Route.LayoutPicker` |
| ViewModel | `SplashUiState` | The notice (empty until read), and `next`, the route that replaces the splash, null until the splash has ended and the layouts and the saved game are known |
| Data layer | `CopyrightRepository` | The interface: the one way to the GNU GPL notice, `suspend fun notice(): String` |
| Data layer | `AssetCopyrightRepository` | The real one: reads `copyright.txt` from the app's assets on `Dispatchers.IO`, and reflows it (`String.reflow()`): the file breaks its lines for the terminal, so each paragraph's lines are joined, for the screen to wrap to its own width |
| Data layer | `FakeCopyrightRepository` | A true fake for tests: returns the text it was given |
| Data layer | `SavedGameRepository` | The interface: the one way to what the auto-save holds before a game is started, `suspend fun savedLayout(): String?`, the name of the layout it is on, or null when there is none, or it can't be read (the game says why when it starts) |
| Data layer | `FakeSavedGameRepository` | A true fake for tests: returns the layout it was given |
| Data source | `PythonSavedGameRepository` | The real one: asks the Python `AutoSave` for the layout of the auto-save file, through Chaquopy, on `Dispatchers.IO` |
| Data source | app assets | `copyright.txt`, packaged from the repository's `ui/copyright.txt` by the build |
| Python | `AutoSave` | `ui/android/auto_save.py` (see the game feature): `saved_layout()` reads the file through `SaveFile` |

### From start through splash to game

```mermaid
sequenceDiagram
    autonumber
    participant M as MainActivity<br/>(UI thread)
    participant S as SplashScreen<br/>(UI thread)
    participant VM as SplashViewModel<br/>(viewModelScope)
    participant R as CopyrightRepository<br/>(IO pool)
    participant L as LayoutRepository<br/>(IO pool)
    participant SG as SavedGameRepository<br/>(IO pool)

    M->>VM: made, through its Factory
    VM->>R: launch { notice() }
    VM->>L: launch { layouts(), then savedLayout() }: starts Python
    VM->>VM: launch { delay(5 s) }
    R-->>VM: the notice's text
    VM-->>S: StateFlow‹SplashUiState›: the notice
    Note over S: shows the title and the notice
    alt the player taps
        S->>VM: onTap()
    else 5 seconds pass
        Note over VM: the delay ends
    end
    L-->>VM: the layouts
    VM->>SG: savedLayout(), in the same coroutine
    SG-->>VM: the saved game's layout, or null
    VM-->>M: StateFlow‹SplashUiState›: the next key, once ended and both known
    Note over M: replaces Splash on the back stack with<br/>Game(saved layout), Game(the only layout) or LayoutPicker
```

Python starts behind the splash: reading the layouts starts it, and its slow first start overlaps the 5 seconds.
The layouts and the saved game are read one after the other, in one coroutine, as both go through the one
Python. If the splash is tapped before they are known, it waits for them. The splash's ViewModel
lives only while `Splash` is on the back stack, so its timer ends with it.

## The layouts feature

```mermaid
flowchart TB
    subgraph Host["View · the activity that hosts the screens"]
        SudokuApp["MainActivity.SudokuApp"]
    end

    subgraph View["View · Compose · UI thread"]
        LayoutPickerScreen
    end

    subgraph VM["ViewModel"]
        direction LR
        LayoutPickerViewModel --- LayoutPickerUiState
    end

    subgraph DataLayer["Model · data layer · data/"]
        direction LR
        LayoutRepository["«interface» LayoutRepository"]
        FakeLayoutRepository["FakeLayoutRepository (tests)"] -. implements .-> LayoutRepository
        LayoutRepository --- Layout
    end

    subgraph DataSource["Model · data source · game/"]
        direction LR
        PythonLayoutRepository -- "starts Python, once" --> AppPython
    end

    subgraph Python["Python"]
        direction LR
        Catalog["Catalog (ui/android)"] --> PuzzleCatalog["PuzzleCatalog (game/)"]
    end

    LayoutPickerScreen -- "onPick(layout): replaces the picker with Game(layout)" --> SudokuApp
    LayoutPickerViewModel -. "StateFlow‹LayoutPickerUiState›" .-> LayoutPickerScreen
    LayoutPickerViewModel -- "layouts()" --> LayoutRepository
    PythonLayoutRepository -. implements .-> LayoutRepository
    PythonLayoutRepository -- "Chaquopy, on Dispatchers.IO" --> Catalog
```

| Layer | Class | What it does |
|---|---|---|
| View | `LayoutPickerScreen` | Stateless: a Material 3 list of the layouts (`ListItem`s), each with its label; a broken one is shown, with its notes, but can't be picked. When none can be picked, it says so above the list, so the notes explain why; Back leaves the app. A pick goes up as `onPick(layout)`, which `SudokuApp` handles: picking is navigation, so it is the UI's to do, not the ViewModel's |
| ViewModel | `LayoutPickerViewModel` | Reads the layouts for the picker, in `viewModelScope`; its `Factory` gets the repository from the app's container |
| ViewModel | `LayoutPickerUiState` | The layouts (null until read), and `noneCanBePicked`: they are known and none can be picked, so the screen says so |
| Data layer | `Layout` | One layout: its `name`, its `label` (the name and any notes, as the terminal shows it), and whether it `canPick` |
| Data layer | `LayoutRepository` | The interface: the one way to the puzzle layouts, `suspend fun layouts(): List<Layout>` |
| Data layer | `FakeLayoutRepository` | A true fake for tests: returns the layouts it was given; a test can hold them back until it releases them, as a slow first start of Python would |
| Data source | `PythonLayoutRepository` | The real one: asks the Python `Catalog` for the layouts, through Chaquopy, on `Dispatchers.IO` |
| Data source | `AppPython` | Starts the app's one Python on first use, synchronized, for the layouts, the saved game and the game; slow the first time after an install |
| Python | `Catalog` | `ui/android/catalog.py`: lists the layouts in plain values, and makes the board of the one named; it plays the part `Main` plays for the terminal |
| Python | `PuzzleCatalog` | The game's catalog (`game/`): finds the layouts in `game/puzzles/` |

## The game feature

```mermaid
flowchart TB
    subgraph Host["View · the activity that hosts the screens"]
        GameEntry["MainActivity's Game entry · LifecycleEventEffect(ON_STOP)"]
    end

    subgraph View["View · Compose · UI thread"]
        SudokuScreen
    end

    subgraph VM["ViewModel"]
        direction LR
        SudokuViewModel["SudokuViewModel"] --- SudokuUiState
    end

    subgraph DataLayer["Model · data layer · data/"]
        direction LR
        GameRepository["GameRepository"] --- GameState
    end

    subgraph DataSource["Model · data source · game/"]
        direction LR
        PythonGame["PythonGame"] -. implements .-> Game["«interface» Game"]
        GameEvent
        FakeGame["FakeGame (tests)"] -. implements .-> Game
        PythonScreen
    end

    subgraph Python["Python · game thread"]
        direction LR
        AndroidUI["AndroidUI"] --> Puzzle["Puzzle, Board, Cell"]
        AndroidUI --> AutoSave["AutoSave"]
        AutoSave --> SaveFile["SaveFile (game/)"]
    end

    subgraph Storage["App storage · filesDir"]
        AutoSaveFile["autosave.json"]
    end

    GameEntry -- "onStopped()" --> SudokuViewModel
    SudokuScreen -- "intents" --> SudokuViewModel
    SudokuViewModel -. "StateFlow‹SudokuUiState›" .-> SudokuScreen
    SudokuViewModel -- "act(), answer(), save()" --> GameRepository
    GameRepository -. "StateFlow‹GameState›" .-> SudokuViewModel
    GameRepository -- "act(), answer(), save()" --> Game
    Game -. "Flow‹GameEvent›" .-> GameRepository
    PythonGame -- "Chaquopy" --> AndroidUI
    AndroidUI -. "showCell(), askConfirm() …" .-> PythonScreen
    PythonScreen -. "GameEvent" .-> PythonGame
    PythonGame -- "Catalog.board(layout), see the layouts feature" --> AndroidUI
    SaveFile -- "writes, reads" --> AutoSaveFile

    classDef new fill:#2e7d32,stroke:#a5d6a7,stroke-width:2px,color:#ffffff
    classDef changed fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff
    class AutoSave,AutoSaveFile new
    class GameEntry,SudokuViewModel,GameRepository,PythonGame,Game,FakeGame,AndroidUI changed
```

Everything from `GameRepository` down is MVVM's **Model**, which Google's guide splits into the data layer and
its data sources. The Python game is at the bottom, as the source of truth for the puzzle.

| Layer | Class | What it does |
|---|---|---|
| View | `MainActivity`'s `Game` entry | Gets the ViewModel and shows the screen; closes the app once the game is over; and calls `onStopped()` whenever the app is stopped, with `LifecycleEventEffect(Lifecycle.Event.ON_STOP)`, which runs only while the entry is on screen |
| View | `SudokuScreen` | Stateless composables: draws the state, and passes taps on as intents (`SudokuIntents`); when the game has failed, shows why ("The game stopped: …") in place of the board, or of "Starting the game…" |
| ViewModel | `SudokuViewModel` | `uiState = repository.state.map { SudokuUiState(it) }.stateIn(viewModelScope, WhileSubscribed(5 s))`; each intent is `viewModelScope.launch { repository.act(...) }`; `onStopped()` asks the repository to save the game; `factory(layout)` gets the game on that layout from the app's container |
| ViewModel | `SudokuUiState` | The game's state, plus what the screen works out from it (the mode switch) |
| Data layer | `GameRepository` | The one way to the game, in an app-long scope: `state = events.runningFold(GameState()) { s, e -> s.after(e) }.stateIn(scope, Eagerly)`; `act()` and `answer()` run on `Dispatchers.IO`, one at a time, so they keep their order. `save()` doesn't wait: it launches the save in the app-long scope, on the same one-at-a-time dispatcher, so it isn't canceled when Back clears the ViewModel right after `ON_STOP`, and it comes after the actions already made |
| Data layer | `GameState` | Only what the game reported; `after(event)` works out each event's effect; including `GameEvent.Failed`, which sets `failure`, the reason the game stopped. `failure` is kept apart from `isOver`, since `isOver` closes the app and the player would never see why; `hasEnded` is either |
| Data source | `Game` | The interface: `events: Flow<GameEvent>`, `act()`, `answer()`, `save()` |
| Data source | `GameEvent` | What the game reports (`Started`, `CellChanged`, `Over`, ...), and `Failed(reason)`: the game has stopped on an error, while starting or later, and its flow ends |
| Data source | `PythonGame` | The real game, on the layout named, auto-saved to the file it is given: `events = callbackFlow { ... }` starts the game thread, on the board from `Catalog.board(layout)` (with Python started by `AppPython`), and ends when the game is over; `act()` and `save()` call `AndroidUI` through Chaquopy. Any error that reaches it, in setting up or in play, is reported as `GameEvent.Failed`, so the app never waits on a game that can't start or no longer answers (an error in one of the player's actions doesn't reach it: `AndroidUI` catches that, and play goes on) |
| Data source | `PythonScreen` | What Python calls (`showCell()`, `askConfirm()`, `questionAnswered()`, ...), turned into `GameEvent`s |
| Data source | `FakeGame` | A stand-in for tests: reports the events it is given, records the actions and the saves |
| Python | `AndroidUI` | The port's adapter (`ui/android/`): `act()` and `save()` → one requests queue → `play()`, so a save never lands in the middle of a move; an action goes to `puzzle.handle()`, a save to `AutoSave`. `play()` has `AutoSave` restore the game first, and forget it once the game is over; `confirm()` waits for `answer()` |
| Python | `AutoSave` | `ui/android/auto_save.py`: the game in progress, in the file it is given, read and written through `SaveFile`. `restore()` restores the file's puzzle into the game, or warns why it can't (damaged, from a newer version, or on another layout) and leaves the file alone; `save()` writes the game when the board has values; `forget()` deletes the file once the game is over. A file it couldn't read is overwritten only once the player has something to save, and is never deleted, so the player can still install a newer version or keep the file |
| Python | `SaveFile` | The game's save files (`game/save_file.py`), the same format as on the PC |
| Python | `Puzzle`, `Board`, `Cell`, ... | The game itself (`game/`): the single source of truth for the puzzle; `saved_state()` and `restore()` |

### One tap, end to end: entering 5 in the selected cell

```mermaid
sequenceDiagram
    autonumber
    participant S as SudokuScreen<br/>(UI thread)
    participant VM as SudokuViewModel<br/>(UI thread)
    participant R as GameRepository<br/>(IO pool for act)
    participant PG as PythonGame
    participant UI as AndroidUI<br/>(game thread)
    participant P as Puzzle<br/>(game thread)
    participant PS as PythonScreen<br/>(game thread)

    S->>VM: onDigit(5)
    VM->>R: viewModelScope.launch { act(VALUE, 5) }
    R->>PG: withContext(IO) { act(VALUE, 5) }
    PG->>UI: act("value", digit=5)
    UI-->>PG: queued: returns at once
    Note over UI: play() takes the action off the queue
    UI->>P: handle(VALUE, 5)
    P->>UI: cell_changed(cell), for the cell and each related cell
    UI->>PS: showCell(...)
    PS-->>R: GameEvent.CellChanged, through PythonGame's callbackFlow
    Note over R: its collector folds the event:<br/>state = state.after(event)
    R-->>VM: StateFlow‹GameState›
    VM-->>S: StateFlow‹SudokuUiState›
    Note over S: recomposes, showing the 5
```

The intent and the result travel separate paths: `act()` returns as soon as the action is queued, and the 5
comes back later as events (unidirectional data flow). The UI thread never waits on Python.

### Leaving the app, and coming back after process death

```mermaid
sequenceDiagram
    autonumber
    participant E as Game entry<br/>(UI thread)
    participant VM as SudokuViewModel
    participant R as GameRepository<br/>(app-long scope)
    participant UI as AndroidUI<br/>(game thread)
    participant A as AutoSave<br/>(game thread)
    participant F as autosave.json

    Note over E: the player presses Home (or Back, or switches apps)
    E->>VM: ON_STOP: onStopped()
    VM->>R: save(): returns at once
    R->>UI: scope.launch(in order) { save() }: queued
    UI->>A: save(puzzle), after the actions before it
    A->>F: SaveFile.write(puzzle.saved_state())
    Note over E,F: Android ends the stopped app's process, calling nothing
    Note over E: the player reopens the app: Nav 3 restores Route.Game(layout)
    E->>R: a new game, through the container
    R->>UI: collects events: play(puzzle) on the game thread
    UI->>A: restore(puzzle)
    A->>F: SaveFile.read()
    A->>UI: puzzle.restore(saved): the board comes back as it was
```

A fresh start of the app goes through the splash instead, which reads the saved game's layout and opens
`Route.Game` on it; from there the game restores itself the same way.

### When the game fails

For example, after process death the back stack reopens `Route.Game(layout)`, but that layout has since been
removed from `game/puzzles/`, or broken. Any other error that reaches `PythonGame`, while starting or later, goes
the same way.

```mermaid
sequenceDiagram
    autonumber
    participant S as SudokuScreen<br/>(UI thread)
    participant C as AppContainer
    participant R as GameRepository<br/>(app-long scope)
    participant PG as PythonGame<br/>(game thread)

    C->>R: made by gameRepository(layout)
    R->>PG: collects events: starts the game thread
    PG->>PG: Catalog.board(layout) raises
    PG-->>R: GameEvent.Failed(reason), then the flow ends
    Note over R: state = state.after(Failed): failure = reason
    R-->>S: StateFlow, through the ViewModel
    Note over S: shows "The game stopped: reason"<br/>in place of "Starting the game…" (or of the board)
    Note over S: the player leaves with Back
    Note over C: on reopening, gameRepository(layout) sees<br/>state.hasEnded, and makes a new game that tries again
```

The cases, side by side:

| What happens | `GameState` | What the player sees |
|---|---|---|
| Python is still starting | `size` null, `failure` null | "Starting the game…" |
| An action fails (`AndroidUI` catches it, as the terminal does) | `message`, a warning | The board, with the warning in the status line; play goes on |
| The auto-save can't be restored (damaged, from a newer version, or on another layout) | `message`, a warning | A new board, with the warning in the status line; the file is kept until the player has something to save |
| Anything else fails, while starting or later (`PythonGame` catches it) | `failure` set | "The game stopped: …" in place of the board; Back leaves; reopening tries again |
| The player quits | `isOver` | The app closes, and the auto-save is deleted; reopening starts a new game |
