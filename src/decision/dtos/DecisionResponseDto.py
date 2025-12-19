from dataclasses import dataclass
from typing import List, Optional
from src.condition.dtos.ConditionResponseDto import ConditionResponseDto
from src.metrics.dtos.MetricsResponseDto import MetricsResponseDto

@dataclass
class VariationDecisionDto:
  variationId: int
  variationTitle: str
  js: Optional[str]
  css: Optional[str]

@dataclass
class ExperimentDecisionDto:
  experimentId: int
  experimentTitle: str
  experimentJs: Optional[str]
  experimentCss: Optional[str]
  variation: VariationDecisionDto
  conditions: List[ConditionResponseDto]
  metrics: List[MetricsResponseDto]

@dataclass
class DecisionResponseDto:
  endUserId: int
  decisions: List[ExperimentDecisionDto]