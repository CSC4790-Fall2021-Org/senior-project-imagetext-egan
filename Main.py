"""

Required Packages:
spacy
(en_core_web_sm) -> from spacy
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


    for cmd in cmds:
        # Get the root word, should be verb
        rt = next(cmd.sents).root
        head, do, pl = parseTreeNodes(rt)
        #Build the method then call
        theImg = ImageChange.getMethod(head.text.lower(), theImg)

    theImg.show()


def parseCommands(userIn):
    # Split up each command with "and" so that sentences don't get too long
    commands = userIn.split("and")
    nlp = spacy.load("en_core_web_sm")

    # Go through each split -> can use multiprocessing/numba here later
    allCmds = list()
    #Process each command and return in a list
    for cmd in commands:
        toks = nlp(cmd.strip())
        allCmds.append(toks)

    return allCmds


# Take the head node of the sentence, go through the tree
# Find prepositions that come from the ROOT, these will be the parameters -> exhaust prep search
def parseTreeNodes(head):
    # Build tuple (head, obj [can be implied], list_of_parameters( prep_node )
    dirObj = None
    parameterList = list()

    # Root node should be a verb, and should have a direct object (dobj)
    for node in head.children:
        # Find direct object, should only be one
        if node.dep_ == "dobj":
            dirObj = node
        if node.dep_ == "prep" or node.dep_ == "npadvmod":
            # Just pass the preposition: children will still be accessable
            parameterList.append(node)

    return head, dirObj, parameterList


if __name__ == "__main__":
    main()
