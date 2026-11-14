
import sys
from pathlib import Path

import grpc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CATEGORY_GRPC_DIR = PROJECT_ROOT / "grpc" / "category"

if str(CATEGORY_GRPC_DIR) not in sys.path:
    sys.path.insert(0, str(CATEGORY_GRPC_DIR))

import category_pb2
import category_pb2_grpc


class CategoryServiceClient:

    def __init__(self, address="localhost:5057"):
        self.channel = grpc.insecure_channel(address)
        self.stub = category_pb2_grpc.CategoryServiceStub(
            self.channel
        )

    def get_categories(self, metadata=None):
        return self.stub.GetCategories(
            category_pb2.Empty(),
            metadata=metadata,
            timeout=10,
        )

    def get_category(self, category_id: int, metadata=None):
        request = category_pb2.CategoryRequest(
            category_id=category_id
        )

        return self.stub.GetCategory(
            request,
            metadata=metadata,
            timeout=10,
        )

    def create_category(
        self,
        name: str,
        metadata=None,
    ):
        request = category_pb2.CreateCategoryRequest(
            name=name,
        )

        return self.stub.CreateCategory(
            request,
            metadata=metadata,
            timeout=10,
        )

    def update_category(
        self,
        category_id: int,
        name: str,
        metadata=None,
    ):
        request = category_pb2.UpdateCategoryRequest(
            category_id=category_id,
            name=name,
        )

        return self.stub.UpdateCategory(
            request,
            metadata=metadata,
            timeout=10,
        )

    def delete_category(
        self,
        category_id: int,
        metadata=None,
    ):
        request = category_pb2.DeleteCategoryRequest(
            category_id=category_id
        )

        return self.stub.DeleteCategory(
            request,
            metadata=metadata,
            timeout=10,
        )

    def close(self):
        self.channel.close()
