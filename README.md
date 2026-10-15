# BMS Plotter

A Python-based plotting tool for battery management system (BMS) data.

The project separates data sources, plotting components, and interfaces into dedicated modules to keep data acquisition and visualization organized.

## Project Structure

```text
BMS_Plotter/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── config/              # Configuration files
├── core/
│   ├── data_source/     # Data source components
│   ├── plotting/        # Plotting components
│   └── utils.py         # Shared utilities
├── interfaces/          # Interface components
├── assets/              # Project assets
└── example_sketches/     # Example sketches
```

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone [https://github.com/tobias-daiger/BMS_Plotter.git](https://github.com/tobias-daiger/BMS_Plotter.git)
cd BMS_Plotter
```

Create and activate a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running the Application

From the project directory, run:

```bash
python main.py
```

## Configuration and Examples

Configuration files are located in `config/`. The `example_sketches/`
directory contains example sketches.

Data source components and plotting logic are organized separately in
`core/data_source/` and `core/plotting/`.
