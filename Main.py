"""

A program that takes english commands and edits photos
based off of them. Uses the spacy library for nlp and the
pillow library for image editing.

"""
print("Loading libraries... ")
import spacy
import re
from numerizer import numerize
from ImageLayer import ImageLayer
import Values

def main(nlp, newImg):
    #Example: "Crop the image and rotate it and grayscale it"
    userIn = input("Cmd: ");
    success = False

    if(userIn.lower().strip() == "quit"):
        print("Bye!")
        return False

    cmds = parseCommands(userIn, nlp)
    #Each command sep

    for cmd in cmds:
        #spacy.displacy.serve(cmd, style="dep")
        # Get the root word, should be verb
        rt, params = getParameters(cmd)
        adjs = gatherAdjectives(cmd.root)
        objs = getPossibleObjects(cmd.root)
        objs.append(cmd.root.text)

        if rt is None:
            #Command could not be found
            continue
        #Reset and undo are a bit different
        #Add methods here from ImageLayer that change as necessary
        #Build the method then call
        success = newImg.commandHandler(rt, adjs, objs, params)

    if success:
        newImg.showImage()
        #Set where image should be rolled back to
        newImg.setUndo()
    return True

def parseCommands(userIn, nlp):
    doc = nlp(userIn.lower())
    #Split it up by sentences, commas, and keyword "and"
    commands = [token.text for token in doc]
    separatedCmds = list()
    lastSplit = 0
    for i,v in enumerate(commands):
        if v.lower() in Values.breakWords:
            separatedCmds.append(commands[lastSplit : i])
            lastSplit = i
    separatedCmds.append(commands[lastSplit : ])

    #The commands have been separated out, now need to rebuild sentences
    sentences = list()
    for x in range(0, len(separatedCmds)):
        fullSentence = ""
        for word in separatedCmds[x]:
            if word not in Values.breakWords:
                fullSentence += word + " "
        sentences.append(fullSentence.strip())

    allCmds = list()
    #Process each command and return in a list
    #Split up by the keyword "and"
    for cmd in sentences:
        cmd = cmd.strip().lower()
        if not cmd.endswith("."):
            cmd = cmd + "."
        toks = nlp(cmd)
        #Split up by sentences
        for atomized in toks.sents:
            allCmds.append(atomized)

    return allCmds


# Since we deal with one command at a time, only one adj. should be passed
def gatherAdjectives(head):
    for node in head.children:
        #Look for advmod or npadvmod describing how to do this.
        if node.dep_ == "advmod" or node.dep_ == "npadvmod":
            return node.text

    return None

def getPossibleObjects(head):
    object = list()
    for node in head.children:
        #Find direct objet or appos modifier
        if node.dep_ in Values.types:
            object.append(node.text)

        object.extend(getPossibleObjects(node))

    return object

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

def updateEntityList():
    #Load in what we're looking for
    patterns = []
    for i, v in enumerate(Values.allEnts):
        for s in v:
            patterns.append({"label": Values.entLabels[i][0], "pattern": [{"LEMMA": s}], "id": Values.entLabels[i][1]})

    return patterns

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
