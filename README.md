# Wikipedia Event Stream Monitor

A real-time monitoring tool that connects to the Wikipedia Event Stream API and generates periodic reports about Wikipedia activity.

## Features

- Monitors the Wikipedia revision-create event stream in real-time
- Generates periodic reports on:
  - Wikipedia domains with updated pages
  - Users who made changes to English Wikipedia (en.wikipedia.org)
- Supports two monitoring modes:
  - Task 1: Reports based on 1-minute sliding windows
  - Task 2: Reports based on 5-minute sliding windows

## Requirements

- Python 3.6+
- `sseclient` package

## Installation


1. Set up a virtual environment (recommended):
   ```
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

2. Install the required dependency:
   ```
   pip install sseclient
   ```

## Usage

Run the script:
```
python main.py
```

### Controls

- **Press Ctrl+C once**: Switch from Task 1 (1-minute window) to Task 2 (5-minute window)
- **Press Ctrl+C twice**: Exit the application

## How It Works

1. **Data Collection**: Continuously collects events from the Wikipedia Event Stream API
2. **Sliding Window**: Maintains a sliding window of events (1 or 5 minutes) in memory
3. **Report Generation**: Every minute, generates reports based on the events in the current window

### Reports Generated

#### Domains Report
Shows Wikipedia domains that have been updated, with the count of unique pages updated. Domains are sorted by the number of pages updated in descending order.

#### Users Report
Shows non-bot users who have made changes to the English Wikipedia (en.wikipedia.org), sorted by their edit count in descending order.

## Error Handling

The script includes robust error handling for common issues:

- **JSON Parsing Errors**: The stream occasionally contains malformed JSON, which the script safely ignores
- **Connection Issues**: Automatically reconnects if the connection to the Wikipedia API is lost
- **Signal Handling**: Properly responds to keyboard interrupts for mode switching and exit

## Implementation Details

- Uses Python's threading to handle concurrent event collection and report generation
- Uses `collections.deque` for efficient sliding window implementation
- Implements signal handling for interactive mode switching
