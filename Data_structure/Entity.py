#output of the imag-processing phase and gui phsase would be a list of class entity and a list of class relation 
import uuid

class point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class entity:
    def __init__(self, n, CenPoint):
        self.id = getUniqueID()  # unique number for each entity
        self.name = n  # name image processing part give to each entity a name like "entity-1" then Gui Module ask
        # user to change name to whatever he/she likes
        self.attr_list = []  # a list that contain all the entity atttribute each member of the list is instance of
        # class attribute
        self.relations = []  # list of entity relations [relation may be seen twice once in every entity]
        self.CenPoint = CenPoint

    def add_attr(self, attr):
        self.attr_list.append(attr)

    def add_relation(self, relation):
        self.relations.append(relation)

    def getID(self):
        return self.id

    def getPrim_attrib(self):
        for attrib in self.attr_list:
            if attrib.type == "primary" or attrib.type == "prime":
                return attrib


class attribute:
    def __init__(self, name, attr_type, CenPoint, comp=False, Parent=False):
        self.name = name  # name of attribute image processing part give to each attribute  a name like "attribute-1-1" then Gui Module ask user to change name to whatever he/she likes
        self.type = attr_type  # type would be a primary key or non prime
        self.isComposite = comp
        self.isParent = Parent
        self.attrib_childs = []
        self.CenPoint = CenPoint

    def add_child(self, attrib):
        self.attrib_childs.append(attrib)


class relation:
    def __init__(self, name, id1, id2, p_ratio1, p_ratio2, p_type1, p_type2, CenPoint):
        self.name = name
        self.id1 = id1
        self.id2 = id2
        self.id = id1 ^ id2  # unique id of the relation
        self.p_type1 = p_type1  # type  of participation of the first entity could be partial or full
        self.p_type2 = p_type2  # type of participation of the second entity could be partial or full
        self.p_ratio1 = p_ratio1  # ratio of participation of first entity could be one or many
        self.p_ratio2 = p_ratio2  # ratio of participation of second  entity could be one or many
        self.attrib_list = []
        self.CenPoint = CenPoint

    def getTargetEntity(self, srcEntity):
        return self.id ^ srcEntity.getID()

    def add_attrib(self, attrib):
        self.attrib_list.append(attrib)


class lineobj:
    def __init__(self, name, L_type, StartPoint, EndPoint):
        self.name = name
        self.L_type = L_type
        self.StartPoint = StartPoint
        self.EndPoint = EndPoint

def getUniqueID():
    return uuid.uuid1().int
