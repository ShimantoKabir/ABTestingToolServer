import jwt
from passlib.context import CryptContext
from src.db.repository.UserOrgLinkRepository import UserOrgLinkRepository
from src.auth.repository.AuthRepository import AuthRepository
from src.auth.dtos.LoginRequestDto import LoginRequestDto
from src.auth.dtos.LoginResponseDto import LoginResponseDto
from src.user.model.User import User
from fastapi import status, HTTPException
from datetime import datetime, timedelta, timezone
from config import Config
from src.auth.dtos.AuthRefreshResponseDto import AuthRefreshResponseDto
from src.auth.dtos.AuthRefreshRequestDto import AuthRefreshRequestDto
from jwt import ExpiredSignatureError
from src.auth.dtos.tokens import Token
from src.db.repository.UserProjectLinkRepository import UserProjectLinkRepository

class AuthService:
  def __init__(
      self, 
      authRepository : AuthRepository, 
      crypto: CryptContext, 
      userOrgLinkRepo: UserOrgLinkRepository,
      userProjectLinkRepo: UserProjectLinkRepository
    ):
    self.repo = authRepository
    self.crypto = crypto
    self.userOrgLinkRepo = userOrgLinkRepo
    self.userProjectLinkRepo = userProjectLinkRepo

  def login(self, reqDto: LoginRequestDto) -> str:
    dbUser: User = self.repo.getUserByEmail(reqDto.email)

    if not dbUser:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found by this email!")
    
    if not dbUser.verified:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not verified yet!")
  
    isPasswordVerified = self.crypto.verify(reqDto.password, dbUser.password)

    if not isPasswordVerified:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password!")
    
    activeOrgs = []
    for org in dbUser.orgs:
      link = self.userOrgLinkRepo.get(dbUser.id, org.id)
      
      if link and not link.disabled:
        activeOrgs.append({
        "id": org.id,
        "name": org.name
      })
    
    if not activeOrgs:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Your account is disabled in all organizations!"
      )

    activeProjects = []
    for project in dbUser.projects:
      link = self.userProjectLinkRepo.get(dbUser.id, project.id)
      
      if link and not link.disabled:
        activeProjects.append({
        "id": project.id,
        "name": project.name
      })
    if not activeProjects:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="You do not have any project assigned!"
      )

    token = self.generateToken(dbUser, activeOrgs, activeProjects)

    res = LoginResponseDto(accessToken=token.accessToken, refreshToken=token.refreshToken)
    return res
  
  def refresh(self, authRefreshRequestDto: AuthRefreshRequestDto)-> AuthRefreshResponseDto:
    refreshToken = authRefreshRequestDto.refreshToken

    try:
      payload = jwt.decode(refreshToken, Config.getValByKey("SECRET_KEY"), Config.getValByKey("ALGORITHM"))
    except ExpiredSignatureError as e:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired!")

    payloadEmail = payload.get("sub")

    if payloadEmail is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No email found on token payload!")
    
    dbUser: User = self.repo.getUserByEmail(payloadEmail)

    if not dbUser:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found by this email!")
    
    token = self.generateToken(dbUser)

    res  = AuthRefreshResponseDto(accessToken=token.accessToken,refreshToken=token.refreshToken)
    return res
  
  def generateToken(self, user: User, orgs, projects)->Token:
    accessTokenExpires = datetime.now(timezone.utc) + timedelta(minutes=int(Config.getValByKey("ACCESS_TOKEN_EXPIRE_MINUTES")))
    refreshTokenExpires = datetime.now(timezone.utc) + timedelta(minutes=int(Config.getValByKey("REFRESH_TOKEN_EXPIRE_MINUTES")))

    accessToken = jwt.encode({
      "sub" : user.email,
      "userId": user.id,
      "orgs" : orgs,
      "projects": projects,
      "exp" : accessTokenExpires
    }, Config.getValByKey("SECRET_KEY"), Config.getValByKey("ALGORITHM"))

    refreshToken = jwt.encode({
      "sub" : user.email,
      "userId": user.id,
      "orgs" : orgs,
      "projects": projects,
      "exp" : refreshTokenExpires
    }, Config.getValByKey("SECRET_KEY"), Config.getValByKey("ALGORITHM"))
    
    return Token(accessToken=accessToken,refreshToken=refreshToken)

  
