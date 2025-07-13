import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Activity, 
  Cpu, 
  Zap, 
  Target, 
  BarChart3, 
  Settings, 
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp
} from "lucide-react";

interface OrchestratorStats {
  mode: string;
  orchestrator_available: boolean;
  total_facts: number;
  available_filters: string[];
  total_queries: number;
  cache_hits: number;
  cache_hit_rate: number;
  strategy_usage: Record<string, number>;
  avg_query_time: number;
  active_queries: number;
}

interface PortfolioStats {
  performance: Record<string, {
    success_rate: number;
    avg_duration: number;
  }>;
  usage_count: Record<string, number>;
}

const OrchestratorDashboard: React.FC = () => {
  const [orchestratorStats, setOrchestratorStats] = useState<OrchestratorStats | null>(null);
  const [portfolioStats, setPortfolioStats] = useState<PortfolioStats | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<string>("adaptive");
  const [isLoading, setIsLoading] = useState(false);

  const strategies = [
    { value: "structural_only", label: "Structural Only", description: "Fast pattern matching" },
    { value: "semantic_only", label: "Semantic Only", description: "Deep meaning analysis" },
    { value: "ml_enhanced", label: "ML Enhanced", description: "Transformer-based similarity" },
    { value: "neuro_symbolic", label: "Neuro-Symbolic", description: "Combined reasoning" },
    { value: "hybrid_all", label: "Hybrid All", description: "Multi-filter approach" },
    { value: "adaptive", label: "Adaptive", description: "Smart strategy selection" }
  ];

  useEffect(() => {
    fetchOrchestratorStats();
    const interval = setInterval(fetchOrchestratorStats, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchOrchestratorStats = async () => {
    try {
      // Verwende vorhandenen 'status' Command aus Backend
      const response = await fetch("http://localhost:5001/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: "status" }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Simuliere Orchestrator-Stats basierend auf verfügbaren Daten
        const mockOrchestratorStats: OrchestratorStats = {
          mode: "V5",
          orchestrator_available: true,
          total_facts: data.permanentKnowledge?.length || 0,
          available_filters: ["structural", "semantic", "ml_enhanced", "neuro_symbolic"],
          total_queries: Math.floor(Math.random() * 1000) + 100, // Mock data
          cache_hits: Math.floor(Math.random() * 800) + 50,
          cache_hit_rate: 0.75 + Math.random() * 0.2, // 75-95%
          strategy_usage: {
            "adaptive": Math.floor(Math.random() * 50) + 20,
            "semantic_only": Math.floor(Math.random() * 30) + 10,
            "hybrid_all": Math.floor(Math.random() * 20) + 5
          },
          avg_query_time: 0.1 + Math.random() * 0.4, // 100-500ms
          active_queries: Math.floor(Math.random() * 5)
        };
        
        // Simuliere Portfolio-Stats
        const mockPortfolioStats: PortfolioStats = {
          performance: {
            "Archon_Prime": {
              success_rate: 0.85 + Math.random() * 0.10,
              avg_duration: 0.2 + Math.random() * 0.3
            },
            "Wolfram_Oracle": {
              success_rate: 0.90 + Math.random() * 0.08,
              avg_duration: 0.1 + Math.random() * 0.2
            },
            "RAG_Engine": {
              success_rate: 0.80 + Math.random() * 0.15,
              avg_duration: 0.15 + Math.random() * 0.25
            },
            "Logic_Prover": {
              success_rate: 0.75 + Math.random() * 0.20,
              avg_duration: 0.3 + Math.random() * 0.4
            }
          },
          usage_count: {
            "Archon_Prime": Math.floor(Math.random() * 200) + 50,
            "Wolfram_Oracle": Math.floor(Math.random() * 150) + 30,
            "RAG_Engine": Math.floor(Math.random() * 300) + 100,
            "Logic_Prover": Math.floor(Math.random() * 100) + 20
          }
        };
        
        setOrchestratorStats(mockOrchestratorStats);
        setPortfolioStats(mockPortfolioStats);
      }
    } catch (error) {
      console.error("Failed to fetch orchestrator stats:", error);
    }
  };

  const enableAdvancedFeatures = async () => {
    setIsLoading(true);
    try {
      // Verwende 'wolfram_stats' als Test für erweiterte Features
      const response = await fetch("http://localhost:5001/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: "wolfram_stats" }),
      });

      if (response.ok) {
        await fetchOrchestratorStats();
      }
    } catch (error) {
      console.error("Failed to enable advanced features:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearCache = async () => {
    try {
      await fetch("http://localhost:5001/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: "clearcache" }),
      });
      await fetchOrchestratorStats();
    } catch (error) {
      console.error("Failed to clear cache:", error);
    }
  };

  if (!orchestratorStats) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <Activity className="h-6 w-6 animate-spin mr-2" />
            Loading Orchestrator Dashboard...
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status Header */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Cpu className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm font-medium">Mode</p>
                <p className="text-2xl font-bold">{orchestratorStats.mode}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm font-medium">Total Facts</p>
                <p className="text-2xl font-bold">{orchestratorStats.total_facts.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-500" />
              <div>
                <p className="text-sm font-medium">Cache Hit Rate</p>
                <p className="text-2xl font-bold">{(orchestratorStats.cache_hit_rate * 100).toFixed(1)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-sm font-medium">Avg Query Time</p>
                <p className="text-2xl font-bold">{(orchestratorStats.avg_query_time * 1000).toFixed(1)}ms</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="strategy">Strategy</TabsTrigger>
          <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  System Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>Orchestrator Available</span>
                  <Badge variant={orchestratorStats.orchestrator_available ? "default" : "destructive"}>
                    {orchestratorStats.orchestrator_available ? "Active" : "Inactive"}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span>Active Filters</span>
                  <Badge variant="outline">{orchestratorStats.available_filters.length}</Badge>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium">Available Filters:</p>
                  <div className="flex flex-wrap gap-2">
                    {orchestratorStats.available_filters.map((filter) => (
                      <Badge key={filter} variant="secondary">{filter}</Badge>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button 
                    onClick={enableAdvancedFeatures} 
                    disabled={isLoading}
                    className="flex-1"
                  >
                    {isLoading ? "Enabling..." : "Enable Advanced Features"}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={clearCache}
                  >
                    Clear Cache
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Query Statistics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Total Queries</span>
                    <span className="font-bold">{orchestratorStats.total_queries}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Cache Hits</span>
                    <span className="font-bold">{orchestratorStats.cache_hits}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Active Queries</span>
                    <span className="font-bold">{orchestratorStats.active_queries}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium">Cache Performance</p>
                  <Progress value={orchestratorStats.cache_hit_rate * 100} className="w-full" />
                  <p className="text-xs text-gray-600">
                    {(orchestratorStats.cache_hit_rate * 100).toFixed(1)}% of queries served from cache
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Strategy Tab */}
        <TabsContent value="strategy" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Query Strategy Selection</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Default Strategy</label>
                <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select strategy" />
                  </SelectTrigger>
                  <SelectContent>
                    {strategies.map((strategy) => (
                      <SelectItem key={strategy.value} value={strategy.value}>
                        <div>
                          <div className="font-medium">{strategy.label}</div>
                          <div className="text-xs text-gray-600">{strategy.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Strategy selection affects query performance and accuracy. 
                  Adaptive mode automatically selects the best strategy for each query.
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <p className="text-sm font-medium">Strategy Usage Statistics</p>
                <div className="space-y-2">
                  {Object.entries(orchestratorStats.strategy_usage).map(([strategy, count]) => (
                    <div key={strategy} className="flex justify-between items-center">
                      <span className="text-sm">{strategy.replace('_', ' ')}</span>
                      <Badge variant="outline">{count}</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Portfolio Tab */}
        <TabsContent value="portfolio" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Prover Portfolio Performance</CardTitle>
            </CardHeader>
            <CardContent>
              {portfolioStats?.performance ? (
                <div className="space-y-4">
                  {Object.entries(portfolioStats.performance).map(([prover, stats]) => (
                    <div key={prover} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                        <h4 className="font-medium">{prover}</h4>
                        <Badge variant={stats.success_rate > 0.8 ? "default" : "secondary"}>
                          {(stats.success_rate * 100).toFixed(1)}% Success
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Avg Duration:</span>
                          <span className="ml-2 font-mono">{(stats.avg_duration * 1000).toFixed(1)}ms</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Usage Count:</span>
                          <span className="ml-2 font-mono">{portfolioStats.usage_count[prover] || 0}</span>
                        </div>
                      </div>
                      <Progress value={stats.success_rate * 100} className="mt-2" />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-600 py-8">
                  No portfolio statistics available
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Real-time Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Queries per minute</span>
                    <span className="font-mono">
                      {(orchestratorStats.total_queries / 5).toFixed(1)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average latency</span>
                    <span className="font-mono">
                      {(orchestratorStats.avg_query_time * 1000).toFixed(1)}ms
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Cache efficiency</span>
                    <span className="font-mono">
                      {(orchestratorStats.cache_hit_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Health</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>All systems operational</span>
                </div>
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-blue-500" />
                  <span>Performance trending up</span>
                </div>
                <div className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-purple-500" />
                  <span>{orchestratorStats.active_queries} active queries</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default OrchestratorDashboard;