# R8's rules for the release build, beyond Android's own (proguard-android-optimize.txt) and those the libraries
# bring, Chaquopy's among them: https://developer.android.com/topic/performance/app-optimization/enable-app-optimization

# Python calls the screen's methods by name, through Chaquopy, which R8 can't see: keep them, and their names
-keep class io.github.aivanov61.sudoku.game.PythonScreen {
    public <methods>;
}
