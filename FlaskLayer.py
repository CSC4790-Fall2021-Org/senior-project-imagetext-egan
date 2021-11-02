#Import all of the things necessary for the project
from flask import Flask, request, url_for, render_template, send_file
import spacy
import InputLayer
from ImageLayer import ImageLayer
import io
import base64

app = Flask(__name__)

nlp = InputLayer.initialize()
img = ImageLayer()

#This tells the program what to do when someone connects to the site's main page
@app.route('/', methods=['GET','POST'])
def index():
    currImage = base64.b64encode(img.returnImage().getvalue()).decode()
    if request.method == "POST":
        file = request.files['file'] if 'file' in request.files else None
        cmd = request.form['cmd']
        #Needs to update the file
        if file is not None:
            pass

        if cmd != "":
            InputLayer.main(nlp, img, cmd) #updates img as part of function
            currImage = base64.b64encode(img.returnImage().getvalue()).decode() #Returns image as BytesIO array -> converts to b64

    #This tells it where the relevant html file is
    return render_template('index.html', currImage=currImage)

def runServer():
    #app.run(host='0.0.0.0', port=5000)
    app.run()
