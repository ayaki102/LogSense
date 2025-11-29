# LogSense

A Python-based log file analyzer that parses log files and generates comprehensive reports in multiple formats (HTML, CSV, JSON, PDF).

## Features

- **Multi-format Log Parsing**: Automatically parses structured log files with timestamps, log levels, modules, and messages
- **Stacktrace Detection**: Captures and includes error stacktraces in the analysis
- **Comprehensive Statistics**: Provides detailed summaries including:
  - Total log entries by level (ERROR, WARNING, INFO)
  - Module activity breakdown
  - Top error types and occurrences
  - Time range analysis
- **Multiple Export Formats**: Generate reports in HTML, CSV, JSON, or PDF
- **Beautiful HTML Reports**: Professional-looking web reports with responsive design and color-coded sections
- **CLI Interface**: Simple command-line interface with helpful error messages

## Requirements

### Core Dependencies
```bash
pip install colorama
```

### Optional (for PDF export)
```bash
pip install reportlab
```

## Installation

1. Clone or download the script
2. Install required dependencies:
```bash
pip install colorama
```
3. For PDF support:
```bash
pip install reportlab
```

## Usage

### Basic Syntax
```bash
python logsense.py [FILENAME].log -e|--export [type]
```

### Examples

Generate an HTML report:
```bash
python logsense.py app.log --export html
```

Generate a CSV report:
```bash
python logsense.py app.log -e csv
```

Generate a JSON report:
```bash
python logsense.py app.log -e json
```

Generate a PDF report:
```bash
python logsense.py app.log -e pdf
```

### Help
```bash
python logsense.py --help
```

## Supported Log Format

LogSense expects log files in the following format:
```
YYYY-MM-DD HH:MM:SS,mmm LEVEL module - message
```

Example:
```
2024-01-15 10:30:45,123 ERROR Database - Connection failed
2024-01-15 10:30:46,456 WARNING Auth - Invalid token
2024-01-15 10:30:47,789 INFO Server - Request processed
```

### Stacktrace Support
The analyzer automatically captures multi-line stacktraces that follow error entries:
```
2024-01-15 10:30:45,123 ERROR Database - Connection failed
  File "app.py", line 42, in connect
    raise ConnectionError("Database unavailable")
ConnectionError: Database unavailable
```

## Output Formats

### HTML Report
- Visual dashboard with color-coded statistics
- Interactive tables with hover effects
- Formatted stacktraces
- Responsive design for mobile viewing
- Complete error and warning listings

### CSV Report
- Structured data export
- Summary statistics
- Level distribution
- Module activity
- Complete error and warning logs
- Easy to import into spreadsheet applications

### JSON Report
- Machine-readable format
- Complete analysis data structure
- All errors and warnings with metadata
- Perfect for programmatic processing

### PDF Report
- Professional document format
- Summary statistics table
- Top error types
- Formatted for printing
- Requires `reportlab` library

## Error Handling

The tool provides clear, color-coded error messages for:
- Missing or invalid file paths
- Unsupported file types
- Invalid export formats
- Missing dependencies (for PDF export)

## Output Files

Reports are automatically named based on the input file:
- Input: `app.log`
- Output: `app_report.[html|csv|json|pdf]`

## Features Breakdown

### Statistics Tracked
- **Total Entries**: Complete count of all log entries
- **Level Distribution**: Breakdown by ERROR, WARNING, INFO
- **Module Activity**: Which modules generate the most logs
- **Error Types**: Classification and frequency of error types
- **Warning Types**: Classification and frequency of warnings
- **Time Range**: Start and end timestamps of the log file

### Visual Enhancements
- Color-coded severity levels
- Clean, modern UI design
- Syntax-highlighted stacktraces
- Responsive grid layouts
- Professional typography

## License

This tool is provided as-is for log analysis purposes.

## Contributing

Feel free to extend the functionality by:
- Adding support for custom log formats
- Implementing additional export formats
- Adding data visualization charts
- Creating filtering options for specific time ranges or modules

## Troubleshooting

**Q: "reportlab is required for PDF export"**  
A: Install the reportlab library: `pip install reportlab`

**Q: "FILE NOT FOUND" error**  
A: Ensure the log file path is correct and the file exists

**Q: No entries parsed**  
A: Verify your log file matches the expected format with proper timestamps and log levels
