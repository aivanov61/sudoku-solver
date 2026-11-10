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

        ndk {
            // Chaquopy ships Python for these ABIs: real phones, and the emulator on a PC
            abiFilters += listOf("arm64-v8a", "x86_64")
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
    debugImplementation(libs.androidx.compose.ui.tooling)
    testImplementation(libs.junit)
}
