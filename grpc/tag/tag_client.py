
import grpc

import tag_pb2
import tag_pb2_grpc


def run():

    channel = grpc.insecure_channel(
        "localhost:5056"
    )

    stub = tag_pb2_grpc.TagServiceStub(
        channel
    )

    try:

        response = stub.GetTags(
            tag_pb2.Empty()
        )

        for tag in response.tags:
            print("ID:", tag.id)
            print("Name:", tag.name)
            print("Created At:", tag.created_at)
            print("Updated At:", tag.updated_at)

        response = stub.GetTag(
            tag_pb2.TagRequest(
                tag_id=1
            )
        )

        print("GetTag:")
        print("ID:", response.id)
        print("Name:", response.name)

        response = stub.CreateTag(
            tag_pb2.CreateTagRequest(
                name="Python"
            )
        )

        print("Created Tag:")
        print("ID:", response.id)
        print("Name:", response.name)

        created_tag_id = response.id

        response = stub.UpdateTag(
            tag_pb2.UpdateTagRequest(
                tag_id=created_tag_id,
                name="Python gRPC"
            )
        )

        print("Updated Tag:")
        print("ID:", response.id)
        print("Name:", response.name)

        response = stub.GetTagsByIds(
            tag_pb2.GetTagsByIdsRequest(
                ids=[1, created_tag_id]
            )
        )

        print("Tags By IDs:")

        for tag in response.tags:
            print("ID:", tag.id)
            print("Name:", tag.name)

        response = stub.DeleteTag(
            tag_pb2.DeleteTagRequest(
                tag_id=created_tag_id
            )
        )

        print("Deleted Tag:")
        print("ID:", response.id)
        print("Name:", response.name)

    finally:
        channel.close()


if __name__ == "__main__":
    run()
