import grpc

import blog_pb2
import blog_pb2_grpc


def run():

    channel = grpc.insecure_channel(
        "localhost:5053"
    )

    stub = blog_pb2_grpc.BlogServiceStub(
        channel
    )


    response = stub.GetBlogs(
        blog_pb2.Empty()
    )


    for blog in response.blogs:
        print("ID:", blog.id)
        print("Title:", blog.title)
        print("Slug:", blog.slug)
        print("Description:", blog.description)
        print("Content:", blog.content)

  

    response = stub.GetBlog(
        blog_pb2.BlogRequest(
            blog_id=1
        )
    )

    print("ID:", response.id)
    print("Title:", response.title)
    print("Slug:", response.slug)
    print("Description:", response.description)
    print("Content:", response.content)



    response = stub.CreateBlog(
        blog_pb2.CreateBlogRequest(
            title="My gRPC Blog",
            slug="my-grpc-blog",
            description="Blog created with gRPC",
            content="This blog was created using gRPC."
        )
    )

    

    print("ID:", response.id)
    print("Title:", response.title)
    print("Slug:", response.slug)
    print("Description:", response.description)
    print("Content:", response.content)



    response = stub.DeleteBlog(
        blog_pb2.DeleteBlogRequest(
            blog_id=response.id
        )
    )

   

    print("ID:", response.id)
    print("Title:", response.title)


if __name__ == "__main__":
    run()