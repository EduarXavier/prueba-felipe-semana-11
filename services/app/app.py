from flask import Flask, jsonify, request
import os
import psycopg2
from pymongo import MongoClient
from bson import ObjectId

with open(os.getenv('MONGO_USER_FILE', 'r')) as file:
    MONGO_USER = file.read().strip()
with open(os.getenv('MONGO_PASSWORD_FILE', 'r')) as file:
    MONGO_PASSWORD = file.read().strip()
with open(os.getenv('MONGO_DB_NAME_FILE', 'r')) as file:
    MONGO_DB = file.read().strip()

with open(os.getenv('PG_USER_FILE', 'r')) as file:
    USER_POSTGRES = file.read().strip()
with open(os.getenv('PG_PASSWORD_FILE', 'r')) as file:
    PASSWORD_POSTGRES = file.read().strip()
with open(os.getenv('PG_DB_FILE', 'r')) as file:
    DB_POSTGRES = file.read().strip()
HOST_POSTGRES = os.getenv('PG_HOST')
PORT_POSTGRES = os.getenv('PG_PORT')


conn = psycopg2.connect(
    host=HOST_POSTGRES,
    port=int(PORT_POSTGRES),
    user=USER_POSTGRES,
    password=PASSWORD_POSTGRES,
    database=DB_POSTGRES

)
cursor = conn.cursor()

cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                cedula VARCHAR(50),
                nombre_usuario VARCHAR(100),
                correo_electronico VARCHAR(100)
            );
        """)
conn.commit()

mongo_client = MongoClient(
    host=os.getenv('MONGO_HOST', 'mongodb.docker'),
    port=int(os.getenv('MONGO_PORT', 27017)),
    username=MONGO_USER,
    password=MONGO_PASSWORD
)

mongo_db = mongo_client[MONGO_DB]

app = Flask(__name__)

@app.route('/mongo/create', methods=['POST'])
def create_user_mongo():
    data = request.json
    mongo_db['data'].insert_one(data)
    return jsonify({"message": "Dato insertado en MongoDB"})

@app.route('/mongo/list', methods=['GET'])
def list_user_mongo():
    data = [{**doc, "_id": str(doc["_id"])} for doc in mongo_db['data'].find()]
    return jsonify(data)

@app.route('/mongo/delete/<string:id>', methods=['DELETE'])
def delete_user_mongo(id):
    result = mongo_db['data'].delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Dato eliminado de MongoDB"})
    else:
        return jsonify({"message": "Dato no encontrado"}), 404

@app.route('/mongo/update/<id>', methods=['PUT'])
def update_user_mongo(id):
    data = request.json
    result = mongo_db['data'].update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.matched_count == 1:
        return jsonify({"message": "Dato actualizado en MongoDB"})
    else:
        return jsonify({"message": "Dato no encontrado"}), 404


@app.route('/postgres/create', methods=['POST'])
def create_user_postgres():
    data = request.json
    cursor.execute(
        "INSERT INTO users (cedula, nombre_usuario , correo_electronico) values (%s, %s, %s)", 
        (
        data.get('id', 'no disponible'),
        data.get('name', 'no disponible'),
        data.get('email', 'no disponible') 
        )
    )
    conn.commit()
    return jsonify({"message": "Datos insertado en postgres"})

@app.route('/postgres/list', methods=['GET'])
def list_user_postgres():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    result = []
    for user in users:
        result.append({
            "id": user[0],
            "cedula": user[1],
            "nombre_usuario": user[2],
            "correo_electronico": user[3]
        })
    return jsonify(result)

@app.route('/postgres/delete/<int:id>', methods=['DELETE'])
def delete_user_postgres(id):
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    if cursor.rowcount == 1:
        conn.commit()
        return jsonify({"message": "Dato eliminado de Postgres"})
    else:
        return jsonify({"message": "Dato no encontrado"}), 404

@app.route('/postgres/update/<int:id>', methods=['PUT'])
def update_user_postgres(id):
    data = request.json
    cursor.execute(
    "UPDATE users SET cedula = %s, nombre_usuario = %s, correo_electronico = %s WHERE id = %s",
    (
        data.get('cedula', 'no disponible'),
        data.get('nombre_usuario', 'no disponible'),
        data.get('correo_electronico', 'no disponible'),
        id
    )
    )
    if cursor.rowcount == 1:
        conn.commit()
        return jsonify({"message": "Dato actualizado en Postgres"})
    else:
        return jsonify({"message": "Dato no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)