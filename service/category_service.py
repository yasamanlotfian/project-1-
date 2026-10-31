
import grpc

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from tables.tag import Tag

import tag_pb2
import tag_pb2_grpc


def to_proto(tag):
    return tag_pb2.TagResponse(
        id=tag.id,
        name=tag.name,
        created_at=(
            tag.created_at.isoformat()
            if tag.created_at else ""
        ),
        updated_at=(
            tag.updated_at.isoformat()
            if tag.updated_at else ""
        ),
    )


class TagService(tag_pb2_grpc.TagServiceServicer):

    def CreateTag(self, request, context):
        db: Session = SessionLocal()

        try:
            name = request.name.strip()

            if not name:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Tag name is required",
                )

            tag = Tag(name=name)
            db.add(tag)
            db.commit()
            db.refresh(tag)

            return to_proto(tag)

        except IntegrityError:
            db.rollback()
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Tag already exists",
            )

        finally:
            db.close()

    def GetTag(self, request, context):
        db: Session = SessionLocal()

        try:
            tag = db.query(Tag).filter(
                Tag.id == request.tag_id
            ).first()

            if tag is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Tag not found",
                )

            return to_proto(tag)

        finally:
            db.close()

    def GetTags(self, request, context):
        db: Session = SessionLocal()

        try:
            tags = db.query(Tag).order_by(Tag.id).all()

            return tag_pb2.TagList(
                tags=[to_proto(tag) for tag in tags]
            )

        finally:
            db.close()

    def UpdateTag(self, request, context):
        db: Session = SessionLocal()

        try:
            tag = db.query(Tag).filter(
                Tag.id == request.tag_id
            ).first()

            if tag is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Tag not found",
                )

            name = request.name.strip()

            if not name:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Tag name is required",
                )

            tag.name = name
            db.commit()
            db.refresh(tag)

            return to_proto(tag)

        except IntegrityError:
            db.rollback()
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Tag already exists",
            )

        finally:
            db.close()

    def DeleteTag(self, request, context):
        db: Session = SessionLocal()

        try:
            tag = db.query(Tag).filter(
                Tag.id == request.tag_id
            ).first()

            if tag is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Tag not found",
                )

            db.delete(tag)
            db.commit()

            return tag_pb2.TagResponse(
                id=tag.id,
                name=tag.name,
                created_at="",
                updated_at="",
            )

        finally:
            db.close()
