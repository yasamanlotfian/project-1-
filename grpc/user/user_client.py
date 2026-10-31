
import grpc

import user_pb2
import user_pb2_grpc


def run():

    channel = grpc.insecure_channel(
        "localhost:5051"
    )

    stub = user_pb2_grpc.UserServiceStub(channel)


    response = stub.GetUsers(
        user_pb2.Empty()
    )

    for user in response.users:
        print(
            f"ID: {user.id} | "
            f"Username: {user.username} | "
            f"Email: {user.email} | "
            f"Role: {user.role}"
        )

    response = stub.GetUser(
        user_pb2.UserRequest(
            user_id=1
        )
    )

    print(f"ID: {response.id}")
    print(f"Username: {response.username}")
    print(f"Email: {response.email}")
    print(f"Role: {response.role}")
    print(f"Created At: {response.created_at}")
    print(f"Updated At: {response.updated_at}")

 
    response = stub.CreateUser(
        user_pb2.CreateUserRequest(
            username="grpc_user",
            email="grpc@example.com",
            password="123456"
        )
    )

    print(f"ID: {response.id}")
    print(f"Username: {response.username}")
    print(f"Email: {response.email}")
    print(f"Role: {response.role}")

    new_user_id = response.id



    response = stub.UpdateUser(
        user_pb2.UpdateUserRequest(
            user_id=new_user_id,
            username="grpc_user_updated",
            email="updated@example.com",
            password="654321",
            role="user"
        )
    )

    print(f"ID: {response.id}")
    print(f"Username: {response.username}")
    print(f"Email: {response.email}")
    print(f"Role: {response.role}")


    response = stub.DeleteUser(
        user_pb2.UserRequest(
            user_id=new_user_id
        )
    )

    print(f"Success: {response.success}")
    print(f"Message: {response.message}")

    channel.close()


if __name__ == "__main__":
    run()
