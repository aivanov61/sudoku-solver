# The Android app's architecture

How the app's code maps onto MVVM and Modern Android App Architecture, and how the parts talk to each other.
Updated at the end of each phase; this is the state after **MVP 1, phase 1** (the data layer).

Colors: green is new in phase 1, amber is changed in phase 1, uncolored is unchanged.

Arrows: solid arrows are calls; dotted arrows are data flowing back, or a class implementing an interface.

## The layers

```mermaid
flowchart TB
    subgraph View["View · Compose · UI thread"]
        direction LR
        MainActivity --> SudokuScreen
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

    classDef new fill:#2e7d32,stroke:#a5d6a7,stroke-width:2px,color:#ffffff
    classDef changed fill:#b45309,stroke:#fcd34d,stroke-width:2px,color:#ffffff
    class GameRepository,GameState,FakeGame new
    class MainActivity,SudokuScreen,SudokuViewModel,SudokuUiState,Game,PythonGame,PythonScreen,AndroidUI changed
```

Everything from `GameRepository` down is MVVM's **Model**, which Google's guide splits into the data layer and
its data sources. The Python game is at the bottom, as the source of truth for the puzzle.

| Layer | Class | What it does |
|---|---|---|
| View | `MainActivity` | Makes the ViewModel, collects its `uiState` with `collectAsStateWithLifecycle()`, and shows `SudokuScreen`; closes once the game is over |
| View | `SudokuScreen` | Stateless composables: draws the state, and passes taps on as intents (`SudokuIntents`) |
| ViewModel | `SudokuViewModel` | `uiState = repository.state.map { SudokuUiState(it) }.stateIn(viewModelScope, WhileSubscribed(5 s))`; each intent is `viewModelScope.launch { repository.act(...) }` |
| ViewModel | `SudokuUiState` | The game's state, plus what the screen works out from it (the mode switch) |
| Data layer | `GameRepository` | The one way to the game, in an app-long scope: `state = events.runningFold(GameState()) { s, e -> s.after(e) }.stateIn(scope, Eagerly)`; `act()` and `answer()` run on `Dispatchers.IO` |
| Data layer | `GameState` | Only what the game reported; `after(event)` works out each event's effect |
| Data source | `Game` | The interface: `events: Flow<GameEvent>`, `act()`, `answer()` |
| Data source | `PythonGame` | The real game: `events = callbackFlow { ... }` starts the game thread; `act()` calls `AndroidUI.act()` through Chaquopy |
| Data source | `PythonScreen` | What Python calls (`showCell()`, `askConfirm()`, `questionAnswered()`, ...), turned into `GameEvent`s |
| Data source | `FakeGame` | A stand-in for tests: reports the events it is given, records the actions |
| Python | `AndroidUI` | The port's adapter (`ui/android/`): `act()` → actions queue → `play()` → `puzzle.handle()`; `confirm()` waits for `answer()` |
| Python | `Puzzle`, `Board`, `Cell`, ... | The game itself (`game/`): the single source of truth for the puzzle |

## One tap, end to end: entering 5 in the selected cell

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
