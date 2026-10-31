
import sys
from concurrent import futures

import grpc
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, r"C:\Users\lotus\project")
sys.path.insert(0, r"C:\Users\lotus\project\grpc\category")

from database import SessionLocal
from tables.category import Category

import category_pb2
import category_pb2_grpc


class CategoryService(
    category_pb2_grpc.CategoryServiceServicer
):

    def make_category_response(self, category):
        return category_pb2.CategoryResponse(
            id=category.id,
            name=category.name,
            created_at=(
                category.created_at.isoformat()
                if category.created_at else ""
            ),
            updated_at=(
                category.updated_at.isoformat()
                if category.updated_at else ""
            ),
        )

    def GetCategories(self, request, context):
        print("GetCategories request received")

        db = SessionLocal()

        try:
            categories = (
                db.query(Category)
                .order_by(Category.id)
                .all()
            )

            return category_pb2.CategoryList(
                categories=[
                    self.make_category_response(category)
                    for category in categories
                ]
            )

        except Exception as exc:
            print(f"GetCategories error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve categories",
            )

        finally:
            db.close()

    def GetCategory(self, request, context):
        print("GetCategory request received")

        db = SessionLocal()

        try:
            category = (
                db.query(Category)
                .filter(Category.id == request.category_id)
                .first()
            )

            if category is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Category not found",
                )

            return self.make_category_response(category)

        except Exception as exc:
            if isinstance(exc, grpc.RpcError):
                raise

            print(f"GetCategory error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve category",
            )

        finally:
            db.close()

    def CreateCategory(self, request, context):
        print("CreateCategory request received")

        db = SessionLocal()

        try:
            name = request.name.strip()

            if not name:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Category name is required",
                )

            category = Category(name=name)

            db.add(category)
            db.commit()
            db.refresh(category)

            return self.make_category_response(category)

        except IntegrityError:
            db.rollback()

            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Category name already exists",
            )

        except Exception as exc:
            db.rollback()

            if isinstance(exc, grpc.RpcError):
                raise

            print(f"CreateCategory error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to create category",
            )

        finally:
            db.close()

    def UpdateCategory(self, request, context):
        print("UpdateCategory request received")

        db = SessionLocal()

        try:
            category = (
                db.query(Category)
                .filter(Category.id == request.category_id)
                .first()
            )

            if category is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Category not found",
                )

            name = request.name.strip()

            if not name:
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Category name is required",
                )

            category.name = name

            db.commit()
            db.refresh(category)

            return self.make_category_response(category)

        except IntegrityError:
            db.rollback()

            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Category name already exists",
            )

        except Exception as exc:
            db.rollback()

            if isinstance(exc, grpc.RpcError):
                raise

            print(f"UpdateCategory error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to update category",
            )

        finally:
            db.close()

    def DeleteCategory(self, request, context):
        print("DeleteCategory request received")

        db = SessionLocal()

        try:
            category = (
                db.query(Category)
                .filter(Category.id == request.category_id)
                .first()
            )

            if category is None:
                context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Category not found",
                )

            response = self.make_category_response(category)

            db.delete(category)
            db.commit()

            return response

        except Exception as exc:
            db.rollback()

            if isinstance(exc, grpc.RpcError):
                raise

            print(f"DeleteCategory error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to delete category",
            )

        finally:
            db.close()


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    category_pb2_grpc.add_CategoryServiceServicer_to_server(
        CategoryService(),
        server,
    )

    port = server.add_insecure_port("[::]:5057")

    if port == 0:
        raise RuntimeError(
            "Could not bind gRPC server to port 5057"
        )

    server.start()
    print("Category gRPC Server running on port 5057")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=2)


if __name__ == "__main__":
    serve()
