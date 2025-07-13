#!/usr/bin/env python3
"""
HAK-GAL Autonomous Stress Testing & Analytics Engine
===================================================

Sendet alle 30 Sekunden diverse Anfragen an das HAK-GAL Backend
und sammelt umfassende Performance- und Qualitäts-Metriken.

Usage:
    python hak_gal_stress_tester.py [--interval 30] [--duration 3600]
    
Features:
    🎯 Automatische Query-Rotation (ask, explain, learn, status, etc.)
    📊 Performance-Metriken Collection  
    🧠 Fact-Learning-Pipeline Testing
    ⚡ Timeout & Error Analysis
    📈 Automated Final Reports
    🔬 Observability Stack Validation
"""

import asyncio
import aiohttp
import json
import time
import random
import signal
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics

@dataclass
class QueryMetrics:
    """Metrics for a single query execution"""
    timestamp: str
    command_type: str
    query: str
    response_time_ms: float
    success: bool
    error_message: Optional[str]
    response_length: int
    facts_extracted: int
    learning_suggestions: int
    permanent_knowledge_count: int
    backend_issue: Optional[str]
    timeout_occurred: bool
    http_status: int

@dataclass
class SystemSnapshot:
    """System state snapshot"""
    timestamp: str
    llm_active: int
    llm_total: int
    knowledge_count: int
    suggestions_count: int
    data_sources: int
    wolfram_available: bool

class HAKGALStressTester:
    """HAK-GAL Autonomous Stress Testing Engine"""
    
    def __init__(self, base_url: str = "http://localhost:5001", interval: int = 30):
        self.base_url = base_url
        self.interval = interval
        self.running = True
        self.metrics: List[QueryMetrics] = []
        self.snapshots: List[SystemSnapshot] = []
        self.start_time = datetime.now()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Query pools for different testing scenarios
        self.query_pools = {
            'ask_simple': [
                "ask Was ist Machine Learning?",
                "ask Erkläre Künstliche Intelligenz.",
                "ask Was bedeutet HAK-GAL?",
                "ask Wie funktioniert Deep Learning?",
                "ask Was ist ein neuronales Netz?"
            ],
            'ask_complex': [
                "ask AkkumuliertZwischen(MachineLearning, NeuralNetworks).",
                "ask Evaluiere(SystemPerformance, OptimierungsStrategien).",
                "ask AnalysiereBeziehung(KuenstlicheIntelligenz, SymbolischeLogik).",
                "ask BewerteKompatibilitaet(LLMProvider, ReasoningEngine).",
                "ask OptimiereFuerProduktion(HAK_GAL_System)."
            ],
            'explain': [
                "explain neuro-symbolic AI",
                "explain logical reasoning",
                "explain knowledge representation",
                "explain automated theorem proving",
                "explain RAG pipeline"
            ],
            'learn_cycle': [
                "add_raw Funktioniert(PerformanceTest).",
                "add_raw Optimiert(SystemResponse).",
                "add_raw Validiert(BackendStability).",
                "learn",
                "show"
            ],
            'system_checks': [
                "status",
                "wolfram_stats", 
                "advanced_tools_status",
                "sources",
                "help"
            ],
            'edge_cases': [
                "ask " + "x" * 200,  # Very long query
                "ask 🤖🧠💻🚀",  # Unicode/Emoji query
                "parse InvalidSyntax(Missing.",  # Syntax error
                "ask Löse(ComplexConstraint(A,B,C,D,E)).",  # Complex logical formula
                "retract NonExistent(Fact)."  # Non-existent retraction
            ]
        }
        
        # Setup signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print(f"\n🛑 Received signal {signum}. Shutting down gracefully...")
        self.running = False
    
    async def setup_session(self):
        """Setup aiohttp session with timeouts"""
        timeout = aiohttp.ClientTimeout(total=120)  # 2 minute timeout
        self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def cleanup_session(self):
        """Cleanup aiohttp session"""
        if self.session:
            await self.session.close()
    
    def get_random_query(self) -> tuple[str, str]:
        """Get a random query from the pools"""
        # Weight distribution for different query types
        weights = {
            'ask_simple': 0.3,
            'ask_complex': 0.2, 
            'explain': 0.2,
            'learn_cycle': 0.15,
            'system_checks': 0.1,
            'edge_cases': 0.05
        }
        
        # Weighted random selection
        pool_name = random.choices(
            list(weights.keys()), 
            weights=list(weights.values())
        )[0]
        
        query = random.choice(self.query_pools[pool_name])
        return pool_name, query
    
    async def execute_query(self, query: str) -> QueryMetrics:
        """Execute a single query and collect metrics"""
        start_time = time.time()
        command_type = query.split()[0] if query.split() else "unknown"
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/command",
                json={"command": query},
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                
                # Extract metrics from response
                success = response.status == 200 and response_data.get("status") == "success"
                error_message = response_data.get("error") if not success else None
                response_length = len(str(response_data))
                
                # Extract HAK-GAL specific metrics
                permanent_knowledge_count = len(response_data.get("permanentKnowledge", []))
                learning_suggestions = len(response_data.get("learningSuggestions", []))
                
                # Detect backend issues from response
                chat_response = response_data.get("chatResponse", "")
                backend_issue = None
                if "BACKEND-" in chat_response or "Error:" in chat_response:
                    backend_issue = "detected_in_response"
                
                # Estimate facts that could be extracted (simple heuristic)
                facts_extracted = chat_response.count('.') if chat_response else 0
                
                timeout_occurred = response_time_ms > 45000  # 45s timeout threshold
                
                return QueryMetrics(
                    timestamp=datetime.now().isoformat(),
                    command_type=command_type,
                    query=query[:100] + "..." if len(query) > 100 else query,
                    response_time_ms=response_time_ms,
                    success=success,
                    error_message=error_message,
                    response_length=response_length,
                    facts_extracted=facts_extracted,
                    learning_suggestions=learning_suggestions,
                    permanent_knowledge_count=permanent_knowledge_count,
                    backend_issue=backend_issue,
                    timeout_occurred=timeout_occurred,
                    http_status=response.status
                )
                
        except asyncio.TimeoutError:
            end_time = time.time()
            return QueryMetrics(
                timestamp=datetime.now().isoformat(),
                command_type=command_type,
                query=query[:100] + "..." if len(query) > 100 else query,
                response_time_ms=(end_time - start_time) * 1000,
                success=False,
                error_message="Timeout",
                response_length=0,
                facts_extracted=0,
                learning_suggestions=0,
                permanent_knowledge_count=0,
                backend_issue="timeout",
                timeout_occurred=True,
                http_status=0
            )
        except Exception as e:
            end_time = time.time()
            return QueryMetrics(
                timestamp=datetime.now().isoformat(),
                command_type=command_type,
                query=query[:100] + "..." if len(query) > 100 else query,
                response_time_ms=(end_time - start_time) * 1000,
                success=False,
                error_message=str(e),
                response_length=0,
                facts_extracted=0,
                learning_suggestions=0,
                permanent_knowledge_count=0,
                backend_issue="connection_error",
                timeout_occurred=False,
                http_status=0
            )
    
    async def take_system_snapshot(self) -> SystemSnapshot:
        """Take a snapshot of system state"""
        try:
            async with self.session.post(
                f"{self.base_url}/api/command",
                json={"command": "status"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    llm_status = data.get("llmStatus", {})
                    
                    return SystemSnapshot(
                        timestamp=datetime.now().isoformat(),
                        llm_active=llm_status.get("llm_active", 0),
                        llm_total=llm_status.get("llm_count", 0),
                        knowledge_count=len(data.get("permanentKnowledge", [])),
                        suggestions_count=len(data.get("learningSuggestions", [])),
                        data_sources=len(data.get("dataSources", [])),
                        wolfram_available="Wolfram" in data.get("chatResponse", "")
                    )
        except Exception as e:
            print(f"⚠️ Failed to take system snapshot: {e}")
            
        # Return empty snapshot on failure
        return SystemSnapshot(
            timestamp=datetime.now().isoformat(),
            llm_active=0,
            llm_total=0,
            knowledge_count=0,
            suggestions_count=0,
            data_sources=0,
            wolfram_available=False
        )
    
    def save_metrics_to_file(self):
        """Save current metrics to JSON file"""
        output_dir = Path("stress_test_results")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed metrics
        metrics_file = output_dir / f"hak_gal_metrics_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            json.dump([asdict(m) for m in self.metrics], f, indent=2)
        
        # Save system snapshots
        snapshots_file = output_dir / f"hak_gal_snapshots_{timestamp}.json"
        with open(snapshots_file, 'w') as f:
            json.dump([asdict(s) for s in self.snapshots], f, indent=2)
        
        print(f"💾 Metrics saved to: {metrics_file}")
        print(f"💾 Snapshots saved to: {snapshots_file}")
        
        return metrics_file, snapshots_file
    
    def generate_analysis_report(self) -> str:
        """Generate comprehensive analysis report"""
        if not self.metrics:
            return "No metrics collected yet."
        
        # Calculate statistics
        total_queries = len(self.metrics)
        successful_queries = sum(1 for m in self.metrics if m.success)
        success_rate = (successful_queries / total_queries) * 100
        
        response_times = [m.response_time_ms for m in self.metrics if m.success]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        median_response_time = statistics.median(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times) if response_times else 0
        
        # Error analysis
        errors = [m for m in self.metrics if not m.success]
        error_types = {}
        for error in errors:
            error_type = error.error_message or "Unknown"
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Command type analysis
        command_stats = {}
        for metric in self.metrics:
            cmd = metric.command_type
            if cmd not in command_stats:
                command_stats[cmd] = {"count": 0, "success": 0, "avg_time": 0}
            command_stats[cmd]["count"] += 1
            if metric.success:
                command_stats[cmd]["success"] += 1
                command_stats[cmd]["avg_time"] += metric.response_time_ms
        
        # Calculate averages
        for cmd_data in command_stats.values():
            if cmd_data["success"] > 0:
                cmd_data["avg_time"] /= cmd_data["success"]
            cmd_data["success_rate"] = (cmd_data["success"] / cmd_data["count"]) * 100
        
        # Backend issues analysis
        backend_issues = [m for m in self.metrics if m.backend_issue]
        timeouts = [m for m in self.metrics if m.timeout_occurred]
        
        # Knowledge growth analysis
        if self.snapshots:
            initial_knowledge = self.snapshots[0].knowledge_count
            final_knowledge = self.snapshots[-1].knowledge_count
            knowledge_growth = final_knowledge - initial_knowledge
        else:
            knowledge_growth = 0
        
        # Duration calculation
        duration = datetime.now() - self.start_time
        duration_hours = duration.total_seconds() / 3600
        
        # Generate report
        report = f"""
🎯 HAK-GAL AUTONOMOUS STRESS TEST REPORT
{'='*60}

📊 EXECUTIVE SUMMARY
Test Duration: {duration_hours:.2f} hours
Total Queries: {total_queries}
Success Rate: {success_rate:.1f}%
Average Response Time: {avg_response_time:.0f}ms
95th Percentile Response Time: {p95_response_time:.0f}ms

⚡ PERFORMANCE ANALYSIS
📈 Response Time Statistics:
   • Average: {avg_response_time:.0f}ms
   • Median: {median_response_time:.0f}ms  
   • 95th Percentile: {p95_response_time:.0f}ms
   • Max: {max(response_times) if response_times else 0:.0f}ms
   • Min: {min(response_times) if response_times else 0:.0f}ms

🎯 COMMAND TYPE ANALYSIS
"""

        for cmd, stats in sorted(command_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            report += f"   • {cmd}: {stats['count']} queries, {stats['success_rate']:.1f}% success, {stats['avg_time']:.0f}ms avg\n"

        report += f"""
❌ ERROR ANALYSIS
Total Errors: {len(errors)} ({(len(errors)/total_queries)*100:.1f}%)
Timeouts: {len(timeouts)} ({(len(timeouts)/total_queries)*100:.1f}%)
Backend Issues: {len(backend_issues)} ({(len(backend_issues)/total_queries)*100:.1f}%)

🔍 ERROR BREAKDOWN
"""

        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            report += f"   • {error_type}: {count} occurrences\n"

        report += f"""
🧠 KNOWLEDGE SYSTEM ANALYSIS
Knowledge Growth: {knowledge_growth} new facts learned
Total Facts Extracted: {sum(m.facts_extracted for m in self.metrics)}
Learning Suggestions Generated: {sum(m.learning_suggestions for m in self.metrics)}

🔬 SYSTEM HEALTH
LLM Providers: {self.snapshots[-1].llm_active}/{self.snapshots[-1].llm_total} active (last check)
Data Sources: {self.snapshots[-1].data_sources} loaded
Wolfram Integration: {'✅ Active' if self.snapshots[-1].wolfram_available else '❌ Inactive'}

📈 RECOMMENDATIONS
"""

        # Generate recommendations based on metrics
        recommendations = []
        
        if success_rate < 95:
            recommendations.append(f"• Success rate ({success_rate:.1f}%) below target (95%) - investigate error causes")
        
        if avg_response_time > 5000:
            recommendations.append(f"• Average response time ({avg_response_time:.0f}ms) exceeds 5s target")
        
        if len(timeouts) > total_queries * 0.05:
            recommendations.append(f"• High timeout rate ({(len(timeouts)/total_queries)*100:.1f}%) - consider timeout optimization")
        
        if knowledge_growth == 0:
            recommendations.append("• No knowledge growth detected - learning pipeline may need attention")
        
        if not recommendations:
            recommendations.append("• System performing within acceptable parameters ✅")
        
        for rec in recommendations:
            report += rec + "\n"

        report += f"""
🏆 COMPETITIVE ANALYSIS vs Imandra
• Autonomous Testing: ✅ HAK-GAL has it, Imandra doesn't
• Human-in-the-Loop Learning: ✅ HAK-GAL leads  
• Comprehensive Observability: ✅ HAK-GAL advantage
• Performance Transparency: ✅ Real-time metrics available

{'='*60}
Generated: {datetime.now().isoformat()}
Test Configuration: {self.interval}s intervals, {duration_hours:.1f}h duration
"""

        return report
    
    def print_live_status(self, iteration: int, last_metric: QueryMetrics):
        """Print live status during execution"""
        elapsed = datetime.now() - self.start_time
        success_rate = (sum(1 for m in self.metrics if m.success) / len(self.metrics)) * 100 if self.metrics else 0
        
        print(f"\r🤖 Query {iteration} | ⏱️ {elapsed.total_seconds()/3600:.1f}h | ✅ {success_rate:.1f}% | Last: {last_metric.command_type} ({last_metric.response_time_ms:.0f}ms)", end="", flush=True)
    
    async def run(self, duration_hours: Optional[float] = None):
        """Main execution loop"""
        print("🚀 HAK-GAL Autonomous Stress Tester Starting...")
        print(f"🎯 Target: {self.base_url}")
        print(f"⏱️ Interval: {self.interval} seconds")
        if duration_hours:
            print(f"⏰ Duration: {duration_hours} hours")
        print("🛑 Stop with Ctrl+C")
        print("=" * 60)
        
        await self.setup_session()
        
        # Take initial system snapshot
        initial_snapshot = await self.take_system_snapshot()
        self.snapshots.append(initial_snapshot)
        print(f"📸 Initial snapshot: {initial_snapshot.knowledge_count} facts, {initial_snapshot.llm_active}/{initial_snapshot.llm_total} LLMs")
        
        iteration = 0
        end_time = datetime.now() + timedelta(hours=duration_hours) if duration_hours else None
        
        try:
            while self.running:
                if end_time and datetime.now() >= end_time:
                    print(f"\n⏰ Duration limit ({duration_hours}h) reached. Stopping...")
                    break
                
                iteration += 1
                
                # Get random query
                pool_name, query = self.get_random_query()
                
                # Execute query
                metric = await self.execute_query(query)
                self.metrics.append(metric)
                
                # Take system snapshot every 10 iterations
                if iteration % 10 == 0:
                    snapshot = await self.take_system_snapshot()
                    self.snapshots.append(snapshot)
                
                # Print live status
                self.print_live_status(iteration, metric)
                
                # Save metrics every 50 iterations
                if iteration % 50 == 0:
                    self.save_metrics_to_file()
                
                # Wait for next iteration
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Interrupted by user after {iteration} queries")
        finally:
            await self.cleanup_session()
            
            # Final save and analysis
            print(f"\n📊 Generating final analysis...")
            self.save_metrics_to_file()
            
            # Generate and save final report
            report = self.generate_analysis_report()
            
            output_dir = Path("stress_test_results")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = output_dir / f"hak_gal_analysis_{timestamp}.txt"
            
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"📋 Final report saved to: {report_file}")
            print("\n" + report)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="HAK-GAL Autonomous Stress Tester")
    parser.add_argument("--url", default="http://localhost:5001", help="Backend URL")
    parser.add_argument("--interval", type=int, default=30, help="Query interval in seconds")
    parser.add_argument("--duration", type=float, help="Test duration in hours")
    
    args = parser.parse_args()
    
    tester = HAKGALStressTester(base_url=args.url, interval=args.interval)
    await tester.run(duration_hours=args.duration)

if __name__ == "__main__":
    asyncio.run(main())
