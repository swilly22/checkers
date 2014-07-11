import json

# Represents a single move in the game, encapsulate all information related to
# a single move.

class Play(object):
    def __init__(self, source, dest, bEat = False, eatPosition = None, eatColor = None, eatType = None, bQueened = False):
        self.source = source  # move originate position.
        self.dest = dest      # move destination
        self.bEat = bEat  # was a piece was eaten in this move?
        self.eatPosition = eatPosition    # where was the piece which got eaten
        self.eatColor = eatColor  # what was the color of the eaten piece
        self.eatType = eatType    # what was the type of the eaten piece? Checker / Queen?
        self.bQueened = bQueened # Did this move changed a checker to a queen?

    @property
    def From(self):
        return self.source

    @property
    def To(self):
        return self.dest

    @property
    def Eat(self):
        return self.bEat

    @property
    def EatPosition(self):
        return self.eatPosition

    @property
    def EatColor(self):
        return self.eatColor

    @property
    def EatType(self):
        return self.eatType

    @property
    def BQueened(self):
        return self.bQueened
    
    def ToJson(self):
        dic = {'from' : self.source, 'to' : self.dest, 'bEat' : self.bEat, 'eatPosition' : self.eatPosition, 'eatColor' : self.eatColor, 'eatType' : self.eatType}
        return json.dumps(dic)