import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Search, 
  Brain, 
  Code, 
  Zap, 
  Plus, 
  X, 
  Play,
  BookOpen,
  Target,
  Settings,
  HelpCircle
} from "lucide-react";

interface QueryTemplate {
  id: string;
  name: string;
  command: string;
  description: string;
  parameters: string[];
}

interface AdvancedQueryBuilderProps {
  onExecuteQuery: (query: string) => void;
}

const AdvancedQueryBuilder: React.FC<AdvancedQueryBuilderProps> = ({ onExecuteQuery }) => {
  const [queryType, setQueryType] = useState<string>("natural");
  const [queryText, setQueryText] = useState<string>("");
  const [logicalFormula, setLogicalFormula] = useState<string>("");
  const [selectedTemplate, setSelectedTemplate] = useState<string>("");
  const [parameters, setParameters] = useState<Record<string, string>>({});
  const [queryHistory, setQueryHistory] = useState<string[]>([]);

  const queryTemplates: QueryTemplate[] = [
    {
      id: "ask_about",
      name: "Ask About Entity",
      command: "ask",
      description: "Ask a natural language question",
      parameters: ["question"]
    },
    {
      id: "what_is",
      name: "Entity Profile",
      command: "what_is",
      description: "Get detailed information about an entity",
      parameters: ["entity"]
    },
    {
      id: "add_fact",
      name: "Add Logical Fact",
      command: "add_raw",
      description: "Add a logical fact to the knowledge base",
      parameters: ["formula"]
    },
    {
      id: "search_kb",
      name: "Search Knowledge",
      command: "search",
      description: "Search for information in the knowledge base",
      parameters: ["query"]
    },
    {
      id: "wolfram_query",
      name: "Wolfram Calculation",
      command: "test_wolfram",
      description: "Perform calculation using Wolfram|Alpha",
      parameters: ["calculation"]
    },
    {
      id: "build_kb",
      name: "Index Document",
      command: "build_kb",
      description: "Add documents to the knowledge base",
      parameters: ["file_path"]
    }
  ];

  const logicalPredicates = [
    { name: "Ist", description: "Basic existence predicate" },
    { name: "Hat", description: "Possession relation" },
    { name: "Kann", description: "Capability predicate" },
    { name: "Funktioniert", description: "Functionality predicate" },
    { name: "Verbunden", description: "Connection relation" },
    { name: "Enthaelt", description: "Containment relation" },
    { name: "Groesser", description: "Comparison predicate" },
    { name: "Gleich", description: "Equality predicate" }
  ];

  const handleTemplateSelect = (templateId: string) => {
    const template = queryTemplates.find(t => t.id === templateId);
    if (template) {
      setSelectedTemplate(templateId);
      setParameters({});
      // Initialize parameters with empty values
      template.parameters.forEach(param => {
        setParameters(prev => ({ ...prev, [param]: "" }));
      });
    }
  };

  const buildQueryFromTemplate = () => {
    const template = queryTemplates.find(t => t.id === selectedTemplate);
    if (!template) return "";

    let query = template.command;
    template.parameters.forEach(param => {
      const value = parameters[param];
      if (value) {
        query += ` ${value}`;
      }
    });
    return query;
  };

  const executeQuery = () => {
    let finalQuery = "";
    
    if (queryType === "natural") {
      finalQuery = `ask ${queryText}`;
    } else if (queryType === "logical") {
      finalQuery = `add_raw ${logicalFormula}`;
    } else if (queryType === "template") {
      finalQuery = buildQueryFromTemplate();
    }
    
    if (finalQuery.trim()) {
      onExecuteQuery(finalQuery);
      setQueryHistory(prev => [finalQuery, ...prev.slice(0, 9)]); // Keep last 10
    }
  };

  const insertPredicate = (predicate: string) => {
    const currentPos = logicalFormula.length;
    const newFormula = logicalFormula + predicate + "(";
    setLogicalFormula(newFormula);
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          Advanced Query Builder
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs value={queryType} onValueChange={setQueryType}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="natural" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Natural
            </TabsTrigger>
            <TabsTrigger value="logical" className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              Logical
            </TabsTrigger>
            <TabsTrigger value="template" className="flex items-center gap-2">
              <Target className="h-4 w-4" />
              Template
            </TabsTrigger>
          </TabsList>

          {/* Natural Language Tab */}
          <TabsContent value="natural" className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Natural Language Query</label>
              <Textarea
                placeholder="Ask a question in natural language..."
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                className="min-h-[100px]"
              />
            </div>
            
            <Alert>
              <HelpCircle className="h-4 w-4" />
              <AlertDescription>
                Examples: "What is machine learning?", "How do neural networks work?", "Explain the capital of France"
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <label className="text-sm font-medium">Recent Natural Queries</label>
              <div className="flex flex-wrap gap-2">
                {["What is AI?", "How does RAG work?", "Explain transformers"].map((example) => (
                  <Badge 
                    key={example}
                    variant="outline" 
                    className="cursor-pointer hover:bg-accent"
                    onClick={() => setQueryText(example)}
                  >
                    {example}
                  </Badge>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Logical Formula Tab */}
          <TabsContent value="logical" className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Logical Formula</label>
              <Textarea
                placeholder="Enter logical formula (e.g., Ist(AI, Machine_Learning_System))"
                value={logicalFormula}
                onChange={(e) => setLogicalFormula(e.target.value)}
                className="min-h-[100px] font-mono"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Available Predicates</label>
              <div className="grid grid-cols-2 gap-2">
                {logicalPredicates.map((pred) => (
                  <Button
                    key={pred.name}
                    variant="outline"
                    size="sm"
                    className="justify-start text-left"
                    onClick={() => insertPredicate(pred.name)}
                  >
                    <Plus className="h-3 w-3 mr-2" />
                    {pred.name}
                  </Button>
                ))}
              </div>
            </div>

            <Alert>
              <Code className="h-4 w-4" />
              <AlertDescription>
                Use predicates like: Ist(X, Y), Hat(X, Y), Kann(X, Y). 
                Variables start with uppercase, constants with lowercase.
              </AlertDescription>
            </Alert>
          </TabsContent>

          {/* Template Tab */}
          <TabsContent value="template" className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Query Template</label>
              <Select value={selectedTemplate} onValueChange={handleTemplateSelect}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a query template" />
                </SelectTrigger>
                <SelectContent>
                  {queryTemplates.map((template) => (
                    <SelectItem key={template.id} value={template.id}>
                      <div>
                        <div className="font-medium">{template.name}</div>
                        <div className="text-xs text-gray-600">{template.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedTemplate && (
              <div className="space-y-3">
                <h4 className="text-sm font-medium">Parameters</h4>
                {queryTemplates
                  .find(t => t.id === selectedTemplate)
                  ?.parameters.map((param) => (
                    <div key={param} className="space-y-1">
                      <label className="text-xs font-medium capitalize">
                        {param.replace('_', ' ')}
                      </label>
                      <Input
                        placeholder={`Enter ${param}...`}
                        value={parameters[param] || ""}
                        onChange={(e) => 
                          setParameters(prev => ({ ...prev, [param]: e.target.value }))
                        }
                      />
                    </div>
                  ))}
                
                <div className="p-3 bg-muted rounded-lg">
                  <label className="text-xs font-medium">Generated Query:</label>
                  <code className="block mt-1 text-sm">{buildQueryFromTemplate()}</code>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Execute Button */}
        <div className="flex gap-2">
          <Button 
            onClick={executeQuery} 
            className="flex-1"
            disabled={
              (queryType === "natural" && !queryText.trim()) ||
              (queryType === "logical" && !logicalFormula.trim()) ||
              (queryType === "template" && !selectedTemplate)
            }
          >
            <Play className="h-4 w-4 mr-2" />
            Execute Query
          </Button>
          <Button variant="outline" onClick={() => {
            setQueryText("");
            setLogicalFormula("");
            setSelectedTemplate("");
            setParameters({});
          }}>
            Clear
          </Button>
        </div>

        {/* Query History */}
        {queryHistory.length > 0 && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Recent Queries</label>
            <ScrollArea className="h-32 border rounded-lg p-2">
              <div className="space-y-1">
                {queryHistory.map((query, index) => (
                  <div
                    key={index}
                    className="text-xs p-2 bg-muted rounded cursor-pointer hover:bg-accent"
                    onClick={() => {
                      if (query.startsWith("ask ")) {
                        setQueryType("natural");
                        setQueryText(query.slice(4));
                      } else if (query.startsWith("add_raw ")) {
                        setQueryType("logical");
                        setLogicalFormula(query.slice(8));
                      }
                    }}
                  >
                    <code>{query}</code>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AdvancedQueryBuilder;
