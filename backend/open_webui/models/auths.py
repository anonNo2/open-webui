import logging
import uuid
import jwt
from datetime import UTC, datetime, timedelta
from typing import Optional, Union, List, Dict

from open_webui.internal.db import Base, get_db
from open_webui.models.users import UserModel, Users
from open_webui.env import SRC_LOG_LEVELS
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, String, Text
from open_webui.utils.auth import verify_password
from open_webui.env import SRC_LOG_LEVELS, ENABLE_AUTO_AUTH, WEBUI_SECRET_KEY
from fastapi import Request, HTTPException, status
from open_webui.utils.misc import parse_duration

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# GUEST MODE
####################
SESSION_SECRET = WEBUI_SECRET_KEY
ALGORITHM = "HS256"


####################
# DB MODEL
####################


class Auth(Base):
    __tablename__ = "auth"

    id = Column(String, primary_key=True)
    email = Column(String)
    password = Column(Text)
    active = Column(Boolean)


class AuthModel(BaseModel):
    id: str
    email: str
    password: str
    active: bool = True


####################
# Forms
####################


class Token(BaseModel):
    token: str
    token_type: str


class ApiKey(BaseModel):
    api_key: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    profile_image_url: str


class SigninResponse(Token, UserResponse):
    pass


class SigninForm(BaseModel):
    email: str
    password: str


class LdapForm(BaseModel):
    user: str
    password: str


class ProfileImageUrlForm(BaseModel):
    profile_image_url: str


class UpdateProfileForm(BaseModel):
    profile_image_url: str
    name: str


class UpdatePasswordForm(BaseModel):
    password: str
    new_password: str


class SignupForm(BaseModel):
    name: str
    email: str
    password: str
    profile_image_url: Optional[str] = "/user.png"


class AddUserForm(SignupForm):
    role: Optional[str] = "pending"


class AuthsTable:
    def insert_new_auth(
        self,
        email: str,
        password: str,
        name: str,
        profile_image_url: str = "/user.png",
        role: str = "pending",
        oauth_sub: Optional[str] = None,
    ) -> Optional[UserModel]:
        with get_db() as db:
            log.info("insert_new_auth")

            id = str(uuid.uuid4())

            auth = AuthModel(**{"id": id, "email": email, "password": password, "active": True})
            result = Auth(**auth.model_dump())
            db.add(result)

            user = Users.insert_new_user(id, name, email, profile_image_url, role, oauth_sub)

            db.commit()
            db.refresh(result)

            if result and user:
                return user
            else:
                return None

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        log.info(f"authenticate_user: {email}")
        try:
            with get_db() as db:
                auth = db.query(Auth).filter_by(email=email, active=True).first()
                if auth:
                    if verify_password(password, auth.password):
                        user = Users.get_user_by_id(auth.id)
                        return user
                    else:
                        return None
                else:
                    return None
        except Exception:
            return None

    def authenticate_user_by_api_key(self, api_key: str) -> Optional[UserModel]:
        log.info(f"authenticate_user_by_api_key: {api_key}")
        # if no api_key, return None
        if not api_key:
            return None

        try:
            user = Users.get_user_by_api_key(api_key)
            return user if user else None
        except Exception:
            return False

    # Other Code
    def auto_auth(self, request: Request):
        log.debug("Starting auto auth process")

        random_id = str(uuid.uuid4())[:8]
        auto_email = f"auto_user_{random_id}@auto.local"
        # 访客模式
        auto_name = f"Guest {random_id}"

        auto_password = str(uuid.uuid4())

        try:
            log.info(f"Creating auto user with email: {auto_email}")

            user = self.insert_new_auth(
                email=auto_email,
                password=auto_password,
                name=auto_name,
                role="user",
            )

            if not user:
                log.error("Failed to create auto user")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create auto user",
                )

            log.info(f"Successfully created auto user with ID: {user.id}")

            def create_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
                payload = data.copy()

                if expires_delta:
                    expire = datetime.now(UTC) + expires_delta
                    payload.update({"exp": expire})

                encoded_jwt = jwt.encode(payload, SESSION_SECRET, algorithm=ALGORITHM)
                return encoded_jwt

            token = create_token(
                data={"id": user.id},
                expires_delta=parse_duration("-1"),
            )

            return {
                "status": True,
                "token": token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                },
            }
        except Exception as e:
            log.exception(f"Auto auth failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Auto auth failed: {str(e)}",
            )

    def authenticate_user_by_trusted_header(self, request: Request) -> Optional[UserModel]:
        # log.info(f"authenticate_user_by_trusted_header: {email}")
        # try:
        #     with get_db() as db:
        #         auth = db.query(Auth).filter_by(email=email, active=True).first()
        #         if auth:
        #             user = Users.get_user_by_id(auth.id)
        #             return user
        # except Exception:
        #     return None
        if ENABLE_AUTO_AUTH:
            log.info("Auto auth enabled, creating new user")
            auth_result = self.auto_auth(request)
            if auth_result and auth_result["status"]:
                user = Users.get_user_by_id(auth_result["user"]["id"])
                log.info(f"Created new auto user: {user.id}")
                return user
        return None

    def update_user_password_by_id(self, id: str, new_password: str) -> bool:
        try:
            with get_db() as db:
                result = db.query(Auth).filter_by(id=id).update({"password": new_password})
                db.commit()
                return True if result == 1 else False
        except Exception:
            return False

    def update_email_by_id(self, id: str, email: str) -> bool:
        try:
            with get_db() as db:
                result = db.query(Auth).filter_by(id=id).update({"email": email})
                db.commit()
                return True if result == 1 else False
        except Exception:
            return False

    def delete_auth_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                # Delete User
                result = Users.delete_user_by_id(id)

                if result:
                    db.query(Auth).filter_by(id=id).delete()
                    db.commit()

                    return True
                else:
                    return False
        except Exception:
            return False


Auths = AuthsTable()
