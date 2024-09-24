
import random
import string
from concurrent import futures
from typing import Any

import datanode_pb2
import datanode_pb2_grpc
import grpc
import requests

# Variables globales
name = ""
port = ""
base_url = "http://localhost:5000"
o_datanodes = []
copy_database: dict[str, dict[str, list]] = {}

# Funciones auxiliares
# Generar nombre automaticamente
def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Logeo en el NameNode para que tenga conocimiento de que existo
def send_data_to_rest_server(name, port):
    rest_url = f"http://localhost:5000/login"
    data = {
        'name': name,
        'port': port
    }
    response = requests.post(rest_url, json=data)
    if response.status_code == 200:
        print("Login Successfull")
    else:
        print("Error, is the server running?")

def call_signal_method():
    global o_datanodes
    url = f"{base_url}/signal"
    data = {'name': name}
    response = requests.get(url, json=data)
    data = response.json()
    o_datanodes = data['nodes']
    if response.status_code == 200:
        print("Success: ", data)
    else:
        print("Error:", response.status_code, response.json())

def save_data_namenode(parameters):
    url = f"{base_url}/save_data"
    data = {
        'filename': parameters['filename'],
        'name': parameters['name'],
        'port': parameters['port'],
        'copy': parameters['copy'],
        'port_copy': parameters['port_copy']
    }
    response = requests.post(url, json=data)
    message = response.json()
    if response.status_code == 200:
        print("Success: ", message)
    else:
        print("Error:", message.status_code, response.json())

# Para hacer replicación usamos este metodo para enviar a otro datanode y replicarlo allí
def send_data_to_datanode(parameters, filename):
    data = parameters[filename]
    port = "localhost:" + str(data['port'])
    name = data['name']
    blocks = data['data']
    with grpc.insecure_channel(port) as channel:
        for block in blocks:
            stub = datanode_pb2_grpc.dataNodeStub(channel)
            request = datanode_pb2.ReceiveDataRequest(
                block = block,
                filename = filename,
                name = name
            )
            try:
                response = stub.ReceiveData(request)
                if response.success:
                    print("Data successfully sent to the DataNode.")
                else:
                    print("DataNode responded with failure.")
            except grpc.RpcError as e:
                print(f"Failed to send data: {e}")

# Servidor con gRPC

class dataNode(datanode_pb2_grpc.dataNodeServicer):
    def __init__(self):
        self.block_storage: dict[str, dict] = {}  

    def ReceiveData(self, request, context):
        global copy_database
        block = request.block
        filename = request.filename
        name = request.name
        if name in copy_database:
            if filename in copy_database[name]:
                copy_database[name][filename].append(block)
            else:
                copy_database[name][filename] = [block]
        else:
            copy_database[name] = {filename: [block]} 
        print("Received list with data")
        print("Filename:", filename)

        return datanode_pb2.ReceiveDataResponse(success=True)

    def WriteBlock(self, request, context):
        f_name = request.name
        data = request.data
        
        if f_name not in self.block_storage:
            self.block_storage[f_name] = {'data': [data], 'filename': f_name, 'name': name, 'port': port}
        else:
            self.block_storage[f_name]['data'].append(data)
        return datanode_pb2.WriteBlockResponse(success=True)

    def ReadBlock(self, request, context):
        name = request.name
        if name in self.block_storage:
            return datanode_pb2.ReadBlockResponse(data=self.block_storage[name]['data'])
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Block not found")
            return datanode_pb2.ReadBlockResponse()
        
    def CheckStatus(self, request, context):
        return datanode_pb2.Response(status=True)
    
    def SendIndex(self, request, context):
        filename = request.filename
        call_signal_method()
        if len(o_datanodes) > 1:
            node_c: dict[str, Any] = random.choice(o_datanodes)
        elif len(o_datanodes) == 0:
            node_c = {'name': '0000', 'port': '0000'}
        else:
            node_c = o_datanodes[0]
        self.block_storage[filename]['copy'] = node_c['name']
        self.block_storage[filename]['port_copy'] = node_c['port']
        send_data_to_datanode(self.block_storage, filename)
        for key in self.block_storage.keys():
            save_data_namenode(self.block_storage[key])
            return datanode_pb2.Sended(sended=True)


def serve():
    global name
    global port

    name = generate_random_name()
    start_port = 50051
    end_port = 50060

    for try_port in range(start_port, end_port + 1):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        datanode_pb2_grpc.add_dataNodeServicer_to_server(dataNode(), server)
        try:
            server.add_insecure_port('[::]:{}'.format(try_port))
            server.start()
            print("dataNode name is ",  name)
            print("The server is running on port {}...".format(try_port))
            port = try_port
            break
        except Exception as e:
            print("Cannot initiliaze the server on port {}. trying port...".format(try_port))
            if try_port == end_port:
                print("The are not available ports.")
                return None

    send_data_to_rest_server(name, port)
    
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
