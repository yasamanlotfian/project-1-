
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

            response = category_pb2.CategoryList(
                categories=[
                    self.make_category_response(category)
                    for category in categories
                ]
            )

            return response

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

        except Exception as exc:
            print(f"GetCategory database error: {exc}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve category",
            )

        finally:
            db.close()

        if category is None:
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Category not found",
            )

        return self.make_category_response(category)

    def CreateCategory(self, request, context):
        print("CreateCategory request received")

        name = request.name.strip()

        if not name:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Category name is required",
            )

        db = SessionLocal()

        try:
            category = Category(name=name)

            db.add(category)
            db.commit()
            db.refresh(category)

            response = self.make_category_response(category)

            return response

        except IntegrityError:
            db.rollback()
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Category name already exists",
            )

        except Exception as exc:
            db.rollback()
            print(f"CreateCategory error: {exc}")

            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to create category",
            )

        finally:
            db.close()

    def UpdateCategory(self, request, context):
        print("UpdateCategory request received")

        name = request.name.strip()

        if not name:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                "Category name is required",
            )

        db = SessionLocal()

        try:
            category = (
                db.query(Category)
                .filter(Category.id == request.category_id)
                .first()
            )

            if category is None:
                category_not_found = True
            else:
                category_not_found = False

        except Exception as exc:
            print(f"UpdateCategory query error: {exc}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve category",
            )

        if category_not_found:
            db.close()
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Category not found",
            )

        try:
            category.name = name

            db.commit()
            db.refresh(category)

            response = self.make_category_response(category)

            return response

        except IntegrityError:
            db.rollback()
            context.abort(
                grpc.StatusCode.ALREADY_EXISTS,
                "Category name already exists",
            )

        except Exception as exc:
            db.rollback()
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
                category_not_found = True
                response = None
            else:
                category_not_found = False
                response = self.make_category_response(category)

        except Exception as exc:
            print(f"DeleteCategory query error: {exc}")
            context.abort(
                grpc.StatusCode.INTERNAL,
                "Failed to retrieve category",
            )

        if category_not_found:
            db.close()
            context.abort(
                grpc.StatusCode.NOT_FOUND,
                "Category not found",
            )

        try:
            db.delete(category)
            db.commit()

            return response

        except IntegrityError:
            db.rollback()
            context.abort(
                grpc.StatusCode.FAILED_PRECONDITION,
                "Category cannot be deleted because it is in use",
            )

        except Exception as exc:
            db.rollback()
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
