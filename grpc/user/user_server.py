
import sys
import os
from concurrent import futures
from datetime import datetime, timedelta, timezone

import grpc
import jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from dotenv import load_dotenv

sys.path.insert(0, r"C:\Users\lotus\project")
sys.path.insert(0, r"C:\Users\lotus\project\grpc\user")

from database import SessionLocal

# Load all related SQLAlchemy models before handling requests
from tables.user import User
from tables.blog import Blog
from tables.category import Category
from tables.file import File
from tables.tag import Tag
from tables.blog_tag import BlogTag

import user_pb2
import user_pb2_grpc


pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto"
)


load_dotenv(r"C:\Users\lotus\project\.env")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES", "1")
)

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing from .env"
    )


class UserService(user_pb2_grpc.UserServiceServicer):

    def Login(self, request, context):
        db: Session = SessionLocal()

        try:
            user = (
                db.query(User)
                .filter(User.username == request.username)
                .first()
            )

            if not user:
                context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    "Invalid username or password"
                )

            try:
                password_valid = pwd_context.verify(
                    request.password,
                    user.password
                )
            except (ValueError, TypeError):
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Password could not be processed. "
                    "Please reset your password."
                )

            if not password_valid:
                context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    "Invalid username or password"
                )

            # Upgrade an old bcrypt hash after successful login.
            if pwd_context.needs_update(user.password):
                user.password = pwd_context.hash(
                    request.password
                )
                db.commit()

            payload = {
                "sub": str(user.id),
                "username": user.username,
                "role": user.role,
                "exp": datetime.now(timezone.utc)
                + timedelta(
                    minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                )
            }

            access_token = jwt.encode(
                payload,
                SECRET_KEY,
                algorithm=ALGORITHM
            )

            return user_pb2.LoginResponse(
                access_token=access_token,
                token_type="Bearer"
            )

        finally:
            db.close()

    def GetUsers(self, request, context):
        db: Session = SessionLocal()

        try:
            users = db.query(User).all()

            result = [
                user_pb2.UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    role=user.role
                )
                for user in users
            ]

            return user_pb2.UserList(users=result)

        finally:
            db.close()

    def GetUser(self, request, context):
        db: Session = SessionLocal()

        try:
            user = (
                db.query(User)
                .filter(User.id == request.user_id)
                .first()
            )

            if not user:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "User not found"
                )

            return user_pb2.UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role
            )

        finally:
            db.close()

    def CreateUser(self, request, context):
        db: Session = SessionLocal()

        try:
            if not request.password:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Password is required"
                )

            username_exists = (
                db.query(User)
                .filter(User.username == request.username)
                .first()
            )

            if username_exists:
                context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    "Username already exists"
                )

            email_exists = (
                db.query(User)
                .filter(User.email == request.email)
                .first()
            )

            if email_exists:
                context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    "Email already exists"
                )

            hashed_password = pwd_context.hash(
                request.password
            )

            new_user = User(
                username=request.username,
                email=request.email,
                password=hashed_password,
                role="user"
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return user_pb2.UserResponse(
                id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                role=new_user.role
            )

        except grpc.RpcError:
            raise

        finally:
            db.close()

    def UpdateUser(self, request, context):
        db: Session = SessionLocal()

        try:
            user = (
                db.query(User)
                .filter(User.id == request.user_id)
                .first()
            )

            if not user:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "User not found"
                )

            if request.username:
                username_exists = (
                    db.query(User)
                    .filter(
                        User.username == request.username,
                        User.id != request.user_id
                    )
                    .first()
                )

                if username_exists:
                    context.abort(
                        grpc.StatusCode.ALREADY_EXISTS,
                        "Username already exists"
                    )

                user.username = request.username

            if request.email:
                email_exists = (
                    db.query(User)
                    .filter(
                        User.email == request.email,
                        User.id != request.user_id
                    )
                    .first()
                )

                if email_exists:
                    context.abort(
                        grpc.StatusCode.ALREADY_EXISTS,
                        "Email already exists"
                    )

                user.email = request.email

            if request.password:
                user.password = pwd_context.hash(
                    request.password
                )

            if request.role:
                user.role = request.role

            db.commit()
            db.refresh(user)

            return user_pb2.UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role
            )

        finally:
            db.close()

    def DeleteUser(self, request, context):
        db: Session = SessionLocal()

        try:
            user = (
                db.query(User)
                .filter(User.id == request.user_id)
                .first()
            )

            if not user:
                return user_pb2.DeleteResponse(
                    success=False,
                    message="User not found"
                )

            db.delete(user)
            db.commit()

            return user_pb2.DeleteResponse(
                success=True,
                message="User deleted successfully"
            )

        finally:
            db.close()


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(),
        server
    )

    port = server.add_insecure_port("[::]:5051")

    if port == 0:
        raise RuntimeError(
            "Could not bind User gRPC server to port 5051"
        )

    server.start()

    print("User gRPC Server running on port 5051")

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
