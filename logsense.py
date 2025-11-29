import sys
import re
import json
import csv
from collections import Counter
from colorama import Fore, init as colorama_init
import os

colorama_init(autoreset=True)


class LogEntry:
    def __init__(self, timestamp, level, module, message, stacktrace=None):
        self.timestamp = timestamp
        self.level = level
        self.module = module
        self.message = message
        self.stacktrace = stacktrace

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "module": self.module,
            "message": self.message,
            "stacktrace": self.stacktrace,
        }


class LogAnalyzer:
    def __init__(self, filename):
        self.filename = filename
        self.entries = []
        self.parse_logs()

    def parse_logs(self):
        """Parse log file and extract structured data"""
        with open(self.filename, "r") as file:
            lines = file.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            # Match standard log format: YYYY-MM-DD HH:MM:SS,mmm LEVEL module - message
            match = re.match(
                r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s+(\w+)\s+(\w+)\s+-\s+(.+)$",
                line,
            )

            if match:
                timestamp, level, module, message = match.groups()

                # Check for stacktrace on following lines
                stacktrace = []
                j = i + 1
                while j < len(lines) and not re.match(r"^\d{4}-\d{2}-\d{2}", lines[j]):
                    stacktrace.append(lines[j].strip())
                    j += 1

                entry = LogEntry(
                    timestamp=timestamp,
                    level=level,
                    module=module,
                    message=message,
                    stacktrace="\n".join(stacktrace) if stacktrace else None,
                )
                self.entries.append(entry)
                i = j
            else:
                i += 1

    def get_summary(self):
        """Generate comprehensive summary statistics"""
        level_counts = Counter(entry.level for entry in self.entries)
        module_counts = Counter(entry.module for entry in self.entries)

        # Get error details
        errors = [e for e in self.entries if e.level == "ERROR"]
        error_types = Counter(e.message.split(":")[0] for e in errors)

        # Get warning details
        warnings = [e for e in self.entries if e.level == "WARNING"]
        warning_types = Counter(
            e.message.split(":")[0] if ":" in e.message else e.message.split("-")[0]
            for e in warnings
        )

        # Time range
        if self.entries:
            first_entry = self.entries[0].timestamp
            last_entry = self.entries[-1].timestamp
        else:
            first_entry = last_entry = "N/A"

        return {
            "total_entries": len(self.entries),
            "level_counts": dict(level_counts),
            "module_counts": dict(module_counts),
            "error_count": level_counts["ERROR"],
            "warning_count": level_counts["WARNING"],
            "info_count": level_counts["INFO"],
            "error_types": dict(error_types.most_common(10)),
            "warning_types": dict(warning_types.most_common(10)),
            "time_range": {"start": first_entry, "end": last_entry},
            "errors": [e.to_dict() for e in errors],
            "warnings": [e.to_dict() for e in warnings],
        }


def export_html(analyzer, output_file):
    """Export log analysis to HTML"""
    summary = analyzer.get_summary()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
            padding-left: 10px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            padding: 20px;
            border-radius: 6px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stat-card.error {{ background: #fee; border-left: 4px solid #e74c3c; }}
        .stat-card.warning {{ background: #fff3cd; border-left: 4px solid #f39c12; }}
        .stat-card.info {{ background: #d1ecf1; border-left: 4px solid #3498db; }}
        .stat-card.total {{ background: #e8f5e9; border-left: 4px solid #27ae60; }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 14px;
            text-transform: uppercase;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .error-row {{ background: #fee; }}
        .warning-row {{ background: #fff3cd; }}
        .info-row {{ background: #d1ecf1; }}
        .timestamp {{ color: #7f8c8d; font-size: 12px; }}
        .level {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
        .level.ERROR {{ background: #e74c3c; color: white; }}
        .level.WARNING {{ background: #f39c12; color: white; }}
        .level.INFO {{ background: #3498db; color: white; }}
        .stacktrace {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            margin-top: 5px;
            white-space: pre-wrap;
            overflow-x: auto;
        }}
        .time-range {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Log Analysis Report</h1>
        <p><strong>Source:</strong> {analyzer.filename}</p>
        
        <div class="time-range">
            <strong>Time Range:</strong> {summary["time_range"]["start"]} → {summary["time_range"]["end"]}
        </div>
        
        <h2>Summary Statistics</h2>
        <div class="summary-grid">
            <div class="stat-card total">
                <div class="stat-label">Total Entries</div>
                <div class="stat-number">{summary["total_entries"]}</div>
            </div>
            <div class="stat-card error">
                <div class="stat-label">Errors</div>
                <div class="stat-number">{summary["error_count"]}</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-label">Warnings</div>
                <div class="stat-number">{summary["warning_count"]}</div>
            </div>
            <div class="stat-card info">
                <div class="stat-label">Info</div>
                <div class="stat-number">{summary["info_count"]}</div>
            </div>
        </div>
        
        <h2>Log Level Distribution</h2>
        <table>
            <tr>
                <th>Level</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
"""

    for level, count in sorted(
        summary["level_counts"].items(), key=lambda x: x[1], reverse=True
    ):
        percentage = (count / summary["total_entries"]) * 100
        html += f"""
            <tr>
                <td><span class="level {level}">{level}</span></td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
"""

    html += """
        </table>
        
        <h2>Module Activity</h2>
        <table>
            <tr>
                <th>Module</th>
                <th>Count</th>
            </tr>
"""

    for module, count in sorted(
        summary["module_counts"].items(), key=lambda x: x[1], reverse=True
    ):
        html += f"""
            <tr>
                <td>{module}</td>
                <td>{count}</td>
            </tr>
"""

    html += """
        </table>
        
        <h2>Top Error Types</h2>
        <table>
            <tr>
                <th>Error Type</th>
                <th>Occurrences</th>
            </tr>
"""

    for error_type, count in summary["error_types"].items():
        html += f"""
            <tr>
                <td>{error_type}</td>
                <td>{count}</td>
            </tr>
"""

    html += """
        </table>
        
        <h2>All Errors</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Module</th>
                <th>Message</th>
            </tr>
"""

    for error in summary["errors"]:
        html += f"""
            <tr class="error-row">
                <td class="timestamp">{error["timestamp"]}</td>
                <td>{error["module"]}</td>
                <td>
                    {error["message"]}
                    {f'<div class="stacktrace">{error["stacktrace"]}</div>' if error["stacktrace"] else ""}
                </td>
            </tr>
"""

    html += """
        </table>
        
        <h2>All Warnings</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Module</th>
                <th>Message</th>
            </tr>
"""

    for warning in summary["warnings"]:
        html += f"""
            <tr class="warning-row">
                <td class="timestamp">{warning["timestamp"]}</td>
                <td>{warning["module"]}</td>
                <td>{warning["message"]}</td>
            </tr>
"""

    html += """
        </table>
    </div>
</body>
</html>
"""

    with open(output_file, "w") as f:
        f.write(html)

    print_colored(f"✓ HTML report generated: {output_file}", Fore.GREEN)


def export_csv(analyzer, output_file):
    """Export log analysis to CSV"""
    summary = analyzer.get_summary()

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Summary section
        writer.writerow(["LOG ANALYSIS SUMMARY"])
        writer.writerow(["Source File", analyzer.filename])
        writer.writerow(["Total Entries", summary["total_entries"]])
        writer.writerow(["Errors", summary["error_count"]])
        writer.writerow(["Warnings", summary["warning_count"]])
        writer.writerow(["Info", summary["info_count"]])
        writer.writerow([])

        # Level distribution
        writer.writerow(["LEVEL DISTRIBUTION"])
        writer.writerow(["Level", "Count", "Percentage"])
        for level, count in sorted(
            summary["level_counts"].items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / summary["total_entries"]) * 100
            writer.writerow([level, count, f"{percentage:.1f}%"])
        writer.writerow([])

        # Module activity
        writer.writerow(["MODULE ACTIVITY"])
        writer.writerow(["Module", "Count"])
        for module, count in sorted(
            summary["module_counts"].items(), key=lambda x: x[1], reverse=True
        ):
            writer.writerow([module, count])
        writer.writerow([])

        # Top errors
        writer.writerow(["TOP ERROR TYPES"])
        writer.writerow(["Error Type", "Occurrences"])
        for error_type, count in summary["error_types"].items():
            writer.writerow([error_type, count])
        writer.writerow([])

        # All errors
        writer.writerow(["ALL ERRORS"])
        writer.writerow(["Timestamp", "Module", "Message", "Stacktrace"])
        for error in summary["errors"]:
            writer.writerow(
                [
                    error["timestamp"],
                    error["module"],
                    error["message"],
                    error["stacktrace"] or "",
                ]
            )
        writer.writerow([])

        # All warnings
        writer.writerow(["ALL WARNINGS"])
        writer.writerow(["Timestamp", "Module", "Message"])
        for warning in summary["warnings"]:
            writer.writerow(
                [warning["timestamp"], warning["module"], warning["message"]]
            )

    print_colored(f"✓ CSV report generated: {output_file}", Fore.GREEN)


def export_json(analyzer, output_file):
    """Export log analysis to JSON"""
    summary = analyzer.get_summary()
    summary["source_file"] = analyzer.filename

    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    print_colored(f"✓ JSON report generated: {output_file}", Fore.GREEN)


def export_pdf(analyzer, output_file):
    """Export log analysis to PDF (requires reportlab)"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate,
            Table,
            TableStyle,
            Paragraph,
            Spacer,
        )
        from reportlab.lib.units import inch
    except ImportError:
        print_colored("ERROR: reportlab is required for PDF export", Fore.RED)
        print_colored("Install it with: pip install reportlab", Fore.YELLOW)
        return

    summary = analyzer.get_summary()
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=30,
    )
    elements.append(Paragraph("Log Analysis Report", title_style))
    elements.append(Paragraph(f"<b>Source:</b> {analyzer.filename}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))

    # Summary statistics
    elements.append(Paragraph("Summary Statistics", styles["Heading2"]))
    summary_data = [
        ["Metric", "Value"],
        ["Total Entries", str(summary["total_entries"])],
        ["Errors", str(summary["error_count"])],
        ["Warnings", str(summary["warning_count"])],
        ["Info", str(summary["info_count"])],
    ]

    summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Top errors
    elements.append(Paragraph("Top Error Types", styles["Heading2"]))
    error_data = [["Error Type", "Count"]]
    for error_type, count in list(summary["error_types"].items())[:10]:
        error_data.append([error_type[:50], str(count)])

    if len(error_data) > 1:
        error_table = Table(error_data, colWidths=[4 * inch, 1 * inch])
        error_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightcoral),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        elements.append(error_table)

    doc.build(elements)
    print_colored(f"✓ PDF report generated: {output_file}", Fore.GREEN)


def init_cli():
    """Validates CLI flags and returns filename + output type"""
    if len(sys.argv) == 1 or (
        len(sys.argv) >= 2 and sys.argv[1].lower() in ["-h", "--help"]
    ):
        help_text = """Usage:
  logsense.py [FILENAME].log -e|--export [type: html, csv, json, pdf]

Examples:
  logsense.py app.log --export html
  logsense.py app.log -e json
  logsense.py app.log -e csv
        """
        print_colored(help_text, color=Fore.WHITE, exit=True, cap=False)

    if len(sys.argv) < 4:
        print_colored(
            text=".log file and output type are required\nuse -h for help",
            color=Fore.RED,
            exit=True,
            cap=True,
        )

    filename = sys.argv[1]
    if not filename.endswith(".log"):
        print_colored(
            text="GIVEN FILE TYPE IS NOT SUPPORTED\nOnly .log files are accepted",
            color=Fore.RED,
            exit=True,
            cap=True,
        )

    if not os.path.exists(filename):
        print_colored(
            text=f"FILE NOT FOUND: {filename}",
            color=Fore.RED,
            exit=True,
            cap=True,
        )

    export_flag = sys.argv[2]
    if export_flag not in ["-e", "--export"]:
        print_colored(
            text="EXPORT FLAG IS REQUIRED\nUse -e or --export",
            color=Fore.RED,
            exit=True,
            cap=True,
        )

    output_type = sys.argv[3].lower()
    valid_types = ["html", "csv", "json", "pdf"]
    if output_type not in valid_types:
        print_colored(
            text=f"INVALID OUTPUT TYPE: {sys.argv[3]}\nSupported types: {', '.join(valid_types)}",
            color=Fore.RED,
            exit=True,
            cap=True,
        )

    return (filename, output_type)


def print_colored(text: str, color=Fore.WHITE, exit=False, cap=False) -> None:
    print(color + (text.upper() if cap else text))
    if exit:
        raise SystemExit(1)


def main():
    filename, output_mode = init_cli()

    print_colored(f"📖 Analyzing log file: {filename}", Fore.CYAN)
    analyzer = LogAnalyzer(filename)
    print_colored(f"✓ Parsed {len(analyzer.entries)} log entries", Fore.GREEN)

    # Generate output filename
    base_name = os.path.splitext(filename)[0]
    output_file = f"{base_name}_report.{output_mode}"

    match output_mode:
        case "html":
            export_html(analyzer, output_file)
        case "csv":
            export_csv(analyzer, output_file)
        case "json":
            export_json(analyzer, output_file)
        case "pdf":
            export_pdf(analyzer, output_file)
        case _:
            print_colored("Invalid export type!", color=Fore.RED, exit=True, cap=True)


if __name__ == "__main__":
    main()
