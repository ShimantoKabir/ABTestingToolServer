import mmh3
import random
from datetime import datetime, timedelta, timezone
from fastapi import BackgroundTasks
from src.bucket.repository.BucketRepository import BucketRepository
from src.experiment.repository.ExperimentRepository import ExperimentRepository
from src.decision.dtos.DecisionRequestDto import DecisionRequestDto
from src.decision.dtos.DecisionResponseDto import DecisionResponseDto, ExperimentDecisionDto, VariationDecisionDto
from src.bucket.model.Bucket import Bucket
from src.experiment.model.Experiment import Experiment
from src.condition.model.Operator import Operator
from src.metrics.dtos.MetricsResponseDto import MetricsResponseDto
from src.condition.dtos.ConditionResponseDto import ConditionResponseDto

class DecisionService:
  # The bucketing scale (1 to 10,000 for 0.01% granularity)
  MAX_TRAFFIC_VAL = 10000
  
  # Caching configuration
  _cache = {} 
  _cacheTtl = timedelta(seconds=60) # Cache experiment config for 60 seconds

  def __init__(
    self, 
    bucketRepo: BucketRepository,
    experimentRepo: ExperimentRepository
  ):
    self.bucketRepo = bucketRepo
    self.experimentRepo = experimentRepo

  def makeDecision(
      self, 
      reqDto: DecisionRequestDto, 
      projectId: int, 
      bgTasks: BackgroundTasks
    ) -> DecisionResponseDto:
    
    # 1. Identity Management
    # If client didn't send an ID (first visit), generate a random one.
    endUserId = reqDto.endUserId if reqDto.endUserId else random.randint(100000, 999999)

    # 2. Fetch Active Experiments (with Caching)
    activeExperiments = self.getActiveExperiments(projectId)

    decisions: list[ExperimentDecisionDto] = []

    for exp in activeExperiments:
      # 3. Targeting Check (Does URL match?)
      if not self.checkTargeting(exp, reqDto.url):
        continue

      # 4. Consistency Check (Sticky Bucketing)
      # Check if this user is already assigned to a variation in this experiment
      existingBucket = self.bucketRepo.get(experimentId=exp.id, endUserId=endUserId)

      if existingBucket:
        # User is already locked in. Return the saved variation.
        assignedVariation = next((v for v in exp.variations if v.id == existingBucket.variationId), None)
        if assignedVariation:
          decisions.append(self.buildDecisionDto(exp, assignedVariation))
      
      else:
        # 5. The Bucketing Machine (New Assignment)
        # Hash input: "UserID:ExperimentID" -> Ensures randomness per experiment
        hashKey = f"{endUserId}:{exp.id}"
        hashInt = mmh3.hash(hashKey)
        
        # Scale hash to 1 - 10,000
        bucketVal = (abs(hashInt) % self.MAX_TRAFFIC_VAL) + 1
        
        # 6. Traffic Allocation
        chosenVariation = None
        cumulativeTraffic = 0

        for variation in exp.variations:
          # Convert percentage (traffic is 0-100) to scale (0-10000)
          rangeLimit = int(variation.traffic * 100)
          
          if bucketVal <= (cumulativeTraffic + rangeLimit):
            chosenVariation = variation
            break
          
          cumulativeTraffic += rangeLimit

        if chosenVariation:
          # 7. Async Persistence
          # Queue the DB write to run AFTER response is sent.
          bgTasks.add_task(self.recordAssignment, exp.id, endUserId, chosenVariation.id)
          decisions.append(self.buildDecisionDto(exp, chosenVariation))

    return DecisionResponseDto(endUserId=endUserId, decisions=decisions)

  def recordAssignment(self, expId: int, userId: int, varId: int):
    # This runs in the background.
    # We check again or rely on DB constraints to prevent duplicates.
    existing = self.bucketRepo.get(expId, userId)
    if not existing:
      # Note: Ensure your BucketRepository.add handles IntegrityError/Duplicates gracefully
      self.bucketRepo.add(Bucket(expId=expId, endUserId=userId, variationId=varId))

  def checkTargeting(self, exp: Experiment, url: str) -> bool:
    if not exp.conditions:
      return True

    matches = []
    for cond in exp.conditions:
      isMatch = False 
      
      # OR Logic for Positive Operators (Match if ANY url matches)
      if cond.operator in [Operator.IS, Operator.CONTAIN]:
        for condUrl in cond.urls:
          if cond.operator == Operator.CONTAIN and condUrl in url:
            isMatch = True
            break
          if cond.operator == Operator.IS and condUrl == url:
            isMatch = True
            break
             
      # AND Logic for Negative Operators (Fail if ANY url matches)
      elif cond.operator in [Operator.IS_NOT, Operator.NOT_CONTAIN]:
        isMatch = True # Default to True, try to prove False
        for condUrl in cond.urls:
          if cond.operator == Operator.NOT_CONTAIN and condUrl in url:
            isMatch = False
            break 
          if cond.operator == Operator.IS_NOT and condUrl == url:
            isMatch = False
            break 
      
      matches.append(isMatch)

    if exp.conditionType == "ALL":
      return all(matches)
    else: # ANY
      return any(matches)

  def getActiveExperiments(self, projectId: int) -> list[Experiment]:
    # Check In-Memory Cache
    if projectId in self._cache:
      data, timestamp = self._cache[projectId]
      if datetime.now(timezone.utc) - timestamp < self._cacheTtl:
        return data
    
    # Cache Miss: Fetch from DB
    activeExperiments = self.experimentRepo.getAllActive(rows=1000, page=1, projectId=projectId)
    
    # Set Cache
    self._cache[projectId] = (activeExperiments, datetime.now(timezone.utc))
    
    return activeExperiments

  def buildDecisionDto(self, exp: Experiment, variation) -> ExperimentDecisionDto:
    # Map Conditions
    condDtos = [
      ConditionResponseDto(
        id=c.id, 
        experimentId=c.experimentId, 
        urls=[str(u) for u in c.urls], 
        operator=c.operator
      ) for c in exp.conditions
    ]
    
    # Map Metrics
    metDtos = [
      MetricsResponseDto(
        id=m.id, 
        experimentId=m.experimentId, 
        title=m.title, 
        custom=m.custom, 
        selector=m.selector, 
        description=m.description, 
        triggered=m.triggered
      ) for m in exp.metrics
    ]

    return ExperimentDecisionDto(
      experimentId=exp.id,
      experimentTitle=exp.title,
      experimentJs=exp.js,
      experimentCss=exp.css,
      variation=VariationDecisionDto(
        variationId=variation.id,
        variationTitle=variation.title,
        js=variation.js,
        css=variation.css
      ),
      conditions=condDtos,
      metrics=metDtos
    )