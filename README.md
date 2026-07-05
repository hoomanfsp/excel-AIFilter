# Excel AI Filterer

A fast, modern Windows Desktop application built with Python and CustomTkinter. It leverages the official OpenAI API to intelligently filter massive Excel datasets based on any topic or prompt you provide.

## Features
- **Intelligent Filtering**: Use cutting-edge AI (gpt-4o or gpt-4o-mini) to evaluate rows conceptually rather than just looking for exact keyword matches.
- **Dynamic Context**: Select whichever columns you want from your Excel sheet to form the "context" for the AI to evaluate.
- **Modern UI**: A sleek, dark-mode-first interface that remains fully responsive while processing in the background.
- **Batch Processing**: Automatically groups rows into batches of 25 to minimize API requests and maximize speed.
- **Auto-Retries**: Built-in exponential backoff means if an API request drops, the app smoothly handles it and retries without crashing.

## Usage
1. Open the application.
2. Enter your **OpenAI API Key** (e.g. `sk-proj-...`). The key is only kept in memory while the app runs and is never stored on disk.
3. Select your desired OpenAI model (`gpt-4o-mini` is extremely fast and cheap for this task).
4. Enter your topic (e.g., "Computer Science").
5. Load your `.xlsx` Excel file.
6. Check the columns you want the AI to read.
7. Click **Start Filtering** and choose where to save the output file!

## Installation from Source
If you want to run the python source code directly:
```bash
pip install -r requirements.txt
python app.py
```

## Download the Executable
Check out the [Releases](https://github.com/hoomanfsp/excel-AIFilter/releases) page to download a pre-compiled `.exe` file for Windows. You do not need to install Python to run the `.exe`.
