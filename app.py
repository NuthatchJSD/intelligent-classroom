import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_socketio import SocketIO
from runner import *
from pdf_handler import clean_local

load_dotenv()

COMPONENTS_API_ADDRESS = os.environ.get('COMPONENTS_API_ADDRESS')
WORKING_PATH = os.environ.get('WORKING_PATH')
DATABASE_NAME = os.environ.get('DATABASE_NAME')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
socketio = SocketIO(app)

# Global variable to keep track of the current slide and music state
total_slides = 10  # Total number of slides
music_playing = False  # State of the music


@app.route('/')
def home():
    clean_local()
    classes = search_available_classes()
    return render_template('home.html', classes=classes)


@app.route('/presentation/<serial>', methods=['POST'])
def presentation(serial):
    global current_slide, total_slides
    current_slide = 1
    information = setup_class(serial)
    total_slides = information['total_slides']
    return render_template('presentation.html', serial=serial, slide=current_slide)


@socketio.on('change_slide')
def handle_change_slide(message):
    global current_slide
    if message['action'] == 'next':
        current_slide += 1
        if current_slide > total_slides:
            current_slide = 1
            socketio.emit('redirect_home')
        socketio.emit('update_slide', {'slide': current_slide})


if __name__ == '__main__':
    socketio.run(app, debug=True)
