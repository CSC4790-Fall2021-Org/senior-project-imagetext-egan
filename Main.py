"""

A program that takes english commands and edits photos
based off of them. Uses the spacy library for nlp and the
pillow library for image editing.

"""
print("Loading libraries... ")
import spacy
from ImageLayer import ImageLayer
from numerizer import numerize
import re

def main(nlp, newImg):
    #Example: "Crop the image and rotate it and grayscale it"
    userIn = input("Cmd: ");

    if(userIn.lower().strip() == "quit"):
        print("Bye!")
        return False
    '''
    if(userIn.lower().replace(" ","").strip().startswith("setdefault")):
        newImg.setDefault(userIn.lower().strip().split("default")[-1])
        return True
    '''
    if(userIn.lower().strip().startswith("rollback")):
        newImg.rollbackImage()
        newImg.showImage()
        return True


    cmds = parseCommands(userIn, nlp)
    #Each command sep
    newImg.setRollback()
    for cmd in cmds:
        #spacy.displacy.serve(cmd, style="dep")
        # Get the root word, should be verb
        rt, params = getParameters(cmd)
        deps = parseTreeNodes(cmd.root)
        if rt is None:
            #If command couldn't be found let the user know
            print("Cannot recognize command: %s" % cmd.root.text.lower())
            return True
        #Reset and rollback are a bit different
        #Add methods here from ImageLayer that change as necessary
        #Build the method then call
        success = newImg.commandHandler(rt, deps, params)

    if success:
        newImg.showImage()
    #Set where image should be rolled back to

    return True

def parseCommands(userIn, nlp):
    # Split up each command with "and" so that sentences don't get too long
    commands = userIn.split(" and ")
    allCmds = list()
    #Process each command and return in a list
    #Split up by the keyword "and"
    for cmd in commands:
        cmd = cmd.strip()
        if not cmd.endswith("."):
            cmd = cmd + "."
        toks = nlp(cmd)
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
    dependencies["dobj"] = []
    for node in head.children:
        # Find direct object, should only be one
        if node.dep_ == "dobj" or node.dep_ == "appos":
            dependencies["dobj"].append(node.text)
        #Look for advmod or npadvmod describing how to do this.
        if node.dep_ == "advmod" or node.dep_ == "npadvmod":
            dependencies["modifier"] = node.text

    #If an object can't be found, try the root of the sentence
    #Change this so multiple objects are identified.
    dependencies["dobj"].append(head.text)

    return dependencies

def updateEntityList():
    #Load in what we're looking for
    downSections = ('bottom', 'lower')
    upSections = ('top', 'upper')
    sides = ('right', 'left')
    #Find functions #Add show, reset, rollback
    functs = ('grayscale', 'crop', 'blur', 'rotate', 'invert', 'emboss', 'smooth', 'sharpen', 'enhance', 'reset','show','set')
    patterns = []
    for sect in downSections:
        patterns.append({"label": "DOWN", "pattern": [{"LOWER": sect}], "id": "DOWNSECT"})
    for sect in upSections:
        patterns.append({"label": "UP", "pattern": [{"LOWER": sect}], "id": "UPSECT"})
    for side in sides:
        patterns.append({"label": "SIDE", "pattern": [{"LOWER": side}], "id": "SIDES"})
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
    images = ImageLayer()
    print("Done!")
    while(main(nlp, images)):
        pass
