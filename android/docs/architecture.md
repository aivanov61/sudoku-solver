# The Android app's architecture

How the app's code maps onto MVVM and Modern Android App Architecture, and how the parts talk to each other.
Updated at the end of each phase; this is the state after **MVP 1, phase 3** (the splash screen).

The app is drawn as an overview, then one section per feature (a screen with its ViewModel and data), each
through the same layers. Features share only the app's container and the activity that hosts their screens.

Colors: green is new in phase 3, amber is changed in phase 3, uncolored is unchanged.

Arrows: solid arrows are calls; dotted arrows are data flowing back, or a class implementing an interface.

## Overview

```mermaid
flowchart TB
    subgraph App["App · dependency injection by hand"]
        direction LR
        SudokuApplication --> AppContainer["AppContainer"]
    end

    subgraph Host["View · the activity that hosts the screens"]
        MainActivity
    end

    subgraph Splash["Splash feature"]
        SplashFeature["SplashScreen · SplashViewModel · CopyrightRepository"]
    end

    subgraph Game["Game feature"]
        GameFeature["SudokuScreen · SudokuViewModel · GameRepository"]
    end

    MainActivity -- "shows until it has ended" --> SplashFeature
    MainActivity -- "then shows" --> GameFeature
    AppContainer -- "copyrightRepository" --> SplashFeature
    AppContainer -- "gameRepository" --> GameFeature

    classDef new fill:#2e7d32,stroke:#a5d6a7,stroke-width:2px,color:#ffffff
    classDef changed fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff
    class SplashFeature new
    class SudokuApplication,AppContainer,MainActivity changed
```

| Class | What it does |
|---|---|
| `SudokuApplication` | Made by Android once per process, before any screen (the manifest names it); makes the one `AppContainer`, giving it `newGame` and `newCopyrightRepository` |
| `AppContainer` | The app's dependencies (`DefaultAppContainer`): the app-long scope; the `GameRepository` of the game in play, made when first asked for and anew once the game is over; and the `CopyrightRepository`, made when first asked for |
| `MainActivity` | Makes the features' ViewModels, through their factories, and collects their state with `collectAsStateWithLifecycle()`, in its composable `SudokuApp`; shows the splash until it has ended, then the game; closes once the game is over. It makes the game's ViewModel at once, not after the splash, so the game, and Python's slow first start, get going behind the splash |

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
    AssetCopyrightRepository -- "reads, on Dispatchers.IO" --> Assets

    classDef new fill:#2e7d32,stroke:#a5d6a7,stroke-width:2px,color:#ffffff
    class SplashScreen,SplashViewModel,SplashUiState,CopyrightRepository,AssetCopyrightRepository new
    class FakeCopyrightRepository,Assets new
```

The notice's one copy is the repository's `ui/copyright.txt`: the build packages it as an asset
(`syncSharedAssets`), and the terminal reads it too.

| Layer | Class | What it does |
|---|---|---|
| View | `SplashScreen` | Stateless: the title at the top, the notice centred in the space below (a `Column` with a weighted `Box`); the whole screen reports a tap with `onTap` |
| ViewModel | `SplashViewModel` | Reads the notice from the `CopyrightRepository` and starts a 5-second timer, both in `viewModelScope`; `onTap()` ends the splash at once; its state lives in a `MutableStateFlow`; its `Factory` gets the repository from the app's container |
| ViewModel | `SplashUiState` | The notice (empty until read), and whether the splash has ended (`hasEnded`) |
| Data layer | `CopyrightRepository` | The interface: the one way to the GNU GPL notice, `suspend fun notice(): String` |
| Data layer | `AssetCopyrightRepository` | The real one: reads `copyright.txt` from the app's assets on `Dispatchers.IO`, turning Windows line endings into `\n` |
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

    M->>VM: made, through its Factory
    Note over M: makes SudokuViewModel too, so the game<br/>starts behind the splash
    VM->>R: launch { notice() }
    VM->>VM: launch { delay(5 s) }
    R-->>VM: the notice's text
    VM-->>S: StateFlow‹SplashUiState›: the notice
    Note over S: shows the title and the notice
    alt the player taps
        S->>VM: onTap()
    else 5 seconds pass
        Note over VM: the delay ends
    end
    VM-->>M: StateFlow‹SplashUiState›: hasEnded
    Note over M: shows SudokuScreen in place of SplashScreen
```

The Python game starts behind the splash: `SudokuApp` makes the game's ViewModel along with the splash's, which
asks the container for the game's repository and so starts Python, and its slow first start overlaps the 5
seconds.

## The game feature

```mermaid
flowchart TB
    subgraph View["View · Compose · UI thread"]
        SudokuScreen
    end

    subgraph VM["ViewModel"]
        direction LR
        SudokuViewModel --- SudokuUiState
    end

    subgraph DataLayer["Model · data layer · data/"]
        direction LR
        GameRepository --- GameState
    end

    subgraph DataSource["Model · data source · game/"]
        direction LR
        PythonGame -. implements .-> Game["«interface» Game"]
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
```

Everything from `GameRepository` down is MVVM's **Model**, which Google's guide splits into the data layer and
its data sources. The Python game is at the bottom, as the source of truth for the puzzle.

| Layer | Class | What it does |
|---|---|---|
| View | `SudokuScreen` | Stateless composables: draws the state, and passes taps on as intents (`SudokuIntents`) |
| ViewModel | `SudokuViewModel` | `uiState = repository.state.map { SudokuUiState(it) }.stateIn(viewModelScope, WhileSubscribed(5 s))`; each intent is `viewModelScope.launch { repository.act(...) }`; its `Factory` gets the repository from the app's container |
| ViewModel | `SudokuUiState` | The game's state, plus what the screen works out from it (the mode switch) |
| Data layer | `GameRepository` | The one way to the game, in an app-long scope: `state = events.runningFold(GameState()) { s, e -> s.after(e) }.stateIn(scope, Eagerly)`; `act()` and `answer()` run on `Dispatchers.IO`, one at a time, so they keep their order |
| Data layer | `GameState` | Only what the game reported; `after(event)` works out each event's effect |
| Data source | `Game` | The interface: `events: Flow<GameEvent>`, `act()`, `answer()` |
| Data source | `PythonGame` | The real game: `events = callbackFlow { ... }` starts the game thread, and ends when the game is over; `act()` calls `AndroidUI.act()` through Chaquopy |
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
