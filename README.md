# Ticket Revenue Calculator

A desktop application using Python and `customtkinter` to calculate maximum ticket revenue with different algorithms.

## Features

*   Input up to 9 ticket prices and the desired number of tickets.
*   View detailed results: max revenue, algorithm details (complexity, time, steps).
*   Visualize results: Price distribution (pie) and revenue analysis (bar) charts.
*   Manage history: View past calculations, export to Excel, clear records.
*   Customize settings: Appearance (Light/Dark/System), toggle sound feedback.
*   Save results, history, and settings using an SQLite database.

## Multiple Calculation Algorithms
    *   Brute Force
    *   Dynamic Programming
    *   Optimized Greedy

## Project Structure

```
ticket-revenue-calculator/
├── app/              # Core application package
│   └── gui/         # GUI components and views
│       └── results_tab.py  # Results tab implementation
├── main.py          # Application entry point
├── algorithms.py    # Revenue calculation algorithm implementations
├── models.py        # Data structures (Placeholder)
├── utils.py         # Helper classes (Database, SoundManager)
├── requirements.txt # Python package dependencies
├── ticket_revenue.db# SQLite database file
└── README.md        # This file
```

## Setup & Run

1.  **Prerequisites:** Python 3.8+
2.  **Clone:**
    ```bash
    git clone https://github.com/Mohmedahmed888/ticket-revenue-calculator.git
    cd ticket-revenue-calculator
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run:**
    ```bash
    python main.py
    ```

## How to Use (GUI)

1.  **Input:** Enter prices and ticket count in the `Calculator` tab, select an algorithm.
2.  **Calculate:** Click the "Calculate Maximum Revenue ▶" button.
3.  **View Results:** See details in the `Results` tab. Click "Save Results" to store.
4.  **Explore History:** Check past results in `History`. Refresh, Export, or Clear as needed.
5.  **Analyze:** View charts for the last calculation in `Analytics`. Refresh or Save the chart.
6.  **Configure:** Adjust appearance and sound in `Settings`.

## Development

Extend the application by adding algorithms to `algorithms.py`, enhancing GUI components in `views.py`, or defining data structures in `models.py`.

## Requirements

*   Python 3.8+
*   customtkinter >= 5.2.0
*   matplotlib >= 3.7.1
*   pandas >= 2.0.0
*   numpy >= 1.24.0

## License

© 2025 Egyptian Chinese University – All rights reserved.