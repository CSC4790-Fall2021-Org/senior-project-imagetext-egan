"""

Required Packages:
spacy
(en_core_web_lg) -> from spacy
Pillow PIL
numerizer
re (regex)
ImageChange -> uses os and math

"""
print("Loading libraries... ")
import spacy
from PIL import Image
import ImageChange
from numerizer import numerize
import re

def main(nlp):
    #Example: "Crop the image and rotate it and grayscale it"
    userIn = input("Cmd: ");
    if(userIn == "quit"):
        print("Bye!")
        return False

    cmds = parseCommands(userIn, nlp)
    theImg = Image.open("Koala.jpg")

    #Each command sep
    for cmd in cmds:
        # Get the root word, should be verb
        rt, params = getParameters(cmd)
        deps = parseTreeNodes(cmd.root)
        if rt is None:
            #If command couldn't be found let the user know
            print("Cannot recognize command: %s" % cmd.root.text.lower())
            return True
        #Build the method then call
        theImg = ImageChange.getMethod(rt, deps, params, theImg)

    theImg.show()
    return True

def parseCommands(userIn, nlp):
    # Split up each command with "and" so that sentences don't get too long
    commands = userIn.split("and")
    allCmds = list()
    #Process each command and return in a list
    #Split up by the keyword "and"
    for cmd in commands:
        toks = nlp(cmd.strip())
        #Split up by sentences
        for atomized in toks.sents:
            allCmds.append(atomized)

    return allCmds


# Take the head node of the sentence, go through the tree
def parseTreeNodes(head):
    # Get direct object if it exists
    dirObj = None
    dependencies = {}
    # Root node should be a verb, and should have a direct object (dobj)
    for node in head.children:
        # Find direct object, should only be one
        if node.dep_ == "dobj" or node.dep_ == "appos":
            dependencies["dobj"] = node.text
        #Look for advmod or npadvmod describing how to do this.
        if node.dep_ == "advmod" or node.dep_ == "npadvmod":
            dependencies["modifier"] = node.text


    return dependencies

def updateEntityList():
    #Load in what we're looking for
    sections = ('bottom', 'lower', 'top', 'upper')
    sides = ('right', 'left', 'center', 'middle')
    functs = ('grayscale', 'crop', 'blur', 'rotate', 'invert', 'emboss', 'smooth', 'sharpen')
    patterns = []
    for sect in sections:
        patterns.append({"label": "SECTION", "pattern": [{"LOWER": sect}], "id": "SECT"})
    for side in sides:
        patterns.append({"label": "SIDES", "pattern": [{"LOWER": side}], "id": "SIDE"})
    for func in functs:
        patterns.append({"label": "FUNCT", "pattern": [{"LOWER": func}], "id": "FUNCTION"})
    return patterns

#Should be recieving one sentence
#Returns a dict with [keyword : parameter]
def getParameters(doc):
    params = {}
    nums = []
    funcToCall = None
    for ent in doc.ents:
        if ent.label_ == "CARDINAL" or ent.label_ == "QUANTITY":
            for s in re.findall(r'\d+', numerize(ent.text)):
                nums.append(int(s))
        #ASSUME THERE IS A NUMBER HERE
        elif ent.label_ == "PERCENT":
            params[ent.label_] = re.findall(r'\d+', numerize(ent.text))[0]
        elif ent.label_ == "FUNCT":
            funcToCall = ent.text.lower()
        else:
            params[ent.label_] = ent.text

    if(len(nums) > 0):
        params['NUMBERS'] = nums

    return funcToCall, params

if __name__ == "__main__":
    #Load in spacy nlp -> takes about 1.5-2 seconds:
    nlp = spacy.load("en_core_web_lg")
    #Update entity list for nlp
    entity_ruler = nlp.add_pipe("entity_ruler")
    entity_ruler.initialize(lambda: [], nlp=nlp, patterns=updateEntityList())
    print("Done!")
    while(main(nlp)):
        continue
