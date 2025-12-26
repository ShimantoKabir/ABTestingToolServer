from fastapi import APIRouter, Request
from src.org.dtos.OrgAddResDto import OrgAddResDto
from src.org.dtos.OrgAddReqDto import OrgAddReqDto
from src.user.dtos.UserResponseDto import UserResponseDto
from di import UserServiceDep
from fastapi import status, HTTPException
from src.user.dtos.UpdateUserRequestDto import UpdateUserRequestDto
from src.user.dtos.UpdateUserResponseDto import UpdateUserResponseDto
from src.utils.pagination.PaginationRequestDto import PaginationRequestDto
from src.utils.pagination.PaginationResponseDto import PaginationResponseDto

routes = APIRouter()

@routes.get("/users/{id}", tags=["user"], name="act:get-user")
async def getById(id: int, userService: UserServiceDep)-> UserResponseDto:
  return userService.getUserById(id)

@routes.patch(
  "/users/{userId}/organization/{orgId}", 
  tags=["user"],
  name="act:update-user",
  response_model=UpdateUserResponseDto
)
async def updateUser(
  userId: int, 
  orgId: int,
  reqDto: UpdateUserRequestDto, 
  userService: UserServiceDep
)-> UserResponseDto:
  return userService.updateUser(userId, orgId, reqDto)

@routes.post(
  "/users/organizations", 
  tags=["user"], 
  name="act:add-organization", 
  response_model=OrgAddResDto
)
async def addOrg(
  reqDto: OrgAddReqDto, 
  userService: UserServiceDep, 
  request: Request
)-> OrgAddResDto:
  authEmail = request.headers.get("email")

  if not authEmail:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No mail found on header!")

  return userService.addOrg(reqDto, authEmail)

@routes.post(
  "/users/all",
  tags=["user"],
  name="act:get-users",
  response_model=PaginationResponseDto[UserResponseDto]
)
async def getUsers(
  reqDto: PaginationRequestDto, 
  userService: UserServiceDep
) -> PaginationResponseDto[UserResponseDto]:  
  return userService.getUsers(reqDto)

@routes.get(
  "/{userId}/orgs/{orgId}/details", 
  tags=["user"],
  name="act:get-user-org-details",
  response_model=UserResponseDto
)
def getUserDetailsByOrgAndUser(
    userId: int, 
    orgId: int, 
    userService: UserServiceDep
) -> UserResponseDto:
  """
  Get detailed user information specifically for a given organization context,
  including their Role Name and Menu Template Name.
  """
  return userService.getUserDetailsByOrgAndUser(userId, orgId)