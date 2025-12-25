import random
from src.org.repository.OrgRepository import OrgRepository
# 1. Update imports to use the new DTOs
from src.org.dtos.OrgCreateRequestDto import OrgCreateRequestDto
from src.org.dtos.OrgCreateResponseDto import OrgCreateResponseDto
from src.org.model.Organization import Organization
from src.user.repository.UserRepository import UserRepository
from src.user.model.User import User
from fastapi import HTTPException, status
from passlib.context import CryptContext
from src.utils.FileService import FileService
from src.role.repository.RoleRepository import RoleRepository
from src.role.model.Role import Role
from src.menutemplate.repository.MenuTemplateRepository import MenuTemplateRepository
from src.menutemplate.model.MenuTemplate import MenuTemplate
from src.email.EmailService import EmailService
from src.utils.Constants import OTP_POPULATION_DIGITS
from src.db.repository.UserOrgLinkRepository import UserOrgLinkRepository
from src.org.dtos.OrgSearchResDto import OrgSearchResDto
from src.project.model.Project import Project
from src.db.links.UserProjectLink import UserProjectLink
from src.db.links.PermissionType import PermissionType
from src.project.repository.ProjectRepository import ProjectRepository
from src.db.repository.UserProjectLinkRepository import UserProjectLinkRepository

class OrgService:
  def __init__(
      self, 
      orgRepo: OrgRepository, 
      userRepo: UserRepository,
      roleRepo: RoleRepository,
      crypto: CryptContext,
      fileService: FileService,
      emailService : EmailService,
      userOrgLinkRepo: UserOrgLinkRepository,
      mtRepo: MenuTemplateRepository,
      projectRepo: ProjectRepository,
      userProjectLinkRepo: UserProjectLinkRepository
    ):
    self.repo = orgRepo
    self.userRepo = userRepo
    self.roleRepo = roleRepo
    self.crypto = crypto
    self.fileService = fileService
    self.emailService = emailService
    self.userOrgLinkRepo = userOrgLinkRepo
    self.mtRepo = mtRepo
    self.projectRepo = projectRepo
    self.userProjectLinkRepo = userProjectLinkRepo

  # 2. Update signature to use OrgCreateRequestDto -> OrgCreateResponseDto
  def createOrg(self, reqDto: OrgCreateRequestDto) -> OrgCreateResponseDto:
    
    try:
      domain = reqDto.email.split("@")[1]
      domainName = domain.split(".")[0]
    except IndexError:
      raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
      )

    existingOrg = self.repo.getByDomain(domain)
    if existingOrg:
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT, 
        detail="Organization already exists with this domain!"
      )
    
    existingUser = self.userRepo.getUserByEmail(reqDto.email)
    if existingUser:
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User already exists with this email!"
      )

    newOrg = self.repo.add(Organization(
      name=reqDto.name,
      email=reqDto.email,
      domain=domain
    ))

    adminRole = self.roleRepo.add(Role(name="Admin",orgId=newOrg.id))

    adminMenuTree = self.fileService.readFile("static/menu.json")
    
    adminMenuTemplate = self.mtRepo.add(MenuTemplate(
      name="Admin Menu Template",
      orgId=newOrg.id,
      tree=adminMenuTree
    ))

    otp = self.generateOtp()

    truncatedPassword = reqDto.password[:72]
    
    newUser = self.userRepo.add(User(
      email=reqDto.email,
      password=self.crypto.hash(truncatedPassword),
      verified=False, 
      otp=otp,
      orgs=[newOrg],
      projects=[],
    ))

    userOrgLink = self.userOrgLinkRepo.get(userId=newUser.id, orgId=newOrg.id)
    if userOrgLink:
      userOrgLink.roleId = adminRole.id
      userOrgLink.menuTemplateId = adminMenuTemplate.id
      userOrgLink.super = True 
      userOrgLink.disabled = False
      self.userOrgLinkRepo.edit(userOrgLink)

    defaultProject = self.projectRepo.add(Project(
      name=f"{domainName.capitalize()} Project",
      description=f"Automatically created {domainName} project, during organization registration.",
      orgId=newOrg.id
    ))

    self.userProjectLinkRepo.add(UserProjectLink(
      userId=newUser.id,
      projectId=defaultProject.id,
      super=True,
      permissionType=PermissionType.OWNER,
      disabled=False
    ))

    self.emailService.sendAccountVerificationOtp(newUser.email, otp)

    return OrgCreateResponseDto(
      id=newOrg.id, 
      name=newOrg.name, 
      email=newOrg.email
    )
  
  def generateOtp(self)->str:
    otp = ''.join(random.choices(OTP_POPULATION_DIGITS, k=6))
    return otp
  
  def searchOrg(self, query: str) -> list[OrgSearchResDto]:
    # We limit to 10 results to keep the autocomplete fast
    orgs = self.repo.search(query, limit=10)
    
    return [
      OrgSearchResDto(id=o.id, name=o.name) 
      for o in orgs
    ]