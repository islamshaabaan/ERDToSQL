import imutils
import numpy as np
import cv2
import math
Entities = []
Relations = []
Attributes = []
Lines = []

class point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

class entity:
    def __init__(self, i, n, CenterPoint):
        self.id =i #unique number for each entity
        self.name =n #name image processing part give to each entity a name like "entity-1" then Gui Module ask user to change name to whatever he/she likes
        self.CenterPoint = CenterPoint

        self.attr_list = [] #a list that contain all the entity atttribute each member of the list is instance of class attribute
    def add_attr(self,attr):
        self.attr_list.append(attr)


class attribute:
    def __init__(self, name, attrtype, CenPoint):
        self.name = name # name of attribute image processing part give to each attribute  a name like "attribute-1-1" then Gui Module ask user to change name to whatever he/she likes
        self.attrtype = attrtype # type would be a primary key or non prime
        self.CenPoint = CenPoint


class relation:
    def __init__(self, name, id1, id2, p_ratio1, p_ratio2, p_type1, p_type2, CenP):
        self.name = name
        self.id1 = id1 #id of the first entity in the relation
        self.id2 = id2 #id of the second entity in the relation
        self.p_type1 = p_type1 #type  of participation of the first entity could be partial or full
        self.p_type2 = p_type2 #type of participation of the second entity could be partial or full
        self.p_ratio1 = p_ratio1 #ratio of participation of first entity could be one or many
        self.p_ratio2 = p_ratio2 #ratio of participation of second  entity could be one or many
        self.CenPoint = CenP


class lineobj:
    def __init__(self, name, L_type, StartPoint, EndPoint):
        self.name = name
        self.L_type = L_type
        self.StartPoint = StartPoint
        self.EndPoint = EndPoint


def fillHole(im_in):
    im_floodfill = im_in.copy()

    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h1, w1 = im_in.shape[:2]
    mask = np.zeros((h1 + 2, w1 + 2), np.uint8)

    # Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, mask, (0, 0), 255);

    # Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    # Combine the two images to get the foreground.
    im_out = im_in | im_floodfill_inv

    return im_out


def drawShapes(img):
    imgGrey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    Denoise = cv2.medianBlur(imgGrey, 3)
    cv2.imshow("imgGrey", Denoise)

    _, thrash = cv2.threshold(imgGrey, 185, 255, cv2.THRESH_BINARY)
    cv2.imshow("Thresh", thrash)
    binaryconverted = (255 - thrash)
    cv2.imshow("binaryconverted", binaryconverted)
    binaryconverted1 = fillHole(binaryconverted)
    cv2.imshow("binaryconverted1", binaryconverted1)
    #edges = cv2.Canny(binaryconverted, 100, 200)
    #cv2.imshow('edges images', edges)

    opening = cv2.morphologyEx(binaryconverted1, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
    opening1 = cv2.medianBlur(opening, 1)
    cv2.imshow("opening1", opening1)

    opening2 = cv2.dilate(opening, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    #cv2.imshow("opening2", opening2)

    closing = cv2.morphologyEx(binaryconverted1, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)))
    cv2.imshow("closing", closing)
    onlyline1 = binaryconverted1 - opening1
    cv2.imshow("onlyline1", onlyline1)
    onlyline2 = binaryconverted1 - opening2
    #onlyline2 = cv2.dilate(onlyline2, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    cv2.imshow("onlyline2", onlyline2)

    edges = cv2.Canny(onlyline2, 150, 400, None, 3)
    cv2.imshow("edges", edges)
    #nested = binaryconverted - (255-opening)
    #cv2.imshow("nested", nested)

    lines = cv2.HoughLinesP(onlyline1, 1, np.pi / 180, 38, None, minLineLength=1, maxLineGap=10)
    numberoflines = 0
    print(len(lines))
    for line in lines:
        numberoflines = numberoflines + 1
        xL, yL, x2, y2 = line[0]
        cv2.line(img, (xL, yL), (x2, y2), (255, 0, 255), 2)
        StartP = point(xL, yL)
        EndP = point(x2, y2)
        li = lineobj("Line" + str(numberoflines), "undefined", StartP, EndP)
        Lines.append(li)
        cv2.putText(img, "line", (int(xL), int(yL)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))

    cv2.imshow("DrawOnlyLine", img)

    contours, _ = cv2.findContours(opening1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    shape = []

    numberofent = 0
    numberofrel = 0
    numberofatt = 0
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)

        x = approx.ravel()[0]
        y = approx.ravel()[1] - 5

        if len(approx) == 4:
            x1, y1, w, h = cv2.boundingRect(approx)
            aspectRatio = float(w) / h
            apratio = cv2.contourArea(contour) / (w * h)
            # print(aspectRatio)
            if 0.95 <= aspectRatio <= 1.05 or apratio < 0.73:
                print("Squares", len(approx))
                print("aspectRatio", aspectRatio)
                cv2.putText(img, "square", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
                shape.append("Relation")
                cv2.drawContours(img, [approx], 0, (0, 0, 255), 2)
                M = cv2.moments(contour)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                CeP = point(cX, cY)
                numberofrel = numberofrel + 1
                rel = relation("Rel" + str(numberofrel), -1, -1, "undefined", "undefined", "undefined", "undefined", CeP)
                Relations.append(rel)

                # draw the contour and center of the shape on the image
                # cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                cv2.circle(img, (cX, cY), 5, (0, 255, 255), -1)
            elif cv2.contourArea(contour) > 1000:
                print("Rectangle", len(approx))
                print("aspectRatio", aspectRatio)
                cv2.putText(img, "rectangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
                M = cv2.moments(contour)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                CentP = point(cX, cY)
                # draw the contour and center of the shape on the image
                #cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                cv2.circle(img, (cX, cY), 5, (0, 255, 255), -1)
                shape.append("Entity")
                cv2.drawContours(img, [approx], 0, (0, 255, 0), 2)
                numberofent = numberofent + 1
                ent = entity(numberofent-1, "Ent"+str(numberofent-1), CentP)
                Entities.append(ent)

        elif 4 <= len(approx) < 8 and cv2.contourArea(contour) > 100:
            print("Squares", len(approx))
            #print("aspectRatio", aspectRatio)
            M = cv2.moments(contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            CeP1 = point(cX, cY)
            # draw the contour and center of the shape on the image
            # cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
            cv2.circle(img, (cX, cY), 5, (0, 255, 255), -1)
            cv2.drawContours(img, [approx], 0, (0, 0, 0), 2)
            cv2.putText(img, "square", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
            shape.append("Relation")
            numberofrel = numberofrel + 1
            rel = relation("Rel" + str(numberofrel), -1, -1, "undefined", "undefined", "undefined", "undefined", CeP1)
            Relations.append(rel)
        elif len(approx) > 4:
            print("Cirlcles", len(approx))
            cv2.putText(img, "Circle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
            shape.append("Attribute")
            cv2.drawContours(img, [approx], 0, (255, 0, 0), 2)
            M = cv2.moments(contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            CirCentP = point(cX, cY)
            # draw the contour and center of the shape on the image
            # cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
            cv2.circle(img, (cX, cY), 5, (0, 255, 255), -1)
            numberofatt = numberofatt + 1
            att = attribute("Att" + str(numberofatt), "undefined", CirCentP)
            Attributes.append(att)

    cv2.imshow("shapes", img)
    return img


def CalcDistance(Point1, Point2):
    return math.sqrt(math.pow(Point1.x - Point2.x, 2) + math.pow(Point1.y - Point2.y, 2))


def ConnectedSh(line, Ents, Attrs, Rels):
    startPointofLine = line.StartPoint
    endPointofLine = line.EndPoint
    connectedtostart = Ents[0].name
    connectedtoend = Ents[0].name


    MinDisSt = CalcDistance(startPointofLine, Ents[0].CenterPoint)
    for i in range(1, len(Ents)):
        MinDisTemp = CalcDistance(startPointofLine, Ents[i].CenterPoint)
        if MinDisTemp < MinDisSt:
            MinDisSt = MinDisTemp
            connectedtostart = Ents[i].name

    for i1 in range(0, len(Attrs)):
        MinDisTemp = CalcDistance(startPointofLine, Attrs[i1].CenPoint)
        if MinDisTemp < MinDisSt:
            MinDisSt = MinDisTemp
            connectedtostart = Attrs[i1].name
    for i2 in range(0, len(Rels)):
        MinDisTemp = CalcDistance(startPointofLine, Rels[i2].CenPoint)
        if MinDisTemp < MinDisSt:
            MinDisSt = MinDisTemp
            connectedtostart = Rels[i2].name

    MinDisEnd = CalcDistance(endPointofLine, Ents[0].CenterPoint)
    for i3 in range(0, len(Ents)):
        MinDisTemp = CalcDistance(endPointofLine, Ents[i3].CenterPoint)
        if MinDisTemp < MinDisEnd:
            MinDisEnd = MinDisTemp
            connectedtoend = Ents[i3].name

    for i4 in range(0, len(Attrs)):
        MinDisTemp = CalcDistance(endPointofLine, Attrs[i4].CenPoint)
        if MinDisTemp < MinDisEnd:
            MinDisEnd = MinDisTemp
            connectedtoend = Attrs[i4].name
    for i5 in range(0, len(Rels)):
        MinDisTemp = CalcDistance(endPointofLine, Rels[i5].CenPoint)
        if MinDisTemp < MinDisEnd:
            MinDisEnd = MinDisTemp
            connectedtoend = Rels[i5].name

    connectedshape = [connectedtostart, connectedtoend]
    return connectedshape


def Merge(lines, Ents, Attrs, Rels):
    connectedshapes = []
    for i in range(0, len(lines)):
        connectedshapes.append(ConnectedSh(lines[i], Ents, Attrs, Rels))

    for i in range(0, len(connectedshapes)):
        if "Ent" in connectedshapes[i][0] and "Rel" in connectedshapes[i][1]:
            stri1 = connectedshapes[i][0]
            stri2 = connectedshapes[i][1]
            if Relations[int(stri2[len(stri2)-1:]) - 1].id1 == -1:
                Relations[int(stri2[len(stri2)-1:]) - 1].id1 = int(stri1[len(stri1)-1:])
            elif Relations[int(stri2[len(stri2) - 1:]) - 1].id2 == -1:
                if Relations[int(stri2[len(stri2)-1:]) - 1].id1 < int(stri1[len(stri1) - 1:]):
                    Relations[int(stri2[len(stri2) - 1:]) - 1].id2 = int(stri1[len(stri1) - 1:])
                else:
                    Relations[int(stri2[len(stri2) - 1:]) - 1].id2 = Relations[int(stri2[len(stri2)-1:]) - 1].id1
                    Relations[int(stri2[len(stri2) - 1:]) - 1].id1 = int(stri1[len(stri1) - 1:])

        elif "Rel" in connectedshapes[i][0] and "Ent" in connectedshapes[i][1]:
            stri1 = connectedshapes[i][1]
            stri2 = connectedshapes[i][0]
            index = stri2[len(stri2)-1:]
            if Relations[int(index) - 1].id1 == -1:
                Relations[int(stri2[len(stri2)-1:]) - 1].id1 = int(stri1[len(stri1)-1:])
            elif Relations[int(stri2[len(stri2) - 1:]) - 1].id2 == -1:
                if Relations[int(stri2[len(stri2) - 1:]) - 1].id1 < int(stri1[len(stri1) - 1:]):
                    Relations[int(stri2[len(stri2) - 1:]) - 1].id2 = int(stri1[len(stri1) - 1:])
                else:
                    Relations[int(stri2[len(stri2) - 1:]) - 1].id2 = Relations[int(stri2[len(stri2) - 1:]) - 1].id1
                    Relations[int(stri2[len(stri2) - 1:]) - 1].id1 = int(stri1[len(stri1) - 1:])

        elif "Ent" in connectedshapes[i][0] and "Att" in connectedshapes[i][1]:
            stri1 = connectedshapes[i][0]
            stri2 = connectedshapes[i][1]
            Entities[int(stri1[len(stri1)-1:])].add_attr(Attributes[int(stri2[len(stri2)-1:]) - 1])

        elif "Att" in connectedshapes[i][0] and "Ent" in connectedshapes[i][1]:
            stri2 = connectedshapes[i][0]
            stri1 = connectedshapes[i][1]
            Entities[int(stri1[len(stri1)-1:])].add_attr(Attributes[int(stri2[len(stri2)-1:]) - 1])


    return connectedshapes




img = cv2.imread('\ASU\Senior\Flowchart5.png')
cv2.imshow("img", img)
Test = drawShapes(img)
Test2 = Merge(Lines, Entities, Attributes, Relations)




print("Smile")
# contours1, _ = cv2.findContours(onlyline, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
# for contour1 in contours1:
# approx1 = cv2.approxPolyDP(contour1, 0.001 * cv2.arcLength(contour1, True), False)
# cv2.drawContours(img, [approx1], 0, (0, 0, 255), 2)
# x1 = approx1.ravel()[0]
# y1 = approx1.ravel()[1]
# print(len(approx1))
# cv2.putText(img, "line", (int(x1), int(y1)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))


# Exiting the window if 'q' is pressed on the keyboard.
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()
