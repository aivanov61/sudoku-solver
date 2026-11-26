// -----------------------------------------------------------------------------
// Copyright (c) by Anton Ivanov.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.
// -----------------------------------------------------------------------------

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)  // Navigation 3's keys are @Serializable, to save the back stack
    alias(libs.plugins.chaquopy)
}

android {
    namespace = "io.github.aivanov61.sudoku"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "io.github.aivanov61.sudoku"
        minSdk = 24
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        // Runs the instrumented tests (app/src/androidTest) on the device: the Compose UI tests of the screens
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        ndk {
            // Chaquopy ships Python for these ABIs: real phones, and the emulator on a PC
            abiFilters += listOf("arm64-v8a", "x86_64")
        }
    }

    buildTypes {
        debug {
            // Measure what the unit tests cover, with JaCoCo: gradle :app:createDebugUnitTestCoverageReport writes
            // the report to app/build/reports/coverage/test/debug/index.html
            enableUnitTestCoverage = true
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    buildFeatures {
        compose = true
    }
}

// The app's Python is the repository's own (two levels up), copied in without its tests, so the app always
// plays the same code the terminal does: the game/ package, and of ui/ only what the Android user interface uses.
val appPython = layout.buildDirectory.dir("app-python")
val syncAppPython = tasks.register<Sync>("syncAppPython") {
    into(appPython)
    exclude("**/tests/**", "**/__pycache__/**")
    from(rootDir.resolve("../game")) {
        into("game")
    }
    from(rootDir.resolve("../ui")) {
        into("ui")
        include("__init__.py", "error_log.py", "android/**")
    }
}
tasks.matching { it.name.startsWith("merge") && it.name.endsWith("PythonSources") }.configureEach {
    dependsOn(syncAppPython)
}

// The repository's files the app shows as they are, packaged as assets (read with context.assets), so there is one
// copy of each: the GNU GPL notice (ui/copyright.txt), which the terminal shows as its splash too.
abstract class SyncSharedAssets : DefaultTask() {
    @get:InputFiles
    abstract val sources: ConfigurableFileCollection

    @get:OutputDirectory
    abstract val outputDir: DirectoryProperty

    @TaskAction
    fun sync() {
        val target = outputDir.get().asFile
        target.deleteRecursively()
        target.mkdirs()
        sources.forEach { it.copyTo(target.resolve(it.name)) }
    }
}
val syncSharedAssets = tasks.register<SyncSharedAssets>("syncSharedAssets") {
    sources.from(rootDir.resolve("../ui/copyright.txt"))
}
androidComponents {
    onVariants { variant ->
        // The Variant API: the task's output is an assets folder, so every step that needs the assets runs it first
        variant.sources.assets?.addGeneratedSourceDirectory(syncSharedAssets, SyncSharedAssets::outputDir)
    }
}

chaquopy {
    defaultConfig {
        version = "3.15"  // the game needs 3.14 or later; matching the PC's Python lets the build compile it
    }
    sourceSets {
        getByName("main") {
            srcDir(appPython)
        }
    }
}

dependencies {
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.lifecycle.viewmodel.navigation3)
    implementation(libs.androidx.navigation3.runtime)
    implementation(libs.androidx.navigation3.ui)
    debugImplementation(libs.androidx.compose.ui.tooling)
    debugImplementation(libs.androidx.compose.ui.test.manifest)  // the empty activity createComposeRule() shows a screen in
    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.test)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.compose.ui.test.junit4)
    androidTestImplementation(libs.androidx.test.runner)
    // Newer than the Espresso ui-test-junit4 brings, whose way of sending taps Android 17 no longer has
    androidTestImplementation(libs.androidx.test.espresso.core)
}
