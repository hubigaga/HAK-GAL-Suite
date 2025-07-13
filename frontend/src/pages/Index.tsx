// Index.tsx - Korrigierte Version mit Wolfram Status
import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  Trash2, Send, Upload, Loader2, Sun, Moon, 
  Brain, Database, MessageSquare, FileText,
  Settings, Activity, Cpu, CheckCircle, XCircle,
  Eye, EyeOff, Copy, BookOpen, Lightbulb, ArrowRight,
  Filter, RefreshCw, Plus, Minus
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import { useTheme } from "@/hooks/useTheme";
import OrchestratorDashboard from "@/components/orchestrator/OrchestratorDashboard";
import AdvancedQueryBuilder from "@/components/query/AdvancedQueryBuilder";

type Message = {
  type: "user" | "system";
  content: string;
  timestamp?: string;
  facts?: ExtractedFact[];
  rawResponse?: string;
};

type ExtractedFact = {
  id: string;
  content: string;
  confidence: 'high' | 'medium' | 'low';
  category: 'rule' | 'fact' | 'relationship' | 'property';
  selected: boolean;
  source: string;
};

type LearningItem = {
  content: string;
  selected: boolean;
  source: 'suggestion' | 'manual' | 'extracted';
};

const Index = () => {
  const { theme, themeName, toggleTheme } = useTheme();
  
  const [inputMessage, setInputMessage] = useState("");
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  const [activeTab, setActiveTab] = useState("rag");
  const [profileEntity, setProfileEntity] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const [permanentKnowledge, setPermanentKnowledge] = useState<string[]>([]);
  const [learningSuggestions, setLearningSuggestions] = useState<string[]>([]);
  const [dataSources, setDataSources] = useState<string[]>([]);
  const [ragContext, setRagContext] = useState("No context loaded yet.");
  const [llmStatus, setLlmStatus] = useState<{llm_count: number, llm_active: number, llm_providers: any[]}>({llm_count: 0, llm_active: 0, llm_providers: []});
  
  // Human-in-the-Loop Learning States
  const [selectedFacts, setSelectedFacts] = useState<Set<string>>(new Set());
  const [showFactExtraction, setShowFactExtraction] = useState(true);
  const [factFilter, setFactFilter] = useState<'all' | 'selected' | 'unselected'>('all');
  const [learningItems, setLearningItems] = useState<LearningItem[]>([]);
  const [showFullResponses, setShowFullResponses] = useState(false);
  
  // NEUE: Wolfram Status State
  const [wolframLoaded, setWolframLoaded] = useState<boolean>(false);
  
  const conversationEndRef = useRef<null | HTMLDivElement>(null);

  // === FACT EXTRACTION UTILITIES ===
  const extractFactsFromResponse = (response: string): ExtractedFact[] => {
    const facts: ExtractedFact[] = [];
    
    // Pattern matching für verschiedene Fakttypen
    const patterns = [
      // Logische Regeln: Wenn X, dann Y
      { regex: /(?:Wenn|If)\s+(.+?)\s*,\s*(?:dann|then)\s+(.+?)\./gi, category: 'rule' as const },
      // Fakten: X ist Y
      { regex: /(\w+)\s+(?:ist|is)\s+(.+?)\./gi, category: 'fact' as const },
      // Beziehungen: X hat Y, X gehört zu Y
      { regex: /(\w+)\s+(?:hat|gehört zu|belongs to|has)\s+(.+?)\./gi, category: 'relationship' as const },
      // Eigenschaften: X kann Y, X verfügt über Y
      { regex: /(\w+)\s+(?:kann|verfügt über|can|has the ability to)\s+(.+?)\./gi, category: 'property' as const }
    ];
    
    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.regex.exec(response)) !== null) {
        const fullMatch = match[0];
        const confidence = fullMatch.length > 50 ? 'high' : fullMatch.length > 20 ? 'medium' : 'low';
        
        facts.push({
          id: `fact_${Date.now()}_${facts.length}`,
          content: fullMatch.trim(),
          confidence,
          category: pattern.category,
          selected: false,
          source: 'llm_response'
        });
      }
    });
    
    return facts;
  };
  
  const toggleFactSelection = (factId: string) => {
    setSelectedFacts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(factId)) {
        newSet.delete(factId);
      } else {
        newSet.add(factId);
      }
      return newSet;
    });
  };
  
  const learnSelectedFacts = async () => {
    const selectedFactsArray = conversationHistory
      .flatMap(msg => msg.facts || [])
      .filter(fact => selectedFacts.has(fact.id));
    
    for (const fact of selectedFactsArray) {
      try {
        await sendCommandToBackend(`add_raw ${fact.content}`);
        console.log(`✅ Learned fact: ${fact.content}`);
      } catch (error) {
        console.error(`❌ Failed to learn fact: ${fact.content}`, error);
      }
    }
    
    // Clear selections after learning
    setSelectedFacts(new Set());
  };
  
  const learnSingleFact = async (fact: ExtractedFact) => {
    try {
      await sendCommandToBackend(`add_raw ${fact.content}`);
      console.log(`✅ Learned single fact: ${fact.content}`);
    } catch (error) {
      console.error(`❌ Failed to learn fact: ${fact.content}`, error);
    }
  };

  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversationHistory]);

  // Initial check für Wolfram Status
  useEffect(() => {
    checkWolframStatus();
  }, []);

  const checkWolframStatus = async () => {
    try {
      const response = await fetch("http://localhost:5001/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: "status" }),
      });

      if (response.ok) {
        const data = await response.json();
        // Prüfe ob Wolfram in der chatResponse erwähnt wird
        if (data.chatResponse && data.chatResponse.includes("Wolfram|Alpha Orakel")) {
          setWolframLoaded(true);
          console.log("✅ Wolfram detected in prover list");
        }
      }
    } catch (error) {
      console.error("Failed to check Wolfram status:", error);
    }
  };

  // DEBUG: Log State-Änderungen
  useEffect(() => {
    console.log("🔄 State Update - Conversations:", conversationHistory.length);
    console.log("🔄 State Update - Knowledge:", permanentKnowledge.length);
    console.log("🔄 State Update - Suggestions:", learningSuggestions.length);
  }, [conversationHistory, permanentKnowledge, learningSuggestions]);

  const sendCommandToBackend = async (commandString: string) => {
    console.log("📤 Frontend sendet Command:", commandString);
    
    if (!commandString.trim() || isLoading) return;

    setIsLoading(true);
    setConversationHistory(prev => {
      const newHistory = [...prev, { type: "user", content: commandString }];
      console.log("✅ User Message hinzugefügt. Neue Länge:", newHistory.length);
      return newHistory;
    });
    setInputMessage("");

    if (commandString.toLowerCase().startsWith("what_is ")) {
        const entity = commandString.slice(8).trim();
        setProfileEntity(entity);
        setActiveTab("profile");
    } else {
        setActiveTab("rag");
    }

    try {
      console.log("🌐 Sende API Request...");
      const response = await fetch("http://localhost:5001/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: commandString }),
      });

      console.log("📨 Response erhalten. Status:", response.status);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("✅ API Response Data:", {
        status: data.status,
        hasChat: !!data.chatResponse,
        chatLength: data.chatResponse?.length || 0,
        knowledgeCount: data.permanentKnowledge?.length || 0,
        suggestionsCount: data.learningSuggestions?.length || 0,
        ragContextLength: data.ragContext?.length || 0,
        dataSourcesCount: data.dataSources?.length || 0
      });
      
      // DETAIL-DEBUGGING
      console.log("🔍 DETAILED API Response:", {
        permanentKnowledge: data.permanentKnowledge,
        learningSuggestions: data.learningSuggestions,
        ragContext: data.ragContext?.substring(0, 200) + "...",
        dataSources: data.dataSources
      });

      if (data.status === "success") {
        // WOLFRAM CHECK: Prüfe ob Wolfram in Response erwähnt wird
        if (data.chatResponse && (
          data.chatResponse.includes("Wolfram|Alpha Orakel") ||
          data.chatResponse.includes("Wolfram") ||
          data.chatResponse.includes("wolfram_stats")
        )) {
          setWolframLoaded(true);
        }
        
        console.log("🔄 Updating permanentKnowledge...");
        const newKnowledge = Array.isArray(data.permanentKnowledge) ? data.permanentKnowledge : [];
        setPermanentKnowledge(newKnowledge);
        console.log("✅ Knowledge updated:", newKnowledge.length, "items");

        console.log("🔄 Updating learningSuggestions...");
        const newSuggestions = Array.isArray(data.learningSuggestions) ? data.learningSuggestions : [];
        setLearningSuggestions(newSuggestions);
        console.log("✅ Suggestions updated:", newSuggestions.length, "items");
        
        // Update RAG Context und Data Sources
        if (data.ragContext) {
          console.log("🔄 Updating RAG Context...");
          setRagContext(data.ragContext);
          console.log("✅ RAG Context updated:", data.ragContext.length, "characters");
        }
        
        if (data.dataSources) {
          console.log("🔄 Updating Data Sources...");
          setDataSources(data.dataSources);
          console.log("✅ Data Sources updated:", data.dataSources.length, "items");
        }
        
        // Update LLM Status
        if (data.llmStatus) {
          console.log("🔄 Updating LLM Status...");
          setLlmStatus(data.llmStatus);
          console.log("✅ LLM Status updated:", data.llmStatus.llm_active + "/" + data.llmStatus.llm_count, "active");
        }
        
        // EXPLIZITE Learning Suggestions Check
        if (data.learningSuggestions && Array.isArray(data.learningSuggestions) && data.learningSuggestions.length > 0) {
          console.log("🔥 LEARNING SUGGESTIONS DETECTED:", data.learningSuggestions);
        } else {
          console.log("⚠️ Learning Suggestions empty or invalid:", data.learningSuggestions);
        }
        
        if (data.chatResponse) {
          console.log("💬 Adding system message. Content length:", data.chatResponse.length);
          
          // Extract facts from LLM response
          const extractedFacts = extractFactsFromResponse(data.chatResponse);
          
          setConversationHistory(prev => {
            const newMessage: Message = {
              type: "system", 
              content: data.chatResponse,
              facts: extractedFacts,
              rawResponse: data.chatResponse,
              timestamp: new Date().toISOString()
            };
            const newHistory = [...prev, newMessage];
            console.log("✅ System Message hinzugefügt. Neue Länge:", newHistory.length);
            console.log(`🧠 Extracted ${extractedFacts.length} facts from response`);
            return newHistory;
          });
        } else {
          console.log("⚠️ Keine chatResponse erhalten, verwende Fallback");
          setConversationHistory(prev => {
            const fallbackMessage = `✅ Command '${commandString}' executed successfully.`;
            const newHistory = [...prev, { type: "system", content: fallbackMessage }];
            console.log("✅ Fallback Message hinzugefügt. Neue Länge:", newHistory.length);
            return newHistory;
          });
        }
      } else {
        throw new Error(data.message || "An unknown error occurred.");
      }

    } catch (error) {
      console.error("💥 API call failed:", error);
      const errorResponse: Message = {
        type: "system",
        content: `🚨 Error: ${error.message}`,
        timestamp: new Date().toISOString()
      };
      setConversationHistory(prev => {
        const newHistory = [...prev, errorResponse];
        console.log("❌ Error Message hinzugefügt. Neue Länge:", newHistory.length);
        return newHistory;
      });
    } finally {
      setIsLoading(false);
      console.log("🏁 Command processing completed");
    }
  };

  const handleSendMessage = () => {
    console.log("🎯 handleSendMessage called with:", inputMessage);
    sendCommandToBackend(inputMessage);
  };
  
  const handleLearnAll = () => {
    console.log("🎯 handleLearnAll called");
    sendCommandToBackend("learn");
  };
  
  const handleRetractItem = (item: string) => {
    console.log("🎯 handleRetractItem called with:", item);
    sendCommandToBackend(`retract ${item}`);
  };
  
  const handleUploadDocument = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt,.pdf,.md';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        console.log("📄 File selected:", file.name);
        // Simuliere Upload - in echter Implementierung würde hier ein File-Upload API-Call stehen
        sendCommandToBackend(`build_kb ${file.name}`);
      }
    };
    input.click();
  };

  return (
    <div 
      className="h-screen flex flex-col transition-colors duration-200"
      style={{ 
        backgroundColor: theme.colors.background,
        color: theme.colors.text 
      }}
    >
      {/* Header mit Theme Toggle - FIXED */}
      <div 
        className="flex-shrink-0 border-b px-6 py-4 flex items-center justify-between"
        style={{ 
          borderColor: theme.colors.border,
          backgroundColor: theme.colors.surface 
        }}
      >
        <div className="flex items-center gap-3">
          <Brain className="h-8 w-8" style={{ color: theme.colors.primary }} />
          <div>
            <h1 className="text-2xl font-bold" style={{ color: theme.colors.text }}>HAK-GAL Suite</h1>
            <p className="text-sm" style={{ color: theme.colors.textMuted }}>
              Hybrid AI Framework für verifizierbares Wissen
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <Badge variant="outline" className="flex items-center gap-1">
            <Activity className="h-3 w-3" />
            KB: {permanentKnowledge.length}
          </Badge>
          <Badge variant="outline" className="flex items-center gap-1">
            <Database className="h-3 w-3" />
            Docs: {dataSources.length}
          </Badge>
          {/* NEUE LLM-Status-Anzeige */}
          <Badge 
            variant={llmStatus.llm_active > 0 ? "default" : "destructive"} 
            className="flex items-center gap-1"
          >
            🤖 LLM: {llmStatus.llm_active}/{llmStatus.llm_count}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={toggleTheme}
            className="flex items-center gap-2"
          >
            {themeName === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
            {themeName === 'light' ? 'Dark' : 'Light'}
          </Button>
        </div>
      </div>

      {/* Debug Panel - FIXED mit Wolfram Status */}
      <div 
        className="flex-shrink-0 border-b px-4 py-2 text-xs"
        style={{ 
          backgroundColor: theme.colors.warning + '20',
          borderColor: theme.colors.warning + '30',
          color: theme.colors.textSecondary
        }}
      >
        🔧 DEBUG: Messages: {conversationHistory.length} | Knowledge: {permanentKnowledge.length} | Suggestions: {learningSuggestions.length} | Docs: {dataSources.length} | RAG: {ragContext.length > 50 ? "loaded" : "empty"} | Wolfram: {wolframLoaded ? "YES" : "NO"} | Selected Facts: {selectedFacts.size}
        <button 
          onClick={() => console.log("Current State:", { 
            conversationHistory: conversationHistory.length, 
            permanentKnowledge, 
            learningSuggestions, 
            dataSources, 
            ragContext: ragContext.substring(0, 100) + "...",
            selectedFacts: Array.from(selectedFacts),
            extractedFactsTotal: conversationHistory.reduce((sum, msg) => sum + (msg.facts?.length || 0), 0)
          })}
          className="ml-2 px-2 py-1 rounded hover:opacity-80"
          style={{ backgroundColor: theme.colors.warning + '20' }}
        >
          Log State
        </button>
        <button 
          onClick={() => sendCommandToBackend("status")}
          className="ml-2 px-2 py-1 rounded hover:opacity-80"
          style={{ backgroundColor: theme.colors.primary + '20' }}
        >
          Refresh
        </button>
        <button 
          onClick={() => sendCommandToBackend("help")}
          className="ml-2 px-2 py-1 rounded hover:opacity-80"
          style={{ backgroundColor: theme.colors.success + '20' }}
        >
          Test Commands
        </button>
        <button 
          onClick={() => sendCommandToBackend("wolfram_stats")}
          className="ml-2 px-2 py-1 rounded hover:opacity-80"
          style={{ backgroundColor: theme.colors.accent + '20' }}
        >
          Wolfram Check
        </button>
      </div>
      
      {/* KRITISCHE LAYOUT-REPARATUR: Flexbox statt Grid */}
      <div className="flex-1 flex flex-col lg:flex-row gap-6 p-6 overflow-hidden">
        
        {/* Knowledge Base Panel - 1/3 WIDTH, FULL HEIGHT */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Card 
            className="flex flex-col border h-full"
            style={{ 
              backgroundColor: theme.colors.surface,
              borderColor: theme.colors.border
            }}
          >
          <CardHeader className="pb-4 flex-shrink-0">
            <CardTitle className="flex items-center gap-2" style={{ color: theme.colors.text }}>
              <Database className="h-5 w-5" style={{ color: theme.colors.primary }} />
              Knowledge Base
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col space-y-4 overflow-hidden min-h-0">
            
            {/* Permanent Knowledge - SCROLLABLE */}
            <div className="flex-1 flex flex-col min-h-0">
              <div className="flex items-center justify-between mb-3 flex-shrink-0">
                <h3 className="text-sm font-medium" style={{ color: theme.colors.textSecondary }}>
                  Permanent Knowledge
                </h3>
                <Badge variant="secondary">{permanentKnowledge.length}</Badge>
              </div>
              <ScrollArea 
                className="flex-1 rounded-lg border p-3 min-h-0"
                style={{ 
                  borderColor: theme.colors.border,
                  backgroundColor: theme.colors.background
                }}
              >
                {permanentKnowledge.length > 0 ? (
                  <div className="space-y-2">
                    {permanentKnowledge.map((item, index) => (
                      <div 
                        key={`perm-${index}`} 
                        className="flex items-center justify-between text-sm p-3 rounded-lg border group hover:shadow-sm transition-all"
                        style={{ 
                          backgroundColor: theme.colors.surface,
                          borderColor: theme.colors.border
                        }}
                      >
                        <span className="flex-1 font-mono text-xs" style={{ color: theme.colors.text }}>
                          {String(item)}
                        </span>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleRetractItem(String(item))} 
                          className="ml-2 h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                          style={{ color: theme.colors.error }}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-center p-8" style={{ color: theme.colors.textMuted }}>
                    No permanent knowledge yet.
                  </p>
                )}
              </ScrollArea>
            </div>
            
            <Separator style={{ backgroundColor: theme.colors.border }} className="flex-shrink-0" />
            
            {/* Learning Suggestions - SCROLLABLE */}
            <div className="flex-1 flex flex-col min-h-0">
              <div className="flex items-center justify-between mb-3 flex-shrink-0">
                <h3 className="text-sm font-medium" style={{ color: theme.colors.textSecondary }}>
                  Learning Suggestions
                </h3>
                <Badge variant="secondary">{learningSuggestions.length}</Badge>
              </div>
              <ScrollArea 
                className="flex-1 rounded-lg border p-3 min-h-0"
                style={{ 
                  borderColor: theme.colors.border,
                  backgroundColor: theme.colors.background
                }}
              >
                {learningSuggestions.length > 0 ? (
                  <div className="space-y-2">
                    {learningSuggestions.map((item, index) => (
                      <div 
                        key={`learn-${index}`} 
                        className="text-sm p-3 rounded-lg border"
                        style={{ 
                          backgroundColor: theme.colors.surface,
                          borderColor: theme.colors.border
                        }}
                      >
                        <span className="font-mono text-xs" style={{ color: theme.colors.text }}>
                          {String(item)}
                        </span>
                      </div>
                    ))}
                    <Button 
                      className="w-full mt-3"
                      onClick={handleLearnAll}
                      style={{ 
                        backgroundColor: theme.colors.success,
                        color: 'white'
                      }}
                    >
                      Learn All Suggestions
                    </Button>
                  </div>
                ) : (
                  <p className="text-xs text-center p-8" style={{ color: theme.colors.textMuted }}>
                    No new facts to learn.
                  </p>
                )}
              </ScrollArea>
            </div>
            
            <Separator style={{ backgroundColor: theme.colors.border }} className="flex-shrink-0" />
            
            {/* Data Sources - FIXED HEIGHT */}
            <div className="flex-shrink-0">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium" style={{ color: theme.colors.textSecondary }}>
                  Data Sources
                </h3>
                <Badge variant="secondary">{dataSources.length}</Badge>
              </div>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {dataSources.map((file, index) => (
                  <div 
                    key={index} 
                    className="text-xs p-2 rounded border flex items-center gap-2"
                    style={{ 
                      backgroundColor: theme.colors.surface,
                      borderColor: theme.colors.border
                    }}
                  >
                    <FileText className="h-3 w-3" style={{ color: theme.colors.accent }} />
                    <span style={{ color: theme.colors.text }}>{file}</span>
                  </div>
                ))}
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  style={{ borderColor: theme.colors.border }}
                  onClick={handleUploadDocument}
                >
                  <Upload className="h-3 w-3 mr-2" />
                  Upload Document
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
        </div>

        {/* Interaction Panel - 1/3 WIDTH, FULL HEIGHT */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Card 
            className="flex flex-col border h-full"
            style={{ 
              backgroundColor: theme.colors.surface,
              borderColor: theme.colors.border
            }}
          >
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2" style={{ color: theme.colors.text }}>
                <MessageSquare className="h-5 w-5" style={{ color: theme.colors.primary }} />
                Interaction Panel
              </CardTitle>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFullResponses(!showFullResponses)}
                  className="flex items-center gap-1"
                >
                  {showFullResponses ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                  {showFullResponses ? 'Compact' : 'Full'}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFactExtraction(!showFactExtraction)}
                  className="flex items-center gap-1"
                >
                  <Brain className="h-3 w-3" />
                  Facts
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col overflow-hidden">
            {/* Learning Controls */}
            {showFactExtraction && selectedFacts.size > 0 && (
              <div className="mb-4 p-3 rounded-lg border" style={{ 
                backgroundColor: theme.colors.warning + '20',
                borderColor: theme.colors.warning + '40'
              }}>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium" style={{ color: theme.colors.text }}>
                    {selectedFacts.size} facts selected for learning
                  </span>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => setSelectedFacts(new Set())}
                      variant="outline"
                    >
                      <XCircle className="h-3 w-3 mr-1" />
                      Clear
                    </Button>
                    <Button
                      size="sm"
                      onClick={learnSelectedFacts}
                      style={{ backgroundColor: theme.colors.success, color: 'white' }}
                    >
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Learn Selected
                    </Button>
                  </div>
                </div>
              </div>
            )}
            
            <ScrollArea className="flex-1 mb-4 pr-4">
              <div className="space-y-4">
                {conversationHistory.map((message, index) => (
                  <div key={`msg-${index}-${message.timestamp}`}>
                    {/* Main Message */}
                    <div 
                      className={`p-4 rounded-lg border transition-all ${
                        message.type === 'user' 
                          ? 'ml-8' 
                          : 'mr-8'
                      }`}
                      style={{ 
                        backgroundColor: message.type === 'user' 
                          ? theme.colors.primary + '10'
                          : theme.colors.surface,
                        borderColor: message.type === 'user'
                          ? theme.colors.primary + '40'
                          : theme.colors.border
                      }}
                    >
                      <div className="flex items-start gap-3">
                        <span className="mt-1 text-lg">
                          {message.type === 'user' ? '👤' : '🤖'}
                        </span>
                        <div className="flex-1">
                          <div 
                            className="font-sans text-sm leading-relaxed overflow-x-auto"
                            style={{ 
                              color: theme.colors.text,
                              whiteSpace: showFullResponses ? 'pre-wrap' : 'normal',
                              wordBreak: 'break-word',
                              maxWidth: '100%',
                              maxHeight: showFullResponses ? 'none' : '200px',
                              overflow: showFullResponses ? 'visible' : 'hidden'
                            }}
                          >
                            {showFullResponses 
                              ? message.content 
                              : message.content.substring(0, 300) + (message.content.length > 300 ? '...' : '')
                            }
                          </div>
                          {message.timestamp && (
                            <div className="text-xs mt-2" style={{ color: theme.colors.textMuted }}>
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    {/* Extracted Facts Panel */}
                    {showFactExtraction && message.facts && message.facts.length > 0 && (
                      <div className="mt-2 mr-8 ml-12">
                        <div 
                          className="p-3 rounded-lg border"
                          style={{
                            backgroundColor: theme.colors.accent + '10',
                            borderColor: theme.colors.accent + '30'
                          }}
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <Lightbulb className="h-4 w-4" style={{ color: theme.colors.accent }} />
                            <span className="text-xs font-medium" style={{ color: theme.colors.textSecondary }}>
                              Extracted Facts ({message.facts.length})
                            </span>
                          </div>
                          <div className="space-y-2">
                            {message.facts.map((fact) => (
                              <div 
                                key={fact.id}
                                className="flex items-start gap-2 p-2 rounded border"
                                style={{
                                  backgroundColor: selectedFacts.has(fact.id) 
                                    ? theme.colors.success + '20' 
                                    : theme.colors.background,
                                  borderColor: selectedFacts.has(fact.id)
                                    ? theme.colors.success + '40'
                                    : theme.colors.border
                                }}
                              >
                                <Checkbox
                                  checked={selectedFacts.has(fact.id)}
                                  onCheckedChange={() => toggleFactSelection(fact.id)}
                                  className="mt-0.5"
                                />
                                <div className="flex-1 min-w-0">
                                  <div className="text-xs font-mono" style={{ color: theme.colors.text }}>
                                    {fact.content}
                                  </div>
                                  <div className="flex items-center gap-2 mt-1">
                                    <Badge 
                                      variant="outline" 
                                      className="text-xs px-1 py-0"
                                      style={{
                                        borderColor: fact.confidence === 'high' 
                                          ? theme.colors.success 
                                          : fact.confidence === 'medium' 
                                          ? theme.colors.warning 
                                          : theme.colors.error
                                      }}
                                    >
                                      {fact.confidence}
                                    </Badge>
                                    <Badge variant="outline" className="text-xs px-1 py-0">
                                      {fact.category}
                                    </Badge>
                                  </div>
                                </div>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => learnSingleFact(fact)}
                                  className="h-6 w-6 p-0"
                                  title="Learn this fact immediately"
                                >
                                  <Plus className="h-3 w-3" />
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-center items-center p-8">
                    <Loader2 className="h-6 w-6 animate-spin mr-2" style={{ color: theme.colors.primary }} />
                    <span className="text-sm" style={{ color: theme.colors.textMuted }}>Processing...</span>
                  </div>
                )}
                <div ref={conversationEndRef} />
              </div>
            </ScrollArea>
            
            <div 
              className="flex gap-3 pt-4 border-t"
              style={{ borderColor: theme.colors.border }}
            >
              <Input 
                value={inputMessage} 
                onChange={(e) => setInputMessage(e.target.value)} 
                placeholder="Enter command or ask a question..." 
                onKeyPress={(e) => e.key === "Enter" && !isLoading && handleSendMessage()} 
                className="flex-1"
                disabled={isLoading}
                style={{
                  backgroundColor: theme.colors.background,
                  borderColor: theme.colors.border,
                  color: theme.colors.text
                }}
              />
              <Button 
                onClick={handleSendMessage} 
                disabled={isLoading || !inputMessage.trim()} 
                style={{ 
                  backgroundColor: theme.colors.primary,
                  color: 'white'
                }}
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
        </div>

        {/* Advanced Control Panel - TAB SYSTEM */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Card 
            className="flex flex-col border h-full"
            style={{ 
              backgroundColor: theme.colors.surface,
              borderColor: theme.colors.border
            }}
          >
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2" style={{ color: theme.colors.text }}>
              <Settings className="h-5 w-5" style={{ color: theme.colors.primary }} />
              Advanced Control Panel
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-hidden">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
              <TabsList className="grid w-full grid-cols-4 mb-4">
                <TabsTrigger 
                  value="rag" 
                  className="flex items-center gap-2"
                >
                  <FileText className="h-4 w-4" />
                  RAG Context
                </TabsTrigger>
                <TabsTrigger 
                  value="orchestrator" 
                  className="flex items-center gap-2"
                >
                  <Cpu className="h-4 w-4" />
                  Orchestrator
                </TabsTrigger>
                <TabsTrigger 
                  value="query" 
                  className="flex items-center gap-2"
                >
                  <Settings className="h-4 w-4" />
                  Query Builder
                </TabsTrigger>
                <TabsTrigger 
                  value="profile" 
                  className="flex items-center gap-2"
                >
                  <Brain className="h-4 w-4" />
                  Profile
                </TabsTrigger>
              </TabsList>
              
              {/* RAG Context Tab */}
              <TabsContent value="rag" className="flex-1 overflow-hidden">
                <ScrollArea 
                  className="h-full rounded-lg border p-4"
                  style={{ 
                    borderColor: theme.colors.border,
                    backgroundColor: theme.colors.background
                  }}
                >
                  <div 
                    className="text-sm font-mono leading-relaxed overflow-x-auto"
                    style={{ 
                      color: theme.colors.textSecondary,
                      whiteSpace: 'pre',
                      wordBreak: 'break-all',
                      minWidth: 'max-content'
                    }}
                  >
                    {ragContext}
                  </div>
                </ScrollArea>
              </TabsContent>
              
              {/* Orchestrator Dashboard Tab */}
              <TabsContent value="orchestrator" className="flex-1 overflow-hidden">
                <div className="h-full overflow-auto">
                  <OrchestratorDashboard />
                </div>
              </TabsContent>
              
              {/* Advanced Query Builder Tab */}
              <TabsContent value="query" className="flex-1 overflow-hidden">
                <div className="h-full overflow-auto">
                  <AdvancedQueryBuilder onExecuteQuery={(query) => sendCommandToBackend(query)} />
                </div>
              </TabsContent>
              
              {/* Profile Tab */}
              <TabsContent value="profile" className="flex-1 overflow-hidden">
                <div className="space-y-6 h-full overflow-auto">
                  <div>
                    <h3 className="text-sm font-medium mb-3" style={{ color: theme.colors.textSecondary }}>
                      Entity: {profileEntity || "None selected"}
                    </h3>
                    <div 
                      className="p-4 rounded-lg border"
                      style={{ 
                        backgroundColor: theme.colors.background,
                        borderColor: theme.colors.border
                      }}
                    >
                      <span className="text-sm" style={{ color: theme.colors.textMuted }}>
                        Use "what_is EntityName" to analyze entities.
                      </span>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium mb-3" style={{ color: theme.colors.textSecondary }}>
                      Explicit Facts
                    </h3>
                    <div 
                      className="p-4 rounded-lg border"
                      style={{ 
                        backgroundColor: theme.colors.background,
                        borderColor: theme.colors.border
                      }}
                    >
                      <span className="text-sm" style={{ color: theme.colors.textMuted }}>
                        Facts will appear here after analysis.
                      </span>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium mb-3" style={{ color: theme.colors.textSecondary }}>
                      Derived Properties
                    </h3>
                    <div 
                      className="p-4 rounded-lg border"
                      style={{ 
                        backgroundColor: theme.colors.background,
                        borderColor: theme.colors.border
                      }}
                    >
                      <span className="text-sm" style={{ color: theme.colors.textMuted }}>
                        Derived properties will appear here.
                      </span>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
        </div>
      </div>
    </div>
  );
};

export default Index;
