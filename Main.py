#Import all of the things necessary for the project
from flask import Flask, request, url_for, render_template
import InputLayer

app = Flask(__name__)
il = InputLayer

#This tells the program what to do when someone connects to the site's main page
@app.route('/')
def index():
    #This tells it where the relevant html file is
    return '''<h1> Hello World </h1>'''

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000)
    il.initialize()
    print("Finished")
    app.run()
