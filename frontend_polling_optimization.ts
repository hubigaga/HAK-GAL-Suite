// Frontend Polling Optimization
// Schritt 3.1: Reduzierte und intelligente Backend-Kommunikation

interface PollingConfig {
  interval_ms: number;
  enabled: boolean;
  adaptive: boolean;
}

interface PollingManager {
  activeIntervals: Map<string, NodeJS.Timeout>;
  lastPollTimes: Map<string, number>;
  activityLevels: Map<string, number>;
}

class OptimizedPollingManager implements PollingManager {
  activeIntervals = new Map<string, NodeJS.Timeout>();
  lastPollTimes = new Map<string, number>();
  activityLevels = new Map<string, number>();
  
  private config: Record<string, PollingConfig> = {
    orchestrator_dashboard: {
      interval_ms: 5000,  // 5s statt kontinuierlich
      enabled: true,
      adaptive: true
    },
    knowledge_base_status: {
      interval_ms: 10000, // 10s für KB Updates
      enabled: true,
      adaptive: false
    },
    performance_metrics: {
      interval_ms: 3000,  // 3s für Performance
      enabled: true,
      adaptive: true
    },
    rag_context: {
      interval_ms: 15000, // 15s für RAG Context
      enabled: true,
      adaptive: false
    }
  };
  
  startOptimizedPolling(component: string, pollFunction: () => Promise<void>) {
    this.stopPolling(component); // Clear existing
    
    const config = this.config[component];
    if (!config?.enabled) return;
    
    const poll = async () => {
      const now = Date.now();
      const lastPoll = this.lastPollTimes.get(component) || 0;
      
      if (this.shouldPoll(component, lastPoll, now)) {
        try {
          await pollFunction();
          this.lastPollTimes.set(component, now);
          
          // Track successful activity
          const activity = this.activityLevels.get(component) || 0;
          this.activityLevels.set(component, Math.min(activity + 1, 5));
          
        } catch (error) {
          console.error(`Polling error for ${component}:`, error);
          
          // Reduce activity on errors
          const activity = this.activityLevels.get(component) || 0;
          this.activityLevels.set(component, Math.max(activity - 1, 0));
        }
      }
      
      // Schedule next poll with adaptive interval
      const nextInterval = this.calculateAdaptiveInterval(component);
      const timeoutId = setTimeout(poll, nextInterval);
      this.activeIntervals.set(component, timeoutId);
    };
    
    // Start immediately
    poll();
  }
  
  private shouldPoll(component: string, lastPoll: number, now: number): boolean {
    const config = this.config[component];
    if (!config) return false;
    
    let interval = config.interval_ms;
    
    if (config.adaptive) {
      const activity = this.activityLevels.get(component) || 0;
      interval = this.calculateAdaptiveInterval(component, activity);
    }
    
    return (now - lastPoll) >= interval;
  }
  
  private calculateAdaptiveInterval(component: string, activityLevel?: number): number {
    const config = this.config[component];
    if (!config) return 10000; // Default 10s
    
    const baseInterval = config.interval_ms;
    const activity = activityLevel ?? this.activityLevels.get(component) ?? 0;
    
    // Adaptive scaling based on activity
    if (activity <= 1) {
      return baseInterval * 3; // Much slower when inactive
    } else if (activity <= 2) {
      return baseInterval * 2; // Slower
    } else if (activity >= 4) {
      return Math.floor(baseInterval * 0.7); // Faster when very active
    } else {
      return baseInterval; // Standard
    }
  }
  
  stopPolling(component: string) {
    const timeoutId = this.activeIntervals.get(component);
    if (timeoutId) {
      clearTimeout(timeoutId);
      this.activeIntervals.delete(component);
    }
  }
  
  stopAllPolling() {
    for (const component of this.activeIntervals.keys()) {
      this.stopPolling(component);
    }
  }
  
  // On-demand polling for specific events
  pollOnDemand(component: string, pollFunction: () => Promise<void>) {
    return pollFunction();
  }
  
  // Update activity level manually (e.g., on user interaction)
  updateActivity(component: string, delta: number = 1) {
    const current = this.activityLevels.get(component) || 0;
    this.activityLevels.set(component, Math.max(0, Math.min(5, current + delta)));
  }
}

// Globale Instanz
const pollingManager = new OptimizedPollingManager();

// Integration in React Components
export const useOptimizedPolling = (
  component: string, 
  pollFunction: () => Promise<void>,
  dependencies: any[] = []
) => {
  useEffect(() => {
    pollingManager.startOptimizedPolling(component, pollFunction);
    
    return () => {
      pollingManager.stopPolling(component);
    };
  }, dependencies);
  
  // Return manual trigger for on-demand polling
  return {
    pollNow: () => pollingManager.pollOnDemand(component, pollFunction),
    updateActivity: (delta: number) => pollingManager.updateActivity(component, delta),
    stopPolling: () => pollingManager.stopPolling(component)
  };
};

// Spezifische Hook-Implementierungen
export const useOrchestratorPolling = (fetchFunction: () => Promise<void>) => {
  return useOptimizedPolling("orchestrator_dashboard", fetchFunction);
};

export const useKnowledgeBasePolling = (fetchFunction: () => Promise<void>) => {
  return useOptimizedPolling("knowledge_base_status", fetchFunction);
};

export const usePerformanceMetricsPolling = (fetchFunction: () => Promise<void>) => {
  return useOptimizedPolling("performance_metrics", fetchFunction);
};

// Event-based activity tracking
export const trackUserActivity = (component: string) => {
  pollingManager.updateActivity(component, 1);
};

// Tab visibility optimization
export const handleVisibilityChange = () => {
  if (document.hidden) {
    // Reduce polling when tab is not visible
    pollingManager.stopAllPolling();
  } else {
    // Resume polling when tab becomes visible
    // Components will restart their polling automatically
  }
};

document.addEventListener('visibilitychange', handleVisibilityChange);
