
import sys
from concurrent import futures

import grpc
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, r"C:\Users\lotus\project")
sys.path.insert(0, r"C:\Users\lotus\project\grpc\tag")

from database import SessionLocal
from tables.tag import Tag

import tag_pb2
import tag_pb2_grpc


class TagService(
    tag_pb2_grpc.TagServiceServicer
):

    def make_tag_response(self, tag):
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

    def GetTags(self, request, context):
        print("GetTags request received")

        db = SessionLocal()

        try:
            tags = (
                db.query(Tag)
                .order_by(Tag.id)
                .all()
            )

            response = tag_pb2.TagList(
                tags=[
                    self.make_tag_response(tag)
                    for tag in tags
                ]
            )

            return response

        except Exception as exc:
            print(f"GetTags error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve tags",
            )

        finally:
            db.close()

    def GetTag(self, request, context):
        print("GetTag request received")

        db = SessionLocal()

        try:
            tag = (
                db.query(Tag)
                .filter(Tag.id == request.tag_id)
                .first()
            )

        except Exception as exc:
            print(f"GetTag database error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve tag",
            )

        finally:
            db.close()

        if tag is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Tag not found",
            )

        return self.make_tag_response(tag)

    def CreateTag(self, request, context):
        print("CreateTag request received")

        name = request.name.strip()

        if not name:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Tag name is required",
            )

        db = SessionLocal()

        try:
            tag = Tag(name=name)

            db.add(tag)
            db.commit()
            db.refresh(tag)

            response = self.make_tag_response(tag)

            return response

        except IntegrityError as exc:
            db.rollback()
            print(f"CreateTag integrity error: {exc}")

            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Tag name already exists",
            )

        except Exception as exc:
            db.rollback()
            print(f"CreateTag error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to create tag",
            )

        finally:
            db.close()

    def UpdateTag(self, request, context):
        print("UpdateTag request received")

        name = request.name.strip()

        if not name:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Tag name is required",
            )

        db = SessionLocal()

        try:
            tag = (
                db.query(Tag)
                .filter(Tag.id == request.tag_id)
                .first()
            )

        except Exception as exc:
            print(f"UpdateTag query error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve tag",
            )

        if tag is None:
            db.close()

            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Tag not found",
            )

        try:
            tag.name = name

            db.commit()
            db.refresh(tag)

            response = self.make_tag_response(tag)

            return response

        except IntegrityError as exc:
            db.rollback()
            print(f"UpdateTag integrity error: {exc}")

            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Tag name already exists",
            )

        except Exception as exc:
            db.rollback()
            print(f"UpdateTag error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to update tag",
            )

        finally:
            db.close()

    def DeleteTag(self, request, context):
        print("DeleteTag request received")

        db = SessionLocal()

        try:
            tag = (
                db.query(Tag)
                .filter(Tag.id == request.tag_id)
                .first()
            )

        except Exception as exc:
            print(f"DeleteTag query error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve tag",
            )

        if tag is None:
            db.close()

            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Tag not found",
            )

        try:
            response = self.make_tag_response(tag)

            db.delete(tag)
            db.commit()

            return response

        except IntegrityError as exc:
            db.rollback()
            print(f"DeleteTag integrity error: {exc}")

            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                "Tag cannot be deleted because it is in use",
            )

        except Exception as exc:
            db.rollback()
            print(f"DeleteTag error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to delete tag",
            )

        finally:
            db.close()

    def GetTagsByIds(self, request, context):
        print("GetTagsByIds request received")

        db = SessionLocal()

        try:
            ids = list(set(request.ids))

            if not ids:
                return tag_pb2.TagList()

            tags = (
                db.query(Tag)
                .filter(Tag.id.in_(ids))
                .order_by(Tag.id)
                .all()
            )

            return tag_pb2.TagList(
                tags=[
                    self.make_tag_response(tag)
                    for tag in tags
                ]
            )

        except Exception as exc:
            print(f"GetTagsByIds error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve tags by IDs",
            )

        finally:
            db.close()


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    tag_pb2_grpc.add_TagServiceServicer_to_server(
        TagService(),
        server,
    )

    port = server.add_insecure_port("[::]:5056")

    if port == 0:
        raise RuntimeError(
            "Could not bind gRPC server to port 5056"
        )

    server.start()
    print("Tag gRPC Server running on port 5056")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=2)


if __name__ == "__main__":
    serve()
