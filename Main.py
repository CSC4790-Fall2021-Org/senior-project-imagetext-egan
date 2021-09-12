"""

Required Packages:
spacy
(en_core_web_lg) -> from spacy
Pillow PIL

"""
import spacy
from PIL import Image
import ImageChange

def main():
    #Example: "Crop the image and rotate it and grayscale it"
    userIn = input("Cmd: ");

    cmds = parseCommands(userIn)
    theImg = Image.open("Koala.jpg")

    #Each command sep
    for cmd in cmds:
        # Get the root word, should be verb
        rt = cmd.root
        head, do = parseTreeNodes(rt)
        #params = getParameters(cmd.sents)
        #Build the method then call
        theImg = ImageChange.getMethod(head.text.lower(), theImg)

    theImg.show()


def parseCommands(userIn):
    # Split up each command with "and" so that sentences don't get too long
    commands = userIn.split("and")
    #Load in spacy pipeline
    nlp = spacy.load("en_core_web_lg")
    #Add in new pipe with my stuff
    entity_ruler = nlp.add_pipe("entity_ruler")
    entity_ruler.initialize(lambda: [], nlp=nlp, patterns=updateEntityList())

    # Go through each split -> can use multiprocessing/numba here later
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
# Find prepositions that come from the ROOT, these will be the parameters -> exhaust prep search
def parseTreeNodes(head):
    # Build tuple (head, obj [can be implied], list_of_parameters( prep_node )
    dirObj = None

    # Root node should be a verb, and should have a direct object (dobj)
    for node in head.children:
        # Find direct object, should only be one
        if node.dep_ == "dobj":
            dirObj = node

    return head, dirObj

def updateEntityList():
    #Load in what we're looking for
    sections = ['bottom', 'lower', 'top', 'upper']
    sides = ['right', 'left', 'center', 'middle']
    patterns = []
    for sect in sections:
        patterns.append({"label": "SECTION", "pattern": [{"LOWER": sect}], "id": "SECT"})
    for side in sides:
        patterns.append({"label": "SIDES", "pattern": [{"LOWER": side}], "id": "SIDE"})
    return patterns

#Should be recieving one sentence
def getParameters(doc):
    params = {}
    for sen in doc:
        nums = []
        for ent in sen.ents:
            if ent.label_ == "CARDINAL" or ent.label_ == "QUANTITY":
                [nums.append(int(s)) for s in re.findall(r'\d+', numerize(ent.text))]
            else:
                params[ent.label_] = ent.text

        if(len(nums) > 0):
            params['NUMBERS'] = nums






if __name__ == "__main__":
    main()
