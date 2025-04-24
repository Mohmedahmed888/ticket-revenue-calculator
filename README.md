# Ticket Revenue Calculator

A desktop application built with Python and `customtkinter` to calculate the maximum possible revenue from selling event tickets using various algorithms.

## Features

*   **Input Flexibility:** Enter up to 9 potential ticket prices and the number of tickets to sell.
*   **Multiple Scheduling Algorithms:**
    *   Brute Force (with memoization)
    *   Dynamic Programming
    *   Optimized Greedy
*   **Detailed Results Display:** Shows maximum revenue, algorithm details (complexity, time), and step-by-step description.
*   **Calculation History:** View past results in a table format.
*   **Export History:** Export calculation history to Excel.
*   **Clear History:** Option to delete all saved history records.
*   **Analytics:** Visualize revenue analysis and price distribution (based on the last calculation).
*   **Save Charts:** Save the generated analytics charts as images.
*   **Settings:** Customize appearance (Light/Dark/System) and toggle sound feedback.
*   **Persistent Settings:** Saves user preferences (appearance, sound) in a database.
*   **Database Integration:** Uses SQLite to store history and settings.

## Project Structure

```
ticket-revenue-calculator/
├── main.py           # Application entry point
├── views.py          # GUI components (Main Window, Tabs)
├── algorithms.py     # Revenue calculation algorithm implementations
├── models.py         # Data structures (Currently empty - placeholder)
├── utils.py          # Helper functions & classes (Database, SoundManager)
├── requirements.txt  # Python package dependencies
├── ticket_revenue.db # SQLite database file (created on first run)
└── README.md         # This file
```

## Component Descriptions

*   **`main.py`**: Entry point for the application. Initializes the main window (`TicketRevenueApp` from `views.py`) and starts the Tkinter main loop.
*   **`views.py`**: Contains all GUI components built using `customtkinter`.
    *   `TicketRevenueApp`: The main application window class, managing tabs and overall application state.
    *   `CalculatorTab`: Frame/Class for handling price/ticket inputs and algorithm selection.
    *   `ResultsTab`: Frame/Class for displaying detailed calculation results.
    *   `AnalyticsTab`: Frame/Class for displaying revenue/price analysis charts using Matplotlib.
    *   `HistoryTab`: Frame/Class for displaying past calculation results from the database.
    *   `SettingsTab`: Frame/Class for managing application settings (appearance, sound).
*   **`algorithms.py`**: Contains implementations of all revenue calculation algorithms (`brute_force_max_revenue`, `dynamic_programming_max_revenue`, `optimized_greedy_max_revenue`).
*   **`models.py`**: Placeholder for defining data structures. Currently not used but kept for potential future expansion.
*   **`utils.py`**: Contains helper classes and functions.
    *   `Database`: Manages all interactions with the SQLite database (saving/loading history and settings).
    *   `SoundManager`: Handles playing sound effects based on application events and settings.

## How to Use

**1. Setup:**

*   Ensure Python 3.8+ is installed.
*   Clone the repository:
    ```bash
    git clone https://github.com/Mohmedahmed888/ticket-revenue-calculator.git
    cd ticket-revenue-calculator
    ```
*   Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

**2. Running the Application:**

*   Navigate to the project directory in your terminal.
*   Run the command:
    ```bash
    python main.py
    ```

**3. Using the GUI:**

*   **Calculator Tab:** Enter ticket prices, number of tickets, and select an algorithm.
*   **Calculate:** Click the "Calculate Maximum Revenue ▶" button.
*   **Results Tab:** View the calculated maximum revenue, algorithm details (complexity, time, steps). Click "Save Results" to store the calculation.
*   **History Tab:** View previously saved calculations. Use "Refresh" to reload, "Export Excel" to save as `.xlsx`, or "Clear History" to delete all records.
*   **Analytics Tab:** View charts analyzing the *last calculated result* (price distribution and revenue analysis). Use "Refresh Plot" if needed, and "Save Chart" to save as an image.
*   **Settings Tab:** Change the appearance mode (Light/Dark/System) and enable/disable sound effects.

## Development

To extend the application:

*   Add new calculation algorithms to `algorithms.py`.
*   Enhance existing GUI components or add new ones in `views.py`.
*   Update the main application class (`TicketRevenueApp` in `views.py`) to integrate new features.
*   Define data models in `models.py` if complex data handling is needed.

## Requirements

*   Python 3.8+
*   customtkinter >= 5.2.0
*   matplotlib >= 3.7.1
*   pandas >= 2.0.0
*   numpy >= 1.24.0

## License

© 2025 Egyptian Chinese University – All rights reserved.