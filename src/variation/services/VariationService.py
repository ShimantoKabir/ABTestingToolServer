from src.variation.repository.VariationRepository import VariationRepository
from src.experiment.repository.ExperimentRepository import ExperimentRepository
from src.variation.dtos.VariationCreateRequestDto import VariationCreateRequestDto
from src.variation.dtos.VariationResponseDto import VariationResponseDto
from src.variation.dtos.VariationUpdateRequestDto import VariationUpdateRequestDto
from src.variation.dtos.TrafficAllocationRequestDto import TrafficAllocationRequestDto
from src.variation.model.Variation import Variation
from fastapi import HTTPException, status

class VariationService:
  def __init__(
    self, 
    repo: VariationRepository,
    experimentRepo: ExperimentRepository
  ):
    self.repo = repo
    self.experimentRepo = experimentRepo

  def createVariation(self, experimentId: int, reqDto: VariationCreateRequestDto) -> VariationResponseDto:
    self.experimentRepo.getById(experimentId)
    variations = self.repo.getByExperimentId(experimentId)

    newVariation = Variation(
      title=reqDto.title,
      js=reqDto.js,
      css=reqDto.css,
      experimentId=experimentId,
      traffic=0 
    )
    
    variations.append(newVariation)
    self._distributeTrafficEvenly(variations)
    self.repo.saveAll(variations)

    return self._mapToResponse(newVariation)

  # 1. Update a single variation (Title, JS, CSS)
  def updateVariation(self, id: int, reqDto: VariationUpdateRequestDto) -> VariationResponseDto:
    variation = self.repo.getById(id)

    if reqDto.title is not None:
      variation.title = reqDto.title
    if reqDto.js is not None:
      variation.js = reqDto.js
    if reqDto.css is not None:
      variation.css = reqDto.css

    updatedVar = self.repo.edit(variation)
    return self._mapToResponse(updatedVar)

  # 2. Update Traffic Allocation for the whole experiment
  def updateTrafficAllocation(self, experimentId: int, reqDto: TrafficAllocationRequestDto) -> list[VariationResponseDto]:
    # Fetch all actual variations from DB
    dbVariations = self.repo.getByExperimentId(experimentId)
    if not dbVariations:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No variations found for this experiment")

    # Create a map for quick lookup
    dbVarMap = {v.id: v for v in dbVariations}
    
    # Input validation: Ensure user sent allocations for ALL existing variations
    inputIds = set(a.variationId for a in reqDto.allocations)
    existingIds = set(dbVarMap.keys())

    if inputIds != existingIds:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail="Traffic allocation must include all variations belonging to this experiment"
      )

    # Apply updates
    for alloc in reqDto.allocations:
      variation = dbVarMap[alloc.variationId]
      variation.traffic = alloc.traffic
    
    # Save changes
    self.repo.saveAll(dbVariations)

    return [self._mapToResponse(v) for v in dbVariations]

  # Helper: Distribute logic (used in creation)
  def _distributeTrafficEvenly(self, variations: list[Variation]):
    count = len(variations)
    if count > 0:
      base_traffic = 100 // count
      remainder = 100 % count
      for i, var in enumerate(variations):
        extra = 1 if i < remainder else 0
        var.traffic = base_traffic + extra

  def _mapToResponse(self, v: Variation) -> VariationResponseDto:
    return VariationResponseDto(
      id=v.id,
      experimentId=v.experimentId, # type: ignore
      title=v.title,
      traffic=v.traffic, # type: ignore
      js=v.js,
      css=v.css
    )