#!/usr/bin/env python3
"""
HAK-GAL Analytics Dashboard Generator
====================================

Erstellt interaktive HTML-Dashboards aus den Stress-Test Ergebnissen.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import statistics
from typing import Dict, List, Any

def generate_html_dashboard(metrics_file: Path, output_file: Path):
    """Generate interactive HTML dashboard from metrics"""
    
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)
    
    if not metrics:
        print("No metrics found in file")
        return
    
    # Prepare data for charts
    timestamps = [m['timestamp'] for m in metrics]
    response_times = [m['response_time_ms'] for m in metrics]
    success_data = [1 if m['success'] else 0 for m in metrics]
    
    # Command type analysis
    command_counts = {}
    for m in metrics:
        cmd = m['command_type']
        command_counts[cmd] = command_counts.get(cmd, 0) + 1
    
    # Error analysis
    error_counts = {}
    for m in metrics:
        if not m['success'] and m['error_message']:
            error = m['error_message']
            error_counts[error] = error_counts.get(error, 0) + 1
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAK-GAL Stress Test Analytics Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #4CAF50;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .chart-container {{
            padding: 30px;
            margin: 20px 0;
        }}
        .chart {{
            height: 400px;
            margin: 20px 0;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .section-title {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #4CAF50;
        }}
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        .competitive-analysis {{
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
            color: white;
            padding: 30px;
            margin: 30px;
            border-radius: 15px;
        }}
        .competitive-analysis h2 {{
            margin-top: 0;
        }}
        .advantage-list {{
            list-style: none;
            padding: 0;
        }}
        .advantage-list li {{
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }}
        .advantage-list li:before {{
            content: "✅ ";
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 HAK-GAL Analytics Dashboard</h1>
            <p>Autonomous Stress Test Results</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Queries</div>
                <div class="stat-value">{len(metrics)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{(sum(1 for m in metrics if m['success']) / len(metrics) * 100):.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Response Time</div>
                <div class="stat-value">{statistics.mean([m['response_time_ms'] for m in metrics if m['success']]):.0f}ms</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">P95 Response Time</div>
                <div class="stat-value">{statistics.quantiles([m['response_time_ms'] for m in metrics if m['success']], n=20)[18] if len([m for m in metrics if m['success']]) > 20 else max([m['response_time_ms'] for m in metrics if m['success']]):.0f}ms</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Errors</div>
                <div class="stat-value">{sum(1 for m in metrics if not m['success'])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Facts Extracted</div>
                <div class="stat-value">{sum(m['facts_extracted'] for m in metrics)}</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2 class="section-title">📈 Performance Timeline</h2>
            <div id="response-time-chart" class="chart"></div>
        </div>
        
        <div class="chart-container">
            <h2 class="section-title">✅ Success Rate Over Time</h2>
            <div id="success-rate-chart" class="chart"></div>
        </div>
        
        <div class="chart-container">
            <h2 class="section-title">🎯 Command Type Distribution</h2>
            <div id="command-distribution-chart" class="chart"></div>
        </div>
        
        <div class="chart-container">
            <h2 class="section-title">❌ Error Analysis</h2>
            <div id="error-analysis-chart" class="chart"></div>
        </div>
        
        <div class="competitive-analysis">
            <h2>🏆 HAK-GAL vs Imandra Competitive Analysis</h2>
            <ul class="advantage-list">
                <li><strong>Autonomous Testing Framework:</strong> HAK-GAL has comprehensive stress testing, Imandra doesn't offer this</li>
                <li><strong>Human-in-the-Loop Learning:</strong> Revolutionary fact extraction and curation interface</li>
                <li><strong>Transparent Performance Metrics:</strong> Real-time observability and analytics</li>
                <li><strong>Self-Sovereign Architecture:</strong> No cloud dependencies, full control</li>
                <li><strong>Advanced Orchestration:</strong> Multi-LLM ensemble with adaptive strategies</li>
                <li><strong>Quality Assurance:</strong> Built-in stress testing and validation tools</li>
            </ul>
        </div>
        
        <div class="footer">
            Generated by HAK-GAL Analytics Engine • {datetime.now().year} • Neuro-Symbolic AI Excellence
        </div>
    </div>

    <script>
        // Response Time Chart
        const responseTimeTrace = {{
            x: {timestamps},
            y: {response_times},
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Response Time (ms)',
            line: {{ color: '#4CAF50', width: 2 }},
            marker: {{ size: 4 }}
        }};
        
        Plotly.newPlot('response-time-chart', [responseTimeTrace], {{
            title: 'Response Time Over Time',
            xaxis: {{ title: 'Time' }},
            yaxis: {{ title: 'Response Time (ms)' }},
            hovermode: 'closest'
        }});
        
        // Success Rate Chart
        const successTrace = {{
            x: {timestamps},
            y: {success_data},
            type: 'scatter',
            mode: 'markers',
            name: 'Success (1) / Failure (0)',
            marker: {{ 
                size: 8,
                color: {success_data},
                colorscale: [
                    [0, '#FF6B6B'],
                    [1, '#4CAF50']
                ],
                showscale: true
            }}
        }};
        
        Plotly.newPlot('success-rate-chart', [successTrace], {{
            title: 'Success/Failure Timeline',
            xaxis: {{ title: 'Time' }},
            yaxis: {{ title: 'Success (1) / Failure (0)' }},
            hovermode: 'closest'
        }});
        
        // Command Distribution Chart
        const commandTrace = {{
            labels: {list(command_counts.keys())},
            values: {list(command_counts.values())},
            type: 'pie',
            hole: 0.4,
            marker: {{
                colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
            }}
        }};
        
        Plotly.newPlot('command-distribution-chart', [commandTrace], {{
            title: 'Command Type Distribution'
        }});
        
        // Error Analysis Chart
        const errorTrace = {{
            x: {list(error_counts.keys())},
            y: {list(error_counts.values())},
            type: 'bar',
            marker: {{ color: '#FF6B6B' }}
        }};
        
        Plotly.newPlot('error-analysis-chart', [errorTrace], {{
            title: 'Error Type Frequency',
            xaxis: {{ title: 'Error Type' }},
            yaxis: {{ title: 'Count' }}
        }});
    </script>
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"📊 Interactive dashboard generated: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate HAK-GAL Analytics Dashboard")
    parser.add_argument("metrics_file", help="Path to metrics JSON file")
    parser.add_argument("--output", default="hak_gal_dashboard.html", help="Output HTML file")
    
    args = parser.parse_args()
    
    metrics_file = Path(args.metrics_file)
    output_file = Path(args.output)
    
    if not metrics_file.exists():
        print(f"❌ Metrics file not found: {metrics_file}")
        return
    
    generate_html_dashboard(metrics_file, output_file)

if __name__ == "__main__":
    main()
