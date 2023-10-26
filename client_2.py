import grpc
import rx
from rx import operators as ops
from my_pb2 import FileRequest
from my_pb2_grpc import FileTransferServiceStub
from datloader2 import Dataloader2
from os.path import join
import math
import time


def zapros(images, path_l, path_r, i):
    with open(join(path_l, images.filenames1[i]), 'rb') as f1, open(join(path_r, images.filenames2[i]), 'rb') as f2:
        image1_bytes = f1.read()
        image2_bytes = f2.read()

    request = FileRequest(
        image_1=image1_bytes,
        image_2=image2_bytes,
        filename1=str(images.filenames1[i]),
        filename2=str(images.filenames2[i]))
    return request


def get_client_stream_requests(images, path_l, path_r):
    return rx.from_(
        (zapros(images, path_l, path_r, i) for i in range(len(images.filenames1)))
    )


def run_client_case4(images, path_l, path_r, stub):
    start_time = time.time()  # Засекаем начальное время перед отправкой

    request_stream = get_client_stream_requests(images, path_l, path_r)

    response_observable = stub.Case4(request_stream)

    # Создаем собственный Observable для подписки на ответы
    response_observable = rx.from_(
        (response for response in response_observable)
    )

    # Подписываемся на Observable ответов и обрабатываем их
    response_observable.subscribe(
        on_next=lambda response: print("response - ", response),
        on_error=lambda error: print("Error:", error),
        on_completed=lambda: print("All responses received.")
    )

    end_time = time.time()  # Засекаем время после получения ответов
    res_time = end_time - start_time
    print(f"Общее время передачи для всех изображений: {res_time} секунд")


def main():
    max_message_length = 2000 * 1024 * 1024
    channel = grpc.insecure_channel('localhost:50052', options=(('grpc.max_send_message_length', max_message_length),))
    stub = FileTransferServiceStub(channel)
    path_l = "/Users/aroslavsapoval/myProjects/images_grpc_1980/left"
    path_r = "/Users/aroslavsapoval/myProjects/images_grpc_1980/right"
    images = Dataloader2(path_l, path_r)

    run_client_case4(images, path_l, path_r, stub)


if __name__ == '__main__':
    main()
