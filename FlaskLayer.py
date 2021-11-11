#Import all of the things necessary for the project
from flask import Flask, request, url_for, render_template, send_file
from werkzeug.exceptions import HTTPException
from random import choice
from ImageLayer import ImageLayer
from multiprocessing import Process
import spacy
import InputLayer
import io
import base64
import string
import os

app = Flask(__name__)

nlp = InputLayer.initialize()
#img = ImageLayer()
users = {}

#Generate a random string of length 20
def randomString():
    return ''.join([choice(string.ascii_letters + string.digits) for i in range(20)])

#This tells the program what to do when someone connects to the site's main page
@app.route('/', methods=['GET','POST'])
def index():
    img = users.get(request.environ['REMOTE_ADDR'], None)
    #If ip is not logged, log it
    if img is None:
        img = ImageLayer()
        users[request.environ['REMOTE_ADDR']] = img
    error2 = None
    
    if request.method == "POST":
        imgFile = request.files.get('file', None)
        cmd = request.form.get('cmd', "")
        undo = request.form.get('undo', "")
        revert = request.form.get('revert', None)
        #Needs to update the file
        if imgFile is not None:
            if "." not in imgFile.filename:
                return render_template('index.html', currImg=None, error="Invalid File")
            ext = imgFile.filename.rsplit('.', 1)[1]
            newName = randomString() +"."+ ext
            imgFile.save(os.path.join("Pictures",  newName))
            img.setDefault(newName)

        if undo != "":
            cmd = "undo"

        if revert is not None:
            img.revertImage(int(revert))

        if cmd != "":
            error2 = InputLayer.main(nlp, img, cmd) #updates img as part of function

    #Update the image at least onece every time page is called
    currImage = base64.b64encode(img.returnImage().getvalue()).decode() #Returns image as BytesIO array -> converts to b64
    #This tells it where the relevant html file is
    return render_template('index.html', currImage=currImage, cmds=img.getCommands(), error2=error2)
'''
@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    img = users.get(request.environ['REMOTE_ADDR'], None)
    #If ip is not logged, log it
    if img is None:
        render_template('index.html', error2="Please relooad the webpage.")
    # This handles non-HTTP exceptions only
    return render_template('index.html', currImage=base64.b64encode(img.returnImage().getvalue()).decode(), cmds=img.getCommands(), error2="Cannot preform that transformation.")
'''
def runServer():
    #app.run(host='0.0.0.0', port=5000)
    app.run()
