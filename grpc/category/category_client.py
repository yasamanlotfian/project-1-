
import grpc

import category_pb2
import category_pb2_grpc


def run():

    channel = grpc.insecure_channel(
        "localhost:5057"
    )

    stub = category_pb2_grpc.CategoryServiceStub(
        channel
    )

    try:

        response = stub.GetCategories(
            category_pb2.Empty()
        )

        print("Categories:")

        for category in response.categories:
            print("ID:", category.id)
            print("Name:", category.name)
            print("Created At:", category.created_at)
            print("Updated At:", category.updated_at)

        response = stub.GetCategory(
            category_pb2.CategoryRequest(
                category_id=1
            )
        )

        print("GetCategory:")
        print("ID:", response.id)
        print("Name:", response.name)

        response = stub.CreateCategory(
            category_pb2.CreateCategoryRequest(
                name="Python"
            )
        )

        print("Created Category:")
        print("ID:", response.id)
        print("Name:", response.name)

        created_category_id = response.id

        response = stub.UpdateCategory(
            category_pb2.UpdateCategoryRequest(
                category_id=created_category_id,
                name="Python gRPC"
            )
        )

        print("Updated Category:")
        print("ID:", response.id)
        print("Name:", response.name)

        response = stub.DeleteCategory(
            category_pb2.DeleteCategoryRequest(
                category_id=created_category_id
            )
        )

        print("Deleted Category:")
        print("ID:", response.id)
        print("Name:", response.name)

    finally:
        channel.close()


if __name__ == "__main__":
    run()
