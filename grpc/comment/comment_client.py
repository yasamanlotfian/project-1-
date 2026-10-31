
import grpc

import comment_pb2
import comment_pb2_grpc


def run():

    channel = grpc.insecure_channel(
        "localhost:5054"
    )

    stub = comment_pb2_grpc.CommentServiceStub(
        channel
    )

    # GetComments
    response = stub.GetComments(
        comment_pb2.Empty()
    )

    for comment in response.comments:

        print("ID:", comment.id)
        print("Name:", comment.name)
        print("Blog ID:", comment.blog_id)
        print("Content:", comment.content)
        print("Created At:", comment.created_at)

    # GetComment
    response = stub.GetComment(
        comment_pb2.CommentRequest(
            comment_id=1
        )
    )

    print("ID:", response.id)
    print("Name:", response.name)
    print("Blog ID:", response.blog_id)
    print("Content:", response.content)
    print("Created At:", response.created_at)

    # CreateComment
    response = stub.CreateComment(
        comment_pb2.CreateCommentRequest(
            name="Test User",
            blog_id=1,
            content="Comment created with gRPC"
        )
    )

    print("ID:", response.id)
    print("Name:", response.name)
    print("Blog ID:", response.blog_id)
    print("Content:", response.content)

    # UpdateComment
    response = stub.UpdateComment(
        comment_pb2.UpdateCommentRequest(
            comment_id=response.id,
            name="Updated User",
            content="Comment updated with gRPC"
        )
    )

    print("Updated ID:", response.id)
    print("Updated Name:", response.name)
    print("Updated Content:", response.content)

    # DeleteComment
    response = stub.DeleteComment(
        comment_pb2.DeleteCommentRequest(
            comment_id=response.id
        )
    )

    print("Deleted ID:", response.id)
    print("Deleted Content:", response.content)

    channel.close()


if __name__ == "__main__":
    run()
