from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, join_room, leave_room, send
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'websocketdemo'
mysql = MySQL(app)
socketio = SocketIO(app)


@app.route('/user1')
def user1():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM message')
    messages = cursor.fetchall()  # Fetch all rows
    cursor.close()
    return render_template('user1.html', messages=messages)

@app.route('/user2')
def user2():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM message')
    messages = cursor.fetchall()  # Fetch all rows
    cursor.close()
    return render_template('user2.html', messages=messages)


@socketio.on('join')
def on_join(data):
    print("on_join(data) ==>> ",data)
    username = data['username']
    chat_id = data['chat_id']
    room = f"chat_{chat_id}"
    join_room(room)
    send(f"{username} has joined the chat.", room=room)


@socketio.on('message')
def handle_message(data):
    chat_id = data['chat_id']
    sender_id = data['sender_id']
    receiver_id = data['receiver_id']
    content = data['content']
    timestamp = datetime.now()

    # Save the message to the database
    cursor = mysql.connection.cursor()
    cursor.execute(
        'INSERT INTO message (chat_id, sender_id, receiver_id, content, timestamp) VALUES (%s, %s, %s, %s, %s)',
        (chat_id, sender_id, receiver_id, content, timestamp)
    )
    mysql.connection.commit()
    cursor.close()

    # Emit the message to the chat room
    room = f"chat_{chat_id}"
    send({'sender_id': sender_id, 'content': content, 'timestamp': str(timestamp)}, room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    chat_id = data['chat_id']
    room = f"chat_{chat_id}"
    leave_room(room)
    send(f"{username} has left the chat.", room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)