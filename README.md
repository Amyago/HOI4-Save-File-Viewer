# HOI4 Save File Viewer

![MIT License](https://img.shields.io/badge/License-MIT-green.svg)

A modern, fast, and user-friendly desktop application for viewing, searching, converting, and comparing Hearts of Iron 4 (`.hoi4`) save files. Built for modders, content creators, and gamers.

![App Screenshot](https://github.com/Amyago/HOI4-Save-File-Viewer/blob/main/preview.JPG)


---

## Features

-   📂 **Opens Any Save File:** Automatically parses both binary and plain-text `.hoi4` files.
-   🌳 **Interactive Tree View:** Displays the entire save file in a clean, expandable tree structure.
-   ⚡ **Instant Search:** A powerful, real-time search bar that filters the entire tree to find keys or values in seconds.
-   💾 **Converter Tool:** Save the loaded data as a human-readable plain-text file or a structured `.json` file for analysis.
-   ↔️ **Save File Comparison (Diff Tool):** Open a second file to see a color-coded view of what was added, removed, or modified between saves.
-   ✨ **Professional UI:** A clean, thematic dark mode and smart, user-friendly features like automatically finding your save folder.
-   🚀 **Fast & Responsive:** Built with multi-threading to ensure the UI never freezes, even on massive late-game saves.

## Installation

The application is distributed as a single `.exe` file with no installer needed.

1.  Go to the **[Releases Page](https://github.com/YourUsername/HOI4-Save-File-Viewer/releases)**.
2.  Download the latest `HOI4_Save_File_Viewer.exe` from the "Assets" section.
3.  Place the `.exe` anywhere on your computer and run it.

## Usage

1.  Launch the application.
2.  Use `File -> Open Default Save Folder...` to immediately jump to your HOI4 save games.
3.  Select a `.hoi4` file to load it.
4.  Browse the tree on the left, use the search bar on the right, and select items to see their details.
5.  To compare files, first open a base file, then use `File -> Compare With...` and select a second file.

## Acknowledgments

This application's powerful parsing capabilities are made possible by the **[hoi4.py](https://github.com/samirelanduk/hoi4.py)** library created by Sam Ireland. The GUI and application features were built on top of this excellent backend.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
