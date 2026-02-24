from typing import Callable, Dict, List
from src.state import AgentState

# -----------------------------
# Node Base Class
# -----------------------------
class Node:
    def __init__(self, name: str, func: Callable[[AgentState], AgentState]):
        self.name = name
        self.func = func
        self.next_nodes: List["Node"] = []

    def add_edge(self, node: "Node"):
        self.next_nodes.append(node)

    def run(self, state: AgentState) -> AgentState:
        print(f"[Node Start] {self.name}")
        new_state = self.func(state)
        for node in self.next_nodes:
            new_state = node.run(new_state)
        print(f"[Node End] {self.name}")
        return new_state

# -----------------------------
# StateGraph Orchestrator
# -----------------------------
class StateGraph:
    def __init__(self, initial_state: AgentState):
        self.state = initial_state
        self.nodes: Dict[str, Node] = {}
        self.fan_in_nodes: List[str] = []

    def add_node(self, node: Node):
        self.nodes[node.name] = node

    def add_edge(self, from_node: str, to_node: str):
        if from_node not in self.nodes or to_node not in self.nodes:
            raise ValueError(f"Nodes {from_node} or {to_node} not found in graph")
        self.nodes[from_node].add_edge(self.nodes[to_node])

    def add_fan_in(self, node_names: List[str]):
        """Declare nodes that must complete before fan-in."""
        self.fan_in_nodes.extend(node_names)

    def run(self):
        """Run graph from all root nodes (no incoming edges)."""
        root_nodes = [node for name, node in self.nodes.items() if name not in self.fan_in_nodes]
        state = self.state
        for node in root_nodes:
            state = node.run(state)
        return state

# -----------------------------
# Example Node Functions (Skeletons)
# -----------------------------

def repo_investigator(state: AgentState) -> AgentState:
    print("Running RepoInvestigator...")
    # Placeholder: integrate git_tools + AST parsing
    return state

def doc_analyst(state: AgentState) -> AgentState:
    print("Running DocAnalyst...")
    # Placeholder: integrate pdf_tools + cross-reference
    return state

def vision_inspector(state: AgentState) -> AgentState:
    print("Running VisionInspector...")
    # Placeholder: integrate vision_tools
    return state

def evidence_aggregator(state: AgentState) -> AgentState:
    print("Aggregating evidence...")
    state.fan_in_ready = True
    return state
