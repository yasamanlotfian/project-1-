import grpc
from datetime import timezone

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from google.protobuf.timestamp_pb2 import Timestamp

from database import SessionLocal
from tables.tag import Tag

import tag_pb2
import tag_pb2_grpc


def to_timestamp(value):
    timestamp = Timestamp()

    if value is not None:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        timestamp.FromDatetime(value)

    return timestamp


def to_proto(tag):
    return tag_pb2.Tag(
        id=tag.id,
        name=tag.name,
        created_at=to_timestamp(tag.created_at),
        updated_at=to_timestamp(tag.updated_at),
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

            return tag_pb2.TagResponse(
                tag=to_proto(tag)
            )

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
                Tag.id == request.id
            ).first()

            if tag is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Tag not found",
                )

            return tag_pb2.TagResponse(
                tag=to_proto(tag)
            )

        finally:
            db.close()

    def ListTags(self, request, context):
        db: Session = SessionLocal()

        try:
            tags = db.query(Tag).order_by(Tag.id).all()

            return tag_pb2.TagListResponse(
                tags=[to_proto(tag) for tag in tags]
            )

        finally:
            db.close()

    def GetTagsByIds(self, request, context):
        db: Session = SessionLocal()

        try:
            ids = list(dict.fromkeys(request.ids))

            if not ids:
                return tag_pb2.TagListResponse()

            tags = db.query(Tag).filter(
                Tag.id.in_(ids)
            ).all()

            tags_by_id = {tag.id: tag for tag in tags}

            return tag_pb2.TagListResponse(
                tags=[
                    to_proto(tags_by_id[tag_id])
                    for tag_id in ids
                    if tag_id in tags_by_id
                ]
            )

        finally:
            db.close()

    def UpdateTag(self, request, context):
        db: Session = SessionLocal()

        try:
            tag = db.query(Tag).filter(
                Tag.id == request.id
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

            duplicate = db.query(Tag).filter(
                Tag.name == name,
                Tag.id != request.id,
            ).first()

            if duplicate:
                context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    "Tag already exists",
                )

            tag.name = name
            db.commit()
            db.refresh(tag)

            return tag_pb2.TagResponse(
                tag=to_proto(tag)
            )

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
                Tag.id == request.id
            ).first()

            if tag is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Tag not found",
                )

            db.delete(tag)
            db.commit()

            return tag_pb2.DeleteTagResponse(
                success=True,
                message="Tag deleted successfully",
            )

        finally:
            db.close()