// Optimized Index.tsx with reduced polling
import React, { useState, useEffect } from 'react';
import { useOptimizedPolling, trackUserActivity } from './frontend_polling_optimization';

const Index = () => {
  // ... existing state ...
  const [activeTab, setActiveTab] = useState("orchestrator");
  const [permanentKnowledge, setPermanentKnowledge] = useState([]);
  const [learningSuggestions, setLearningSuggestions] = useState([]);
  
  // OPTIMIZED: Reduzierte Backend-Calls mit intelligenten Intervallen
  const { pollNow: refreshOrchestrator } = useOptimizedPolling("orchestrator_dashboard", async () => {
    // Nur wenn Orchestrator-Tab aktiv ist
    if (activeTab === "orchestrator") {
      try {
        const response = await fetch("http://localhost:5001/api/command", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ command: "status" }),
        });
        
        if (response.ok) {
          const data = await response.json();
          // Update orchestrator state
        }
      } catch (error) {
        console.error("Orchestrator polling error:", error);
      }
    }
  }, [activeTab]);
  
  const { pollNow: refreshKnowledge } = useOptimizedPolling("knowledge_base_status", async () => {
    // Nur notwendige Updates für Knowledge Base
    try {
      const response = await fetch("http://localhost:5001/api/command", {
        method: "POST", 
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: "show" }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setPermanentKnowledge(data.permanentKnowledge || []);
        setLearningSuggestions(data.learningSuggestions || []);
      }
    } catch (error) {
      console.error("Knowledge base polling error:", error);
    }
  }, []);
  
  const { pollNow: refreshPerformance } = useOptimizedPolling("performance_metrics", async () => {
    // Performance-Metriken nur wenn Tab aktiv
    if (activeTab === "performance" || activeTab === "orchestrator") {
      try {
        const response = await fetch("http://localhost:5001/api/metrics", {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        });
        
        if (response.ok) {
          const metrics = await response.json();
          // Update performance state
        }
      } catch (error) {
        console.error("Performance metrics polling error:", error);
      }
    }
  }, [activeTab]);
  
  // OPTIMIZED: On-demand polling instead of continuous
  const sendCommandToBackend = async (commandString: string) => {
    // Track user activity for adaptive polling
    trackUserActivity("interaction_panel");
    
    try {
      const response = await fetch("http://localhost:5001/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: commandString }),
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Trigger immediate refresh only for relevant components
        if (commandString.startsWith("learn") || commandString.startsWith("add_raw")) {
          refreshKnowledge(); // Immediate KB refresh
        }
        
        if (commandString.startsWith("status") || commandString.startsWith("wolfram")) {
          refreshOrchestrator(); // Immediate orchestrator refresh
        }
        
        if (commandString.includes("performance") || commandString.includes("metrics")) {
          refreshPerformance(); // Immediate performance refresh
        }
        
        return result;
      }
    } catch (error) {
      console.error("Command error:", error);
      throw error;
    }
  };
  
  // OPTIMIZED: Manual tab switching triggers immediate update
  const handleTabChange = (newTab: string) => {
    setActiveTab(newTab);
    trackUserActivity(newTab);
    
    // Immediate refresh for newly activated tab
    if (newTab === "orchestrator") {
      refreshOrchestrator();
    } else if (newTab === "rag") {
      // RAG context refresh only when needed
      trackUserActivity("rag_context");
    } else if (newTab === "performance") {
      refreshPerformance();
    }
  };
  
  // OPTIMIZED: User interaction tracking
  const handleUserInteraction = (interactionType: string) => {
    trackUserActivity("user_interaction");
    
    // Boost polling for active components temporarily
    if (interactionType === "command_input") {
      trackUserActivity("orchestrator_dashboard");
    } else if (interactionType === "knowledge_edit") {
      trackUserActivity("knowledge_base_status");
    }
  };
  
  // OPTIMIZED: Reduced initial loading
  useEffect(() => {
    // Initial load only for default tab
    if (activeTab === "orchestrator") {
      refreshOrchestrator();
    }
    refreshKnowledge(); // Always needed for sidebar
  }, []); // Only on mount
  
  return (
    <div className="app-container">
      {/* Tab Navigation */}
      <div className="tab-navigation">
        {["orchestrator", "rag", "performance", "knowledge"].map(tab => (
          <button
            key={tab}
            className={`tab-button ${activeTab === tab ? 'active' : ''}`}
            onClick={() => handleTabChange(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>
      
      {/* Main Content */}
      <div className="main-content">
        {activeTab === "orchestrator" && (
          <div className="orchestrator-panel">
            <div className="command-input">
              <input
                type="text"
                placeholder="Enter command..."
                onFocus={() => handleUserInteraction("command_input")}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    const command = e.target.value;
                    sendCommandToBackend(command);
                    e.target.value = '';
                  }
                }}
              />
            </div>
            {/* Orchestrator status display */}
          </div>
        )}
        
        {activeTab === "rag" && (
          <div className="rag-panel">
            {/* RAG context display */}
          </div>
        )}
        
        {activeTab === "performance" && (
          <div className="performance-panel">
            {/* Performance metrics display */}
          </div>
        )}
        
        {activeTab === "knowledge" && (
          <div className="knowledge-panel">
            <div className="knowledge-editor">
              <textarea
                placeholder="Edit knowledge..."
                onFocus={() => handleUserInteraction("knowledge_edit")}
                onChange={() => trackUserActivity("knowledge_base_status")}
              />
            </div>
            
            <div className="permanent-knowledge">
              <h3>Permanent Knowledge</h3>
              {permanentKnowledge.map((item, index) => (
                <div key={index} className="knowledge-item">
                  {item}
                </div>
              ))}
            </div>
            
            <div className="learning-suggestions">
              <h3>Learning Suggestions</h3>
              {learningSuggestions.map((suggestion, index) => (
                <div key={index} className="suggestion-item">
                  {suggestion}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Index;
