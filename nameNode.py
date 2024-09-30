import datanode_pb2
import datanode_pb2_grpc
import grpc
from flask import Flask, jsonify, request
from google.protobuf.empty_pb2 import Empty

app = Flask(__name__)

dataNodes = {}
database = {}
not_available = []


def send_request(name) -> list[str]:
    datanodes = []
    for key in dataNodes.keys():
        if key != name:
            info = dataNodes[key]
            ports = "localhost:" + str(info['port'])
            channel = grpc.insecure_channel(f"{ports}")
            client = datanode_pb2_grpc.dataNodeStub(channel)
            try:
                response = client.CheckStatus(Empty())
                if response.status:
                    datanodes.append(dataNodes[key])
                    print(f"This node is available {key}")
                else:
                    print(f"This node is available but there was an error {key}")
            except grpc.RpcError as e:
                not_available.append(key)
                print(f"This node isn't available {key}")
    for node in not_available:
        dataNodes.pop(node)
    return datanodes


def drop_datanode() -> None:
    global dataNodes, not_available
    for key in dataNodes.keys():
        info = dataNodes[key]
        ports = "localhost:" + str(info['port'])
        channel = grpc.insecure_channel(f"{ports}")
        client = datanode_pb2_grpc.dataNodeStub(channel)
        try:
            response = client.CheckStatus(Empty())
            if response.status:
                print(f"This node is available {key}")
            else:
                print(f"This node is available but there was an error {key}")
        except grpc.RpcError as e:
            not_available.append(key)
            print(f"This node isn't available {key} but there is a copy")
    for node in not_available:
        dataNodes.pop(node)


@app.route('/login', methods=['POST'])
def login():
    global dataNodes
    data = request.json
    datanode = data['name']
    port = data["port"]
    dataNodes[datanode] = {"name": datanode, "port": port}
    return jsonify({'message': 'DataNode Register successful', 'Name': datanode, 'Port': port}), 200


@app.route('/signal', methods=['GET'])
def signal():
    data = request.json
    name = data['name']
    if len(dataNodes) >= 1:
        nodes = send_request(name)
        if nodes == 1:
            return jsonify({'message': 'Only 1 available datanode'}), 200
        else: 
            return jsonify({'message': 'Available DataNodes successful', 'nodes': nodes}), 200
    else:
        return jsonify({'error': 'There are not datanode available'}), 404


@app.route('/save_data', methods=['POST'])
def save_data():
    global database
    data = request.json
    name = data['name']
    filename = data['filename']
    port = data['port']
    copy = data['copy']
    user = data['user']
    password = data['password']
    port_copy = data['port_copy']

    print("in namenode: ", filename)
    if filename not in database:
        database[filename] = [{'Filename': filename, 'Datanode Name': name, 'Port': port, 'Copy': copy, 'Port Copy': port_copy, 'user': user, 'password': password}]
    else:
        database[filename].append({'Filename': filename, 'Datanode Name': name, 'Port': port, 'Copy': copy, 'Port Copy': port_copy, 'user': user, 'password': password})
    return jsonify({'message': 'File Register successful', 'Name': filename, 'Port': port}), 200


@app.route('/search', methods=['GET'])
def search():
    try:
        return jsonify({'message': 'Search successful these are the available datanodes', 'dataNodes': dataNodes}), 200
    except Exception as e:
        return jsonify({'error': 'We cannot find any available datanode'}), 404


@app.route('/get_file', methods=['GET'])
def get_file():
    drop_datanode()
    filename = request.json['filename']
    user = request.json['user']
    password = request.json['password']
    if filename in database:
        if database[filename][0]['user'] != user or database[filename][0]['password'] != password:
            return jsonify({'message': 'invalid credentials'}), 403 
        info = database[filename]
        for node in info:
            node['leader_available'] = node['Datanode Name'] not in not_available
    else:
        return jsonify({'message': 'File not found', 'filename' : filename}), 200
    try:
        return jsonify({'message': 'This file is in this datanodes', 'Nodes': database[filename]}), 200
    except Exception as e:
        return jsonify({'error': 'We cannot find any available datanode'}), 404
    

@app.route('/index', methods=['GET'])
def index():
    if len(dataNodes) != 0:
        drop_datanode()
        return jsonify({'message': 'Indexing successful these are the available files', 'dataBase': database}), 200
    else:
        return jsonify({'error': 'We cannot find any file'}), 404
    

@app.route('/mkdir', methods=['POST'])
def mkdir():
    global database
    data = request.json
    directory = data['directory']
    name = data['name']
    
    # Comprobar si el directorio ya existe
    if directory not in database:
        database[directory] = {}
    
    if name not in database[directory]:
        database[directory][name] = {}  # Crear nuevo directorio vacío
        return jsonify({'message': f'Directorio {name} creado en {directory}'}), 200
    else:
        return jsonify({'error': 'Directorio ya existe'}), 400
    

@app.route('/rmdir', methods=['POST'])
def rmdir():
    global database
    data = request.json
    directory = data['directory']
    name = data['name']
    
    # Verificar si el directorio existe y está vacío
    if directory in database and name in database[directory] and not database[directory][name]:
        del database[directory][name]
        return jsonify({'message': f'Directorio {name} eliminado de {directory}'}), 200
    else:
        return jsonify({'error': 'Directorio no encontrado o no está vacío'}), 400
    
    
@app.route('/rm', methods=['POST'])
def rm():
    global database
    data = request.json
    directory = data['directory']
    file_name = data['name']
    
    # Verificar si el archivo existe
    if directory in database and file_name in database[directory]:
        del database[directory][file_name]
        return jsonify({'message': f'Archivo {file_name} eliminado de {directory}'}), 200
    else:
        return jsonify({'error': 'Archivo no encontrado'}), 400


if __name__ == '__main__':
    app.run(debug=True)