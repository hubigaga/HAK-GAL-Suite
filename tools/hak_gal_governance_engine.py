"""
HAK-GAL Governance Engine (Fixed Version)
=========================================

The central decision-making and resource allocation engine for the HAK-GAL Suite,
integrating multi-agent coordination, ETHIK resonance filtering, and self-adaptive governance.
Designed for scalability, ethical alignment, and fault tolerance within the ArchonOS ecosystem.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, AsyncGenerator, Callable
from collections import defaultdict, deque
from enum import Enum
import time
import logging
import json
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
from cachetools import TTLCache
from prometheus_client import Counter, Histogram, Gauge
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity  # FIXED: Added missing import

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Try to import HAK-GAL modules with fallback
try:
    from hak_gal_relevance_filter import Fact
    from hak_gal_orchestrator5 import OrchestratingRelevanceManager, FilterStrategy  # FIXED: Changed to orchestrator5
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    logger.warning("HAK-GAL orchestrator modules not available - running in standalone mode")
    ORCHESTRATOR_AVAILABLE = False
    # Define minimal placeholders
    class Fact:
        def __init__(self, id, subject, predicate, object, confidence=1.0):
            self.id = id
            self.subject = subject
            self.predicate = predicate
            self.object = object
            self.confidence = confidence

# Try to import sentence_transformers with fallback
try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not available - ETHIK filter will use mock implementation")
    TRANSFORMERS_AVAILABLE = False
    class SentenceTransformer:
        def __init__(self, model_name):
            self.model_name = model_name
        def encode(self, texts):
            # Mock implementation
            if isinstance(texts, list):
                return np.random.rand(len(texts), 384)
            return np.random.rand(384)

# Prometheus metrics
GOVERNANCE_DECISIONS = Counter('hak_gal_governance_decisions_total', 'Total governance decisions made')
DECISION_LATENCY = Histogram('hak_gal_governance_decision_latency_seconds', 'Decision processing latency')
ETHIK_VIOLATIONS = Counter('hak_gal_ethik_violations_total', 'Total ETHIK filter violations')
AGENT_PERFORMANCE = Histogram('hak_gal_agent_performance_seconds', 'Agent processing latency', labelnames=['agent'])

class GovernanceAction(Enum):
    """Available governance actions"""
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    PRIORITIZE = "prioritize"
    DEPRIORITIZE = "deprioritize"
    REDISTRIBUTE = "redistribute"

@dataclass
class GovernanceConfig:
    """Configuration for the Governance Engine"""
    max_decision_time: float = 0.5  # Seconds
    ethik_threshold: float = 0.9  # Minimum ETHIK resonance score
    cache_size: int = 10000
    cache_ttl: float = 7200
    max_concurrent_decisions: int = 50
    max_workers: int = 8
    learning_rate: float = 0.01
    transformer_model: str = "all-MiniLM-L6-v2"
    resource_weights: Dict[str, float] = field(default_factory=lambda: {
        'cpu': 0.4,
        'memory': 0.3,
        'network': 0.2,
        'storage': 0.1
    })
    agent_weights: Dict[str, float] = field(default_factory=lambda: {
        'orchestrator': 0.5,
        'ml_model': 0.3,
        'external_api': 0.2
    })
    enable_ethik_filter: bool = True
    enable_learning: bool = True
    enable_resource_optimization: bool = True
    a_b_testing: bool = True

@dataclass
class AgentRequest:
    """Request from an agent to the governance engine"""
    agent_id: str
    action: str
    priority: float
    resources: Dict[str, float]  # Requested resources (cpu, memory, etc.)
    context: Dict[str, Any]  # Additional context (e.g., query, facts)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GovernanceDecision:
    """Decision made by the governance engine"""
    action: GovernanceAction
    agent_id: str
    score: float
    reason: str
    resources_allocated: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    provenance: List[str] = field(default_factory=list)

class ETHIKResonanceFilter:
    """Filter to ensure decisions align with ethical principles"""
    def __init__(self, transformer_model: str, threshold: float):
        self.transformer = SentenceTransformer(transformer_model)
        self.threshold = threshold
        self.ethik_principles = [
            "Ensure fairness and transparency",
            "Minimize harm and bias",
            "Respect user autonomy",
            "Promote truth and accuracy"
        ]
        self.principle_embeddings = self.transformer.encode(self.ethik_principles)
    
    async def evaluate(self, request: AgentRequest) -> bool:
        """Evaluate request against ETHIK principles"""
        try:
            context_text = json.dumps(request.context)
            context_embedding = self.transformer.encode(context_text)
            scores = cosine_similarity([context_embedding], self.principle_embeddings)[0]
            avg_score = np.mean(scores)
            if avg_score < self.threshold:
                ETHIK_VIOLATIONS.inc()
                logger.warning(f"ETHIK violation detected: score={avg_score:.3f}, request={request}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error in ETHIK evaluation: {e}")
            return True  # Default to allowing in case of error

class ResourceOptimizer:
    """Optimizes resource allocation across agents"""
    def __init__(self, config: GovernanceConfig):
        self.config = config
        self.resource_pool = {
            'cpu': 100.0,  # Total available CPU units
            'memory': 1000.0,  # Total available memory (GB)
            'network': 10000.0,  # Total available bandwidth (Mbps)
            'storage': 10000.0  # Total available storage (GB)
        }
    
    async def allocate(self, request: AgentRequest) -> Dict[str, float]:
        """Allocate resources based on request and weights"""
        allocated = {}
        for resource, requested in request.resources.items():
            weight = self.config.resource_weights.get(resource, 1.0)
            available = self.resource_pool.get(resource, 0.0)
            allocated[resource] = min(requested * weight, available * 0.9)  # Reserve 10% buffer
            self.resource_pool[resource] -= allocated[resource]
        return allocated

class GovernanceEngine:
    """
    Core governance engine for HAK-GAL, coordinating multi-agent decisions,
    enforcing ETHIK principles, and optimizing resources.
    """
    def __init__(self, config: Optional[GovernanceConfig] = None):
        self.config = config or GovernanceConfig()
        self.ethik_filter = ETHIKResonanceFilter(self.config.transformer_model, self.config.ethik_threshold)
        self.resource_optimizer = ResourceOptimizer(self.config)
        self.cache = TTLCache(maxsize=self.config.cache_size, ttl=self.config.cache_ttl)
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_decisions)
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self.decision_buffer = deque(maxlen=1000)  # For online learning
        
        # Initialize agents
        self.agents = {}
        if ORCHESTRATOR_AVAILABLE:
            try:
                self.agents['orchestrator'] = OrchestratingRelevanceManager()
                logger.info("Orchestrator agent initialized")
            except Exception as e:
                logger.warning(f"Could not initialize orchestrator: {e}")
        
        self.agents['ml_model'] = None  # Placeholder for ML agent
        self.agents['external_api'] = None  # Placeholder for external API agent
        
        self.metrics = {
            'total_decisions': Gauge('hak_gal_governance_total_decisions', 'Total decisions made'),
            'avg_decision_time': Gauge('hak_gal_governance_avg_decision_time', 'Average decision time'),
            'ethik_compliance_rate': Gauge('hak_gal_governance_ethik_compliance', 'ETHIK compliance rate'),
            'agent_performance': defaultdict(lambda: {'calls': 0, 'avg_time': 0}),
            'resource_utilization': Gauge('hak_gal_resource_utilization', 'Resource utilization', labelnames=['resource'])
        }
        for resource in self.config.resource_weights:
            self.metrics['resource_utilization'].labels(resource=resource).set(0.0)
        logger.info("Governance Engine initialized")
    
    async def add_agent(self, agent_id: str, agent: Any) -> None:
        """Add a new agent to the system"""
        self.agents[agent_id] = agent
        logger.info(f"Agent {agent_id} added to governance engine")
    
    async def process_request(self, request: AgentRequest) -> GovernanceDecision:
        """
        Process an agent request and return a governance decision.
        
        Args:
            request: Agent request containing action, priority, resources, and context
            
        Returns:
            GovernanceDecision: Decision with action, score, and allocated resources
        """
        async with self.semaphore:
            self.metrics['total_decisions'].inc()
            GOVERNANCE_DECISIONS.inc()
            
            with DECISION_LATENCY.time():
                start_time = time.time()
                
                # Check cache
                cache_key = (request.agent_id, request.action, json.dumps(request.context))
                if cache_key in self.cache:
                    decision = self.cache[cache_key]
                    logger.info(f"Cache hit for request: {request}")
                    return decision
                
                # Apply ETHIK filter
                if self.config.enable_ethik_filter:
                    if not await self.ethik_filter.evaluate(request):
                        decision = GovernanceDecision(
                            action=GovernanceAction.REJECT,
                            agent_id=request.agent_id,
                            score=0.0,
                            reason="ETHIK filter violation",
                            metadata={'context': request.context},
                            provenance=["ETHIK_filter_rejection"]
                        )
                        self.cache[cache_key] = decision
                        return decision
                
                # Evaluate request
                score = await self._evaluate_request(request)
                action = self._decide_action(score, request)
                
                # Allocate resources
                resources = await self.resource_optimizer.allocate(request) if action == GovernanceAction.APPROVE else {}
                
                # Create decision
                decision = GovernanceDecision(
                    action=action,
                    agent_id=request.agent_id,
                    score=score,
                    reason=f"Decision based on score {score:.3f} and priority {request.priority}",
                    resources_allocated=resources,
                    metadata={'context': request.context, 'timestamp': time.time()},
                    provenance=[f"score: {score:.3f}", f"priority: {request.priority}"]
                )
                
                # Update learning buffer
                if self.config.enable_learning:
                    self.decision_buffer.append((request, decision))
                    if len(self.decision_buffer) >= 100:
                        await self._update_decision_model()
                
                # Update metrics
                decision_time = time.time() - start_time
                self._update_metrics(decision_time, resources)
                self.cache[cache_key] = decision
                
                logger.info(f"Decision made: {decision.action.value} for {request.agent_id}")
                return decision
    
    async def _evaluate_request(self, request: AgentRequest) -> float:
        """Evaluate request based on agent weights and context"""
        agent_weight = self.config.agent_weights.get(request.agent_id, 1.0)
        score = request.priority * agent_weight
        
        # Context-based scoring (e.g., query relevance)
        if 'query' in request.context and ORCHESTRATOR_AVAILABLE:
            orchestrator = self.agents.get('orchestrator')
            if orchestrator:
                try:
                    async for fact in orchestrator.query(request.context['query'], max_results=1):
                        score += fact.confidence * 0.5  # Boost based on relevance
                except Exception as e:
                    logger.warning(f"Error querying orchestrator: {e}")
        
        return min(score, 1.0)
    
    def _decide_action(self, score: float, request: AgentRequest) -> GovernanceAction:
        """Determine action based on score and priority"""
        if score >= 0.8:
            return GovernanceAction.APPROVE
        elif score >= 0.5:
            return GovernanceAction.ESCALATE
        else:
            return GovernanceAction.REJECT
    
    async def _update_decision_model(self) -> None:
        """Update decision model with buffered data (placeholder for online learning)"""
        logger.info("Updating governance decision model")
        self.decision_buffer.clear()
    
    def _update_metrics(self, decision_time: float, resources: Dict[str, float]) -> None:
        """Update governance metrics"""
        n = self.metrics['total_decisions']._value
        self.metrics['avg_decision_time'].set(
            (self.metrics['avg_decision_time']._value * (n - 1) + decision_time) / n
        )
        self.metrics['ethik_compliance_rate'].set(
            1.0 - (ETHIK_VIOLATIONS._value / max(1, self.metrics['total_decisions']._value))
        )
        for resource, allocated in resources.items():
            total = self.resource_optimizer.resource_pool.get(resource, 1.0)
            if total > 0:
                self.metrics['resource_utilization'].labels(resource=resource).set(allocated / total)
    
    async def coordinate_agents(self, requests: List[AgentRequest]) -> AsyncGenerator[GovernanceDecision, None]:
        """
        Coordinate multiple agent requests in parallel.
        
        Args:
            requests: List of agent requests
            
        Yields:
            GovernanceDecision: Decisions for each request
        """
        tasks = [self.process_request(req) for req in requests]
        for future in await asyncio.gather(*tasks, return_exceptions=True):
            if isinstance(future, GovernanceDecision):
                yield future
            else:
                logger.error(f"Error processing request: {future}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""  # FIXED: Added missing method
        return {
            'total_decisions': self.metrics['total_decisions']._value,
            'avg_decision_time': self.metrics['avg_decision_time']._value,
            'ethik_compliance_rate': self.metrics['ethik_compliance_rate']._value,
            'agent_performance': dict(self.metrics['agent_performance']),
            'resource_utilization': {
                resource: self.metrics['resource_utilization'].labels(resource=resource)._value
                for resource in self.config.resource_weights
            }
        }
    
    async def save_config(self, path: str) -> None:
        """Save configuration to file"""
        with open(path, 'w') as f:
            json.dump({k: v for k, v in self.config.__dict__.items() if not k.startswith('_')}, f, indent=2)
    
    @classmethod
    async def load_config(cls, path: str) -> 'GovernanceEngine':
        """Load configuration from file"""
        with open(path, 'r') as f:
            config_dict = json.load(f)
        config = GovernanceConfig(**config_dict)
        return cls(config)

if __name__ == "__main__":
    async def main():
        config = GovernanceConfig(
            max_decision_time=0.5,
            ethik_threshold=0.9,
            enable_ethik_filter=True,
            enable_learning=True,
            enable_resource_optimization=True,
            resource_weights={'cpu': 0.4, 'memory': 0.3, 'network': 0.2, 'storage': 0.1},
            agent_weights={'orchestrator': 0.5, 'ml_model': 0.3, 'external_api': 0.2}
        )
        governance = GovernanceEngine(config)
        
        # Example agent requests
        requests = [
            AgentRequest(
                agent_id='orchestrator',
                action='query',
                priority=0.8,
                resources={'cpu': 10.0, 'memory': 100.0},
                context={'query': 'Socrates'},
                metadata={'timestamp': time.time()}
            ),
            AgentRequest(
                agent_id='ml_model',
                action='predict',
                priority=0.6,
                resources={'cpu': 20.0, 'memory': 200.0},
                context={'data': 'some_data'},
                metadata={'timestamp': time.time()}
            )
        ]
        
        print("\n=== Testing Governance Engine ===\n")
        async for decision in governance.coordinate_agents(requests):
            print(f"Decision for {decision.agent_id}: {decision.action.value} (Score: {decision.score:.3f})")
            print(f"  Reason: {decision.reason}")
            print(f"  Resources: {decision.resources_allocated}")
            print(f"  Provenance: {decision.provenance}")
        
        print("\n=== Performance Metrics ===")
        metrics = governance.get_metrics()
        print(json.dumps(metrics, indent=2))
    
    asyncio.run(main())
