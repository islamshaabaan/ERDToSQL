import numpy as np
import cv2
import math
from Data_structure import Entity as Shapes


# Function to Fill hole by White Mask
def fillHole(im_in):
    im_floodfill = im_in.copy()

    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h1, w1 = im_in.shape[:2]
    mask = np.zeros((h1 + 2, w1 + 2), np.uint8)

    # Floodfill from point (0, 0)
    cv2.floodFill(im_floodfill, mask, (0, 0), 255)

    # Invert floodfilled image
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    # Combine the two images to get the foreground.
    im_out = im_in | im_floodfill_inv

    return im_out


# Detect Lines by Hough Transform
def GetLinesByTransform(onlylineIMG, Origimg, Lines):
    lines = cv2.HoughLinesP(onlylineIMG, 1, np.pi / 180, 38, None, minLineLength=0, maxLineGap=10)
    print(len(lines))

    numberoflines = 0
    for line in lines:
        numberoflines = numberoflines + 1
        xL, yL, x2, y2 = line[0]

        StartP = Shapes.point(xL, yL)  # Start Point of Line
        EndP = Shapes.point(x2, y2)  # End Point of Line
        # Make a line Object and store it into Line List
        li = Shapes.lineobj("Line" + str(numberoflines), "undefined", StartP, EndP)
        Lines.append(li)
        # Draw the Line
        cv2.line(Origimg, (xL, yL), (x2, y2), (255, 0, 255), 2)
        cv2.putText(Origimg, "line", (int(xL), int(yL)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))

    return Origimg, Lines


# Detect Lines by Contours
def GetLinesByContours(onlyline1, Oimg, Lines):
    # Making these 2 Operations to remove noise
    onlyline1 = cv2.medianBlur(onlyline1, 3)
    onlyline1 = cv2.morphologyEx(onlyline1, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)))

    contours1, _ = cv2.findContours(onlyline1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # cv2.imshow("erode", onlyline1)
    linesNumber = 0
    for contour1 in contours1:
        approx1 = cv2.approxPolyDP(contour1, 0.01 * cv2.arcLength(contour1, True), False)
        x1 = approx1.ravel()[0]
        y1 = approx1.ravel()[1]
        startPoint = Shapes.point(x1, y1)
        # Moments operation to get the Center Point
        M = cv2.moments(contour1)
        # If the Line is just point
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            # CeP = Shapes.point(cX, cY)
        else:
            cX = x1
            cY = y1
            # CeP = Shapes.point(cX, cY)

        # Add the difference distance to the center point to get End Point
        x2 = cX + (cX - x1)
        y2 = cY + (cY - y1)
        endPoint = Shapes.point(x2, y2)

        if x1 != x2 or y1 != y2:  # To make sure that the line is not just a point
            linesNumber = linesNumber + 1
            # print("start", x1, y1)
            # print("C", cX, cY)
            # print("end", x2, y2)

            # Make a line Object and store it into Line List
            li = Shapes.lineobj("Line" + str(linesNumber), "undefined", startPoint, endPoint)
            Lines.append(li)

            # Draw the Line
            cv2.drawContours(Oimg, [approx1], 0, (0, 0, 255), 2)
            cv2.putText(Oimg, "startL", (int(x1), int(y1)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
            cv2.putText(Oimg, "C", (int(cX), int(cY)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
            cv2.putText(Oimg, "endL", (int(x2), int(y2)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255))

    # print("linesN", linesNumber)
    return Oimg, Lines


# Detect Shapes by Contours = Entity or Relation or Attribute
def GetShapes(openingIMG, Orimg, Entities, Relations, Attributes):
    contours, _ = cv2.findContours(openingIMG, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

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

            # To make sure that the shape is Square = Relation
            if 0.95 <= aspectRatio <= 1.05 or apratio < 0.73:
                numberofrel = numberofrel + 1
                # print("Squares", len(approx))
                # print("aspectRatio", aspectRatio)

                # Get Center point
                M = cv2.moments(contour)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                CeP = Shapes.point(cX, cY)

                # Initialize an Relation Object and store it into Relations List with default values
                rel = Shapes.relation("Rel" + str(numberofrel), -1, -1, "1", "1", "full",
                                      "full", CeP)
                Relations.append(rel)

                # Draw the Relation Shape
                cv2.putText(Orimg, "Rel" + str(numberofrel), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
                cv2.drawContours(Orimg, [approx], 0, (0, 0, 255), 2)

                # draw the contour and center of the shape on the image
                # cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                cv2.circle(Orimg, (cX, cY), 5, (0, 255, 255), -1)

            # So now it's not Relation, it is an entity = rectangle
            elif cv2.contourArea(contour) > 1000:
                numberofent = numberofent + 1
                # print("Rectangle", len(approx))
                # Get Center Point of Entity
                M = cv2.moments(contour)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                CentP = Shapes.point(cX, cY)
                # Make an entity object to store it into  Entities List
                ent = Shapes.entity("Ent" + str(numberofent - 1), CentP)
                Entities.append(ent)

                # draw the contour and center of the shape on the image
                # cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                cv2.putText(Orimg, "Ent" + str(numberofent - 1), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
                cv2.circle(Orimg, (cX, cY), 5, (0, 255, 255), -1)
                cv2.drawContours(Orimg, [approx], 0, (0, 255, 0), 2)

        # if the shape is not pure or still there are noises because of the Morphology Operations
        # The result is distorted square with more than 4 Approx.
        elif 4 <= len(approx) < 7 and cv2.contourArea(contour) > 100:
            # print("Squares", len(approx))
            numberofrel = numberofrel + 1

            # Get the Center Point
            M = cv2.moments(contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            CeP1 = Shapes.point(cX, cY)
            # Initialize a Relation object to store it into Relations List with default values
            rel = Shapes.relation("Rel" + str(numberofrel), -1, -1, "1", "1", "full", "full",
                                  CeP1)
            Relations.append(rel)

            # draw the contour and center of the shape on the image
            # cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
            cv2.circle(Orimg, (cX, cY), 5, (0, 255, 255), -1)
            cv2.drawContours(Orimg, [approx], 0, (0, 0, 0), 2)
            cv2.putText(Orimg, "Rel" + str(numberofrel) + str(numberofrel), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))

        # If the approx is more than 6 or 7, it will be a circle or ellipse = attribute
        elif len(approx) > 6:
            # print("Circles", len(approx))
            numberofatt = numberofatt + 1
            # Get Center Point
            M = cv2.moments(contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            CirCentP = Shapes.point(cX, cY)
            # Initialize attribute object to store it into Attributes List with default values
            att = Shapes.attribute("Att" + str(numberofatt), "undefined", CirCentP)
            Attributes.append(att)

            # draw the contour and center of the shape on the image
            # cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
            cv2.circle(Orimg, (cX, cY), 5, (0, 255, 255), -1)
            cv2.putText(Orimg, "Att" + str(numberofatt), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0))
            cv2.drawContours(Orimg, [approx], 0, (255, 0, 0), 2)

    return Orimg, Entities, Relations, Attributes


# The size of masks with trial and check
# Draw the Shapes
def drawShapes(Originalimg, Entities, Relations, Attributes, Lines):
    imgGrey = cv2.cvtColor(Originalimg, cv2.COLOR_BGR2GRAY)
    # Denoise = cv2.medianBlur(imgGrey, 3)
    # cv2.imshow("imgGrey", Denoise)

    _, thresh = cv2.threshold(imgGrey, 100, 255, cv2.THRESH_BINARY)
    cv2.imshow("Thresh", thresh)

    binaryconverted = (255 - thresh)
    cv2.imshow("binaryconverted", binaryconverted)

    binaryconverted1 = fillHole(binaryconverted)
    cv2.imshow("binaryconverted1", binaryconverted1)

    # These operations to make the shapes are sharps so we can detect it effectively
    binaryconverted1 = cv2.erode(binaryconverted1, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    opening = cv2.morphologyEx(binaryconverted1, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10)))
    opening1 = cv2.medianBlur(opening, 3)
    cv2.imshow("opening1", opening1)

    # opening2 = cv2.dilate(opening, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    # cv2.imshow("opening2", opening2)

    # closing = cv2.morphologyEx(binaryconverted1, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7)))
    # cv2.imshow("closing", closing)

    onlyline1 = binaryconverted1 - opening1
    onlyline1 = cv2.medianBlur(onlyline1, 3)
    onlyline1 = cv2.erode(onlyline1, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1)))
    cv2.imshow("onlyline1", onlyline1)

    # onlyline2 = binaryconverted1 - opening2
    # cv2.imshow("onlyline2", onlyline2)

    # edges = cv2.Canny(onlyline2, 150, 400, None, 3)
    # cv2.imshow("edges", edges)

    imgLine, Lines = GetLinesByContours(onlyline1, Originalimg, Lines)
    cv2.imshow("DrawOnlyLine", imgLine)

    shapesImage, Entities, Relations, Attributes = GetShapes(opening1, Originalimg, Entities, Relations, Attributes)
    cv2.imshow("shapesImage", shapesImage)

    return Originalimg, Entities, Relations, Attributes, Lines


# Calculate Distance between two points
def CalcDistance(Point1, Point2):
    return math.sqrt(math.pow(Point1.x - Point2.x, 2) + math.pow(Point1.y - Point2.y, 2))


# Check which shapes are connected to the start point and end point of one line
def ConnectedSh(line, Ents, Rels, Attrs):
    startPointofLine = line.StartPoint
    endPointofLine = line.EndPoint
    # Assume that the input line is connected to first entity
    connectedtostart = Ents[0].name
    connectedtoend = Ents[0].name

    # Calculate the distance between start and end point of line and the other entities center point
    # And the other shapes, if you got the minimum distance less than the temporary one
    # it will be new connected shape
    MinDisSt = CalcDistance(startPointofLine, Ents[0].CenPoint)
    for i in range(1, len(Ents)):
        MinDisTemp = CalcDistance(startPointofLine, Ents[i].CenPoint)
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

    MinDisEnd = CalcDistance(endPointofLine, Ents[0].CenPoint)
    for i3 in range(0, len(Ents)):
        MinDisTemp = CalcDistance(endPointofLine, Ents[i3].CenPoint)
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

    # Return a list has the connected shape to start of the line,
    # and the connected shape to end of the line
    connectedshape = [connectedtostart, connectedtoend]
    return connectedshape, Ents, Rels, Attrs


# Making the list contains only unique items
# While detecting lines, function may detect duplicated line
def unique(list1):
    ConUniq = []
    # to detect if was there a very very short line and delete it
    # it will make the same shape connected to line start point and line end point
    for h in range(0, len(list1)):
        if list1[h][0] != list1[h][1]:
            ConUniq.append(list1[h])
            break

    # For duplicated lines and short lines
    for i in range(1, len(list1)):
        Flag = True
        for j in range(0, len(ConUniq)):
            Tempstr = list1[i][0]
            if (Tempstr == ConUniq[j][0] and list1[i][1] == ConUniq[j][1]) \
                    or (list1[i][0] == ConUniq[j][1] and list1[i][1] == ConUniq[j][0]) \
                    or (list1[i][1] == ConUniq[j][0] and list1[i][0] == ConUniq[j][1]) \
                    or (list1[i][0] == list1[i][1]):
                Flag = False
                break
        if Flag:
            ConUniq.append(list1[i])

    return ConUniq
    
    
def Merge(lines, Ents, Attrs, Rels):
    connectedshapes = []
    # Check which shapes are connected to the start point and end point of all lines
    for i in range(0, len(lines)):
        ConShapes, Ents, Rels, Attrs = ConnectedSh(lines[i], Ents, Rels, Attrs)
        connectedshapes.append(ConShapes)

    # Make it contains unique items as we mentioned above
    Uniqconnectedshapes = unique(connectedshapes)

    # Now make the Merging of shapes to each other
    for i in range(0, len(Uniqconnectedshapes)):
        # If the connected shapes are Entity and Relation
        if "Ent" in Uniqconnectedshapes[i][0] and "Rel" in Uniqconnectedshapes[i][1]:
            stri1 = Uniqconnectedshapes[i][0]
            stri2 = Uniqconnectedshapes[i][1]

            # if This Relation id is still -1, means that the relation is not merged to any entity before
            # int(stri2[len(stri2)-1:]) - 1 == It is the index of the certain shape
            if Rels[int(stri2[len(stri2)-1:]) - 1].id1 == -1:
                # Get the entity id to assign it to the relation
                id1 = Ents[int(stri1[len(stri1)-1:])].getID()
                Rels[int(stri2[len(stri2)-1:]) - 1].id1 = id1
                # Add the Relation to the entity relation list
                Ents[int(stri1[len(stri1) - 1:])].add_relation(Rels[int(stri2[len(stri2)-1:]) - 1])
            # it means that there is an entity merged to this relation, and this entity will be the second one
            elif Rels[int(stri2[len(stri2) - 1:]) - 1].id2 == -1:
                # Get the entity id to assign it to the relation
                id2 = Ents[int(stri1[len(stri1)-1:])].getID()
                Rels[int(stri2[len(stri2)-1:]) - 1].id2 = id2
                # Add the Relation to the entity relation list
                Ents[int(stri1[len(stri1) - 1:])].add_relation(Rels[int(stri2[len(stri2)-1:]) - 1])
                # now, we ensured that there are two entity connected or merged to the relation,
                # so we will assign the relation ID by XORing the two entities ids.
                Rels[int(stri2[len(stri2) - 1:]) - 1].id = Rels[int(stri2[len(stri2)-1:]) - 1].id1 ^ id2

        # Same explanation as above
        elif "Rel" in Uniqconnectedshapes[i][0] and "Ent" in Uniqconnectedshapes[i][1]:
            stri1 = Uniqconnectedshapes[i][1]
            stri2 = Uniqconnectedshapes[i][0]
            index = stri2[len(stri2)-1:]
            if Rels[int(index) - 1].id1 == -1:
                id1 = Ents[int(stri1[len(stri1) - 1:])].getID()
                Rels[int(stri2[len(stri2)-1:]) - 1].id1 = id1
                Ents[int(stri1[len(stri1) - 1:])].add_relation(Rels[int(stri2[len(stri2) - 1:]) - 1])
            elif Rels[int(stri2[len(stri2) - 1:]) - 1].id2 == -1:
                id2 = Ents[int(stri1[len(stri1) - 1:])].getID()
                Rels[int(stri2[len(stri2) - 1:]) - 1].id2 = id2
                Ents[int(stri1[len(stri1) - 1:])].add_relation(Rels[int(stri2[len(stri2) - 1:]) - 1])
                Rels[int(stri2[len(stri2) - 1:]) - 1].id = Rels[int(stri2[len(stri2)-1:]) - 1].id1 ^ id2

        # ==============================================================================================================

        # If the connected shapes are Entity and Attribute
        # We will assign the attributes to the entity attribute list
        # and Making this attribute "Parent" to distinct the composite one
        elif "Ent" in Uniqconnectedshapes[i][0] and "Att" in Uniqconnectedshapes[i][1]:
            stri1 = Uniqconnectedshapes[i][0]
            stri2 = Uniqconnectedshapes[i][1]
            Ents[int(stri1[len(stri1)-1:])].add_attr(Attrs[int(stri2[len(stri2)-1:]) - 1])
            Attrs[int(stri2[len(stri2) - 1:]) - 1].isParent = True

        elif "Att" in Uniqconnectedshapes[i][0] and "Ent" in Uniqconnectedshapes[i][1]:
            stri2 = Uniqconnectedshapes[i][0]
            stri1 = Uniqconnectedshapes[i][1]
            Ents[int(stri1[len(stri1)-1:])].add_attr(Attrs[int(stri2[len(stri2)-1:]) - 1])
            Attrs[int(stri2[len(stri2) - 1:]) - 1].isParent = True

        # ==============================================================================================================

        # If the connected shapes are Relation and Attribute
        # We will assign the attributes to the relation attribute list
        # and Making this attribute "Parent" to distinct the composite one
        elif "Att" in Uniqconnectedshapes[i][0] and "Rel" in Uniqconnectedshapes[i][1]:
            stri1 = Uniqconnectedshapes[i][0]
            stri2 = Uniqconnectedshapes[i][1]
            Rels[int(stri2[len(stri2)-1:]) - 1].add_attrib(Attrs[int(stri1[len(stri1)-1:]) - 1])
            Attrs[int(stri1[len(stri1) - 1:]) - 1].isParent = True
            Attrs[int(stri1[len(stri1) - 1:]) - 1].type = "Non-prime"

        elif "Rel" in Uniqconnectedshapes[i][0] and "Att" in Uniqconnectedshapes[i][1]:
            stri2 = Uniqconnectedshapes[i][0]
            stri1 = Uniqconnectedshapes[i][1]
            Rels[int(stri2[len(stri2)-1:]) - 1].add_attrib(Attrs[int(stri1[len(stri1)-1:]) - 1])
            Attrs[int(stri1[len(stri1) - 1:]) - 1].isParent = True
            Attrs[int(stri1[len(stri1) - 1:]) - 1].type = "Non-prime"

        # ==============================================================================================================

    # initialize the attributes of each entity
    # First Attribute of each entity with "Prime", others are "Non-Prime"
    for i in range(0, len(Ents)):
        Ents[i].attr_list[0].type = "Prime"
        for j in range(1, len(Ents[i].attr_list)):
            Ents[i].attr_list[j].type = "Non-prime"

    # Merge Composite Attribute
    # Check which one of them is the parent = composite to:
    # 1- make the another attribute a child
    # 2- add the child one to Parent attribute children list
    # 3- initialize the prime \ non-prime attributes
    for i in range(0, len(Uniqconnectedshapes)):
        if "Att" in Uniqconnectedshapes[i][0] and "Att" in Uniqconnectedshapes[i][1]:
            stri1 = Uniqconnectedshapes[i][0]
            stri2 = Uniqconnectedshapes[i][1]
            if Attrs[int(stri1[len(stri1) - 1:]) - 1].isParent and \
                    Attrs[int(stri1[len(stri1) - 1:]) - 1].type == "Prime":
                Attrs[int(stri1[len(stri1) - 1:]) - 1].isComposite = True
                Attrs[int(stri1[len(stri1) - 1:]) - 1].add_child(Attrs[int(stri2[len(stri2) - 1:]) - 1])
                Attrs[int(stri2[len(stri2) - 1:]) - 1].type = "Prime"
            elif Attrs[int(stri1[len(stri1) - 1:]) - 1].isParent and \
                    Attrs[int(stri1[len(stri1) - 1:]) - 1].type == "Non-prime":
                Attrs[int(stri1[len(stri1) - 1:]) - 1].isComposite = True
                Attrs[int(stri1[len(stri1) - 1:]) - 1].add_child(Attrs[int(stri2[len(stri2) - 1:]) - 1])
                Attrs[int(stri2[len(stri2) - 1:]) - 1].type = "Non-prime"

            elif Attrs[int(stri2[len(stri2) - 1:]) - 1].isParent and \
                    Attrs[int(stri2[len(stri2) - 1:]) - 1].type == "Prime":
                Attrs[int(stri2[len(stri2) - 1:]) - 1].isComposite = True
                Attrs[int(stri2[len(stri2) - 1:]) - 1].add_child(Attrs[int(stri1[len(stri1) - 1:]) - 1])
                Attrs[int(stri1[len(stri1) - 1:]) - 1].type = "Prime"
            elif Attrs[int(stri2[len(stri2) - 1:]) - 1].isParent and \
                    Attrs[int(stri2[len(stri2) - 1:]) - 1].type == "Non-prime":
                Attrs[int(stri2[len(stri2) - 1:]) - 1].isComposite = True
                Attrs[int(stri2[len(stri2) - 1:]) - 1].add_child(Attrs[int(stri1[len(stri1) - 1:]) - 1])
                Attrs[int(stri1[len(stri1) - 1:]) - 1].type = "Non-prime"

    # ==================================================================================================================

    return Uniqconnectedshapes, Ents, Rels, Attrs


def ERD_Project(Original):
    Entities = []
    Relations = []
    Attributes = []
    Lines = []

    cv2.imshow("img", Original)
    Test1, Entities, Relations, Attributes, Lines = drawShapes(Original, Entities, Relations, Attributes, Lines)
    Test2, Entities, Relations, Attributes = Merge(Lines, Entities, Attributes, Relations)
    print("Smile", Test2)
    FinalEntitiesList = Entities

    return FinalEntitiesList


img = cv2.imread('\ASU\Senior\Flowchart10.png')
Final_Entities_List = ERD_Project(img)


# Exiting the window if 'q' is pressed on the keyboard.
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()
