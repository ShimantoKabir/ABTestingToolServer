from fastapi import APIRouter
from di import ExperimentServiceDep
from src.experiment.dtos.ExperimentCreateRequestDto import ExperimentCreateRequestDto
from src.experiment.dtos.ExperimentCreateResponseDto import ExperimentCreateResponseDto
from src.experiment.dtos.ExperimentResponseDto import ExperimentResponseDto
from src.utils.pagination.PaginationRequestDto import PaginationRequestDto
from src.utils.pagination.PaginationResponseDto import PaginationResponseDto

routes = APIRouter()

@routes.post(
  "/experiments", 
  response_model=ExperimentCreateResponseDto, 
  tags=["experiment"],
  name="act:create-experiment"
)
async def createExperiment(
    reqDto: ExperimentCreateRequestDto,
    service: ExperimentServiceDep
  ) -> ExperimentCreateResponseDto:
  return service.createExperiment(reqDto)

@routes.post(
  "/experiments/all",
  tags=["experiment"],
  name="act:get-experiments",
  response_model=PaginationResponseDto[ExperimentResponseDto]
)
async def getExperiments(
  reqDto: PaginationRequestDto, 
  service: ExperimentServiceDep
) -> PaginationResponseDto[ExperimentResponseDto]:  
  return service.getExperiments(reqDto)

@routes.get(
  "/experiments/{id}",
  tags=["experiment"],
  name="act:get-experiment",
  response_model=ExperimentResponseDto
)
async def getExperimentById(
  id: int,
  service: ExperimentServiceDep
) -> ExperimentResponseDto:
  return service.getById(id)