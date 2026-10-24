from dataclasses import dataclass

from langchain.agents import AgentState


@dataclass
class AgentContext:
    reference_answer: str


class TrainingState(AgentState):
    supervisor_used: bool
