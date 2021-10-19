#Entities
downSections = {'bottom', 'lower'}

upSections = {'top', 'upper'}

sides = {'right', 'left'}

functs = {
    'grayscale', 'crop',
    'blur', 'rotate',
    'invert', 'emboss',
    'smooth', 'sharpen',
    'enhance', 'reset',
    'show','set','undo',
    'revert'
    }

#Store all entities in this tuple
allEnts = (downSections, upSections, sides, functs)

#Give entities a [label] and [id]
entLabels = (
    ('DOWN', 'DOWNSECT'),
    ('UP', 'UPSECT'),
    ('SIDE', 'SIDES'),
    ('FUNCT','FUNCTION')
    )

#Object types
types = {"dobj", "appos", "pobj","compound","nsubj"}

#Possible Objs (using pos, could use tag)
possObjs = {"NOUN","PRON","PROPN","NNS","DET","X","NUM"}

#OpenCV keywords
cvKeywords = {'me','my','face','our','faces','head','heads'}
kwParams = {'around', 'except', 'everything', 'all'}

#Adjective types
#Here are some of the modifiers we're looking for:
modify_more = {
    "lot", "greatly",
    "more", "significantly",
    "really", "substantially"
    }

modify_less = {
    "little", "slightly",
    "less", "bit",
    "lightly", "somewhat"
    }

#Unncessary words to be removed
breakWords = {'and',','}
