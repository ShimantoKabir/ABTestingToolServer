from fastapi import APIRouter
from src.org.dtos.OrgCreateRequestDto import OrgCreateRequestDto
from src.org.dtos.OrgCreateResponseDto import OrgCreateResponseDto
from di import OrgServiceDep

routes = APIRouter()

@routes.post(
  "/organizations", 
  response_model=OrgCreateResponseDto, 
  tags=["organization"],
  name="act:create-organization"
)
async def createOrganization(
    # 1. Switched to the new Create DTOs
    reqDto: OrgCreateRequestDto,
    orgService: OrgServiceDep
  ) -> OrgCreateResponseDto:
  print("Creating organization with email:", reqDto.email)
  return orgService.createOrg(reqDto)