from fastapi import APIRouter
from di import VariationServiceDep
from src.variation.dtos.VariationCreateRequestDto import VariationCreateRequestDto
from src.variation.dtos.VariationResponseDto import VariationResponseDto
from src.variation.dtos.VariationUpdateRequestDto import VariationUpdateRequestDto
from src.variation.dtos.TrafficAllocationRequestDto import TrafficAllocationRequestDto

routes = APIRouter()

@routes.post(
  "/experiments/{experimentId}/variations", 
  response_model=VariationResponseDto, 
  tags=["variation"],
  name="act:create-variation"
)
async def createVariation(
    experimentId: int,
    reqDto: VariationCreateRequestDto,
    service: VariationServiceDep
  ) -> VariationResponseDto:
  return service.createVariation(experimentId, reqDto)

# 1. PATCH: Update general variation details
@routes.patch(
  "/variations/{id}",
  response_model=VariationResponseDto,
  tags=["variation"],
  name="act:update-variation"
)
async def updateVariation(
  id: int,
  reqDto: VariationUpdateRequestDto,
  service: VariationServiceDep
) -> VariationResponseDto:
  return service.updateVariation(id, reqDto)

# 2. PUT: Update traffic allocation (Bulk)
@routes.put(
  "/experiments/{experimentId}/traffic",
  response_model=list[VariationResponseDto],
  tags=["variation"],
  name="act:update-traffic-allocation"
)
async def updateTrafficAllocation(
  experimentId: int,
  reqDto: TrafficAllocationRequestDto,
  service: VariationServiceDep
) -> list[VariationResponseDto]:
  return service.updateTrafficAllocation(experimentId, reqDto)

@routes.get(
  "/experiments/{experimentId}/variations", 
  response_model=list[VariationResponseDto], 
  tags=["variation"],
  name="act:get-variations"
)
async def getVariations(
    experimentId: int,
    service: VariationServiceDep
  ) -> list[VariationResponseDto]:
  """
  Get all variations associated with a specific experiment.
  """
  return service.getVariations(experimentId)

@routes.delete(
  "/variations/{id}",
  response_model=VariationResponseDto,
  tags=["variation"],
  name="act:delete-variation"
)
async def deleteVariation(
  id: int,
  service: VariationServiceDep
) -> VariationResponseDto:
  """
  Delete a variation. 
  Note: The Control variation cannot be deleted.
  """
  return service.deleteVariation(id)