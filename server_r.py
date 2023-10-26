import time

import grpc
from concurrent import futures
from PIL import Image
from io import BytesIO
import my_pb2
import my_pb2_grpc
import os


class FileTransferService(my_pb2_grpc.FileTransferServiceServicer):

    def __init__(self):
        self.image_name1 = None
        self.image_name2 = None
        self.merged_image_name = None

    def work_with_img(self, request, context, case_nom):
        time.sleep(1)
        image1 = Image.open(BytesIO(request.image_1))
        image2 = Image.open(BytesIO(request.image_2))
        self.image_name1 = request.filename1
        self.image_name2 = request.filename2

        merged_image = Image.new("RGB", (image1.width + image2.width, max(image1.height, image2.height)))
        merged_image.paste(image1, (0, 0))
        merged_image.paste(image2, (image1.width, 0))
        self.merged_image_name = self.image_name1 + "_" + self.image_name2

        output_folder = f"merged_image_case_{case_nom}"
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, self.merged_image_name)
        merged_image.save(output_path, format="PNG")

    def Case1(self, request, context):
        # self.work_with_img(request, context, case_nom=1)
        response = my_pb2.FileResponse(message="Images were successfully transferred to the server using 1 method")
        return response

    def Case2(self, request_iterator, context):
        all_img = []
        for request in request_iterator:
            all_img.append(request.filename1)
            # self.work_with_img(request, context, case_nom=2)
            # all_img.append(self.merged_image_name)

        response = my_pb2.FileResponse(message=f"Images were successfully transferred to the server using 2 method. You have sent {len(all_img)}")
        return response

    def Case3(self, request, context):
        # self.work_with_img(request, context, case_nom=3)
        for i in range(3):
            response = my_pb2.FileResponse(message=f"Images were successfully transferred to the server using 3 method {i + 1}")
            yield response

    def Case4(self, request_iterator, context):
        for request in request_iterator:
            # self.work_with_img(request, context, case_nom=4)
            response = my_pb2.FileResponse(
                message=f"Images {self.image_name1} and {self.image_name2} were successfully transferred to the server using 4 method.")
            yield response


def run_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[('grpc.max_receive_message_length', 2000 * 1024 * 1024)])
    my_pb2_grpc.add_FileTransferServiceServicer_to_server(FileTransferService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Сервер запущен на порту 50052...")
    server.wait_for_termination()


if __name__ == '__main__':
    run_server()
