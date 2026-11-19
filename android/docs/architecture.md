# The Android app's architecture

How the app's code maps onto MVVM and Modern Android App Architecture, and how the parts talk to each other.
Updated at the start of each phase and as it goes; this is **MVP 1, phase 4** (Navigation 3), while it is being
built; the marks below show what isn't written yet.

Phase 4 is built in three steps: 4a (done) lists the layouts through the Python `Catalog` and starts each game on a
layout named; 4b brings Navigation 3, with the splash choosing what follows it and the layout picker; 4c reports a
game that can't start (`GameEvent.Failed`).

The app is drawn as an overview, then one section per feature (a screen with its ViewModel and data), each
through the same layers. Features share only the app's container and the activity that hosts their screens.

Colors: green is new in phase 4, amber is changed in phase 4, uncolored is unchanged. The colors cover the whole
phase, through all its steps, so 4a's parts stay colored.

Marks: * is planned for the step being built (today 4b) but not written yet; *(4c) is planned for a later step of
the phase.

Arrows: solid arrows are calls; dotted arrows are data flowing back, or a class implementing an interface.

## Overview

```mermaid
flowchart TB
    subgraph App["App · dependency injection by hand"]
        direction LR
        SudokuApplication --> AppContainer["AppContainer"]
    end

    subgraph Host["View · the activity that hosts the screens"]
        direction LR
        MainActivity --> NavDisplay["NavDisplay · back stack of Routes"]
    end

    subgraph Splash["Splash feature: Route.Splash"]
        SplashFeature["SplashScreen · SplashViewModel · CopyrightRepository"]
    end

    subgraph Layouts["Layouts feature: Route.LayoutPicker"]
        LayoutsFeature["LayoutPickerScreen · LayoutPickerViewModel · LayoutRepository"]
    end

    subgraph Game["Game feature: Route.Game(layout)"]
        GameFeature["SudokuScreen · SudokuViewModel · GameRepository"]
    end

    NavDisplay -- "first" --> SplashFeature
    SplashFeature -- "one layout, which can be picked: replaced by" --> GameFeature
    SplashFeature -- "otherwise: replaced by" --> LayoutsFeature
    LayoutsFeature -- "a pick: replaced by" --> GameFeature
    AppContainer -- "copyrightRepository, layoutRepository" --> SplashFeature
    AppContainer -- "layoutRepository" --> LayoutsFeature
    AppContainer -- "gameRepository(layout)" --> GameFeature

    classDef new fill:#2e7d32,stroke:#a5d6a7,stroke-width:2px,color:#ffffff
    classDef changed fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff
    class NavDisplay,LayoutsFeature new
    class SudokuApplication,AppContainer,MainActivity,SplashFeature,GameFeature changed
```

| Class | What it does |
|---|---|
| `SudokuApplication` | Made by Android once per process, before any screen (the manifest names it); makes the one `AppContainer`, giving it `newGame` (a `PythonGame` on the layout named), `newLayoutRepository` and `newCopyrightRepository` |
| `AppContainer` | The app's dependencies (`DefaultAppContainer`): the app-long scope; `gameRepository(layout)`, the game in play, made when first asked for and anew for another layout or once the game is over; and the `LayoutRepository` and `CopyrightRepository`, each made when first asked for |
| `MainActivity` | Its composable `SudokuApp` holds the back stack (`rememberNavBackStack(Route.Splash)`, kept through rotation and process death) and shows it with `NavDisplay`; `rememberViewModelStoreNavEntryDecorator()` gives each entry its own ViewModels, which live as long as its route is on the stack. Each entry is a small composable (`Splash`, `LayoutPicker`, `Game`) that gets its ViewModel and shows its screen. `SudokuApp` does the navigating (`replaceLast`): it replaces the splash with the splash's `next` route once there is one, and the picker with `Route.Game(layout)` when the player picks one; the game's entry closes the app once the game is over |
| `Route` | `ui/Keys.kt`: Navigation 3's keys, one per screen, in a sealed interface (so `Route.Game` doesn't clash with the `Game` interface): `Route.Splash`, `Route.LayoutPicker` and `Route.Game(layout)`, each a `@Serializable` `NavKey`. Each step replaces the route before it, so Back from the picker or the game leaves the app. After process death the stack comes back as it was, so the app reopens on `Route.Game(layout)` without the splash |

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
    end

    subgraph DataSource["Model · data source"]
        Assets["app assets: copyright.txt"]
    end

    SplashScreen -- "onTap" --> SplashViewModel
    SplashViewModel -. "StateFlow‹SplashUiState›" .-> SplashScreen
    SplashViewModel -- "notice()" --> CopyrightRepository
    SplashViewModel -- "layouts(), see the layouts feature" --> LayoutRepository["LayoutRepository"]
    AssetCopyrightRepository -- "reads, on Dispatchers.IO" --> Assets

    classDef changed fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff
    class SplashViewModel,SplashUiState changed
```

The notice's one copy is the repository's `ui/copyright.txt`: the build packages it as an asset
(`syncSharedAssets`), and the terminal reads it too.

| Layer | Class | What it does |
|---|---|---|
| View | `SplashScreen` | Stateless: the title at the top, the notice centred in the space below (a `Column` with a weighted `Box`); the whole screen reports a tap with `onTap` |
| ViewModel | `SplashViewModel` | Reads the notice from the `CopyrightRepository` and starts a 5-second timer, both in `viewModelScope`; `onTap()` ends the splash at once; its state lives in a `MutableStateFlow`; its `Factory` gets the repositories from the app's container. It also reads the layouts (which starts Python behind the splash), and once the splash has ended and the layouts are known, gives the route that replaces it: `Route.Game(layout)` when there is exactly one layout and it can be picked, as the terminal plays it, otherwise `Route.LayoutPicker` |
| ViewModel | `SplashUiState` | The notice (empty until read), and `next`, the route that replaces the splash, null until the splash has ended and the layouts are known |
| Data layer | `CopyrightRepository` | The interface: the one way to the GNU GPL notice, `suspend fun notice(): String` |
| Data layer | `AssetCopyrightRepository` | The real one: reads `copyright.txt` from the app's assets on `Dispatchers.IO`, and reflows it (`String.reflow()`): the file breaks its lines for the terminal, so each paragraph's lines are joined, for the screen to wrap to its own width |
| Data layer | `FakeCopyrightRepository` | A true fake for tests: returns the text it was given |
| Data source | app assets | `copyright.txt`, packaged from the repository's `ui/copyright.txt` by the build |

### From start through splash to game

```mermaid
sequenceDiagram
    autonumber
    participant M as MainActivity<br/>(UI thread)
    participant S as SplashScreen<br/>(UI thread)
    participant VM as SplashViewModel<br/>(viewModelScope)
    participant R as CopyrightRepository<br/>(IO pool)

    participant L as LayoutRepository<br/>(IO pool)

    M->>VM: made, through its Factory
    VM->>R: launch { notice() }
    VM->>L: launch { layouts() }: starts Python
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
    VM-->>M: StateFlow‹SplashUiState›: the next key, once ended and the layouts known
    Note over M: replaces Splash on the back stack with<br/>Game(layout) or LayoutPicker
```

Python starts behind the splash: reading the layouts starts it, and its slow first start overlaps the 5 seconds.
If the splash is tapped before the layouts are known, it waits for them. The splash's ViewModel lives only while
`Splash` is on the back stack, so its timer ends with it.

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

    classDef new fill:#2e7d32,stroke:#a5d6a7,stroke-width:2px,color:#ffffff
    classDef changed fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff
    class SudokuApp changed
    class LayoutPickerScreen,LayoutPickerViewModel,LayoutPickerUiState,LayoutRepository,Layout new
    class FakeLayoutRepository,PythonLayoutRepository,AppPython,Catalog new
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
| Data source | `AppPython` | Starts the app's one Python on first use, synchronized, for both the layouts and the game; slow the first time after an install |
| Python | `Catalog` | `ui/android/catalog.py`: lists the layouts in plain values, and makes the board of the one named; it plays the part `Main` plays for the terminal |
| Python | `PuzzleCatalog` | The game's catalog (`game/`): finds the layouts in `game/puzzles/` |

## The game feature

```mermaid
flowchart TB
    subgraph View["View · Compose · UI thread"]
        SudokuScreen["SudokuScreen *(4c)"]
    end

    subgraph VM["ViewModel"]
        direction LR
        SudokuViewModel --- SudokuUiState
    end

    subgraph DataLayer["Model · data layer · data/"]
        direction LR
        GameRepository --- GameState["GameState *(4c)"]
    end

    subgraph DataSource["Model · data source · game/"]
        direction LR
        PythonGame["PythonGame *(4c)"] -. implements .-> Game["«interface» Game"]
        FakeGame["FakeGame (tests)"] -. implements .-> Game
        PythonScreen
    end

    subgraph Python["Python · game thread"]
        direction LR
        AndroidUI --> Puzzle["Puzzle, Board, Cell"]
    end

    SudokuScreen -- "intents" --> SudokuViewModel
    SudokuViewModel -. "StateFlow‹SudokuUiState›" .-> SudokuScreen
    SudokuViewModel -- "act(), answer()" --> GameRepository
    GameRepository -. "StateFlow‹GameState›" .-> SudokuViewModel
    GameRepository -- "act(), answer()" --> Game
    Game -. "Flow‹GameEvent›" .-> GameRepository
    PythonGame -- "Chaquopy" --> AndroidUI
    AndroidUI -. "showCell(), askConfirm() …" .-> PythonScreen
    PythonScreen -. "GameEvent" .-> PythonGame
    PythonGame -- "Catalog.board(layout), see the layouts feature" --> AndroidUI

    classDef changed fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff
    class SudokuViewModel,PythonGame,SudokuScreen,GameState changed
```

Everything from `GameRepository` down is MVVM's **Model**, which Google's guide splits into the data layer and
its data sources. The Python game is at the bottom, as the source of truth for the puzzle.

| Layer | Class | What it does |
|---|---|---|
| View | `SudokuScreen` | Stateless composables: draws the state, and passes taps on as intents (`SudokuIntents`); *(4c) shows why the game couldn't start, in place of "Starting the game…", when it failed |
| ViewModel | `SudokuViewModel` | `uiState = repository.state.map { SudokuUiState(it) }.stateIn(viewModelScope, WhileSubscribed(5 s))`; each intent is `viewModelScope.launch { repository.act(...) }`; `factory(layout)` gets the game on that layout from the app's container |
| ViewModel | `SudokuUiState` | The game's state, plus what the screen works out from it (the mode switch) |
| Data layer | `GameRepository` | The one way to the game, in an app-long scope: `state = events.runningFold(GameState()) { s, e -> s.after(e) }.stateIn(scope, Eagerly)`; `act()` and `answer()` run on `Dispatchers.IO`, one at a time, so they keep their order |
| Data layer | `GameState` | Only what the game reported; `after(event)` works out each event's effect; *(4c) including `GameEvent.Failed`, the reason the game couldn't start |
| Data source | `Game` | The interface: `events: Flow<GameEvent>`, `act()`, `answer()` |
| Data source | `PythonGame` | The real game, on the layout named: `events = callbackFlow { ... }` starts the game thread, on the board from `Catalog.board(layout)` (with Python started by `AppPython`), and ends when the game is over; `act()` calls `AndroidUI.act()` through Chaquopy. *(4c) Setting up and playing are caught separately: a setup failure reports `GameEvent.Failed`, so the app never waits on a game that can't start; a failure in play stays a status warning |
| Data source | `PythonScreen` | What Python calls (`showCell()`, `askConfirm()`, `questionAnswered()`, ...), turned into `GameEvent`s |
| Data source | `FakeGame` | A stand-in for tests: reports the events it is given, records the actions |
| Python | `AndroidUI` | The port's adapter (`ui/android/`): `act()` → actions queue → `play()` → `puzzle.handle()`; `confirm()` waits for `answer()` |
| Python | `Puzzle`, `Board`, `Cell`, ... | The game itself (`game/`): the single source of truth for the puzzle |

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
