import math
import apriltag;
import cv2;
import numpy as np;
import sys;

# purple, 240-360, 0-255, 150-255
purpleL = np.array([240 // 2, 0, 150]); # openCV uses 0-180 for hue
purpleH = np.array([360 // 2, 255, 255]);
# white, 0-240, 0-80, 180-255
whiteL = np.array([0, 0, 180]);
whiteH = np.array([240 // 2, 80, 255]);
# green 60-150, 70-195, 140-230
greenL = np.array([60 // 2, 70, 140]);
greenH = np.array([150 // 2, 195, 230]);
# yellow 0-60 100-255, 180-255
yellowL = np.array([0, 100, 180]);
yellowH = np.array([60 // 2, 255, 255]);

def matchColor(color):
    # turn color into a 1x1 image
    image = np.full((1, 1, 3), color, dtype=np.uint8);
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV);
    if cv2.inRange(hsv, purpleL, purpleH).all():
        return "p";
    elif cv2.inRange(hsv, whiteL, whiteH).all():
        return "w";
    elif cv2.inRange(hsv, greenL, greenH).all():
        return "g";
    elif cv2.inRange(hsv, yellowL, yellowH).all():
        return "y";
    else:
        return "";

def matchColors(colors): 
    firstMatch = matchColor(colors[0]);
    secondMatch = matchColor(colors[1]);
    thirdMatch = matchColor(colors[2]);
    fourthMatch = matchColor(colors[3]);
    if firstMatch != secondMatch or firstMatch != thirdMatch or firstMatch != fourthMatch:
        return "" # they all have to be the same
    return firstMatch;

def getColor(color):
    if color == "p":
        return (255, 0, 255);
    elif color == "w":
        return (255, 255, 255);
    elif color == "g":
        return (0, 255, 0);
    elif color == "y":
        return (0, 255, 255);
    else:
        return (0, 0, 0);

def showImage(image):
    cv2.imshow('image', image);
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break;
    cv2.destroyAllWindows();

image = cv2.imread('rsz_input.jpg', cv2.IMREAD_ANYCOLOR);
output = image.copy();
detections = apriltag.Detector().detect(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY));

apriltagColumns = [];

height = [];
y = [];

for detection in detections:
    cv2.drawContours(image, [np.array(detection.corners, dtype=np.int32)], -1, (255, 0, 255), 2);
    #circle corners
    cv2.circle(image, (int(detection.corners[0][0]), int(detection.corners[0][1])), 5, (255, 0, 0), -1);
    cv2.circle(image, (int(detection.corners[1][0]), int(detection.corners[1][1])), 5, (255, 255, 0), -1);
    cv2.circle(image, (int(detection.corners[2][0]), int(detection.corners[2][1])), 5, (0, 255, 0), -1);
    cv2.circle(image, (int(detection.corners[3][0]), int(detection.corners[3][1])), 5, (0, 255, 255), -1);
    # cv2.line(image, (int(detection.center[0]), 0), (int(detection.center[0]), int(image.shape[0])), (255, 0, 255), 2);
    apriltagColumns.append(int(detection.center[0]));
    leftHeight = abs(detection.corners[0][1] - detection.corners[3][1]);
    rightHeight = abs(detection.corners[1][1] - detection.corners[2][1]);
    avgHeight = (leftHeight + rightHeight) / 2;
    height.append(avgHeight);
    y.append(detection.center[1]);

avgHeight = sum(height) / len(height);
avgY = sum(y) / len(y);

avgGap = (apriltagColumns[1] - apriltagColumns[0] + apriltagColumns[2] - apriltagColumns[1]) / 2;

inbetween = [];

for i in range(1, len(apriltagColumns)):
    inbetween.append((apriltagColumns[i] + apriltagColumns[i - 1]) / 2);

# for i in range(len(inbetween)):
#     cv2.line(image, (int(inbetween[i]), 0), (int(inbetween[i]), int(image.shape[0])), (0, 255, 0), 2);

left = int(apriltagColumns[0] - avgGap / 2);
right = int(apriltagColumns[2] + avgGap / 2);

# cv2.line(image, (left, 0), (left, int(image.shape[0])), (0, 255, 0), 2);
# cv2.line(image, (right, 0), (right, int(image.shape[0])), (0, 255, 0), 2);

colorCheckOffsetX = avgGap * 1 / 6;
colorCheckOffsetY = avgHeight * 0.6

cols = [];
cols.append(left);
cols.append(right);
cols.extend(inbetween);
cols.extend(apriltagColumns);

cols.sort();

# for i in range(len(cols)):
#     cv2.line(image, (int(cols[i]), 0), (int(cols[i]), int(image.shape[0])), (0, 255, 0), 2);
#     # left of col and right of col
#     left = int(cols[i] - colorCheckOffset);
#     right = int(cols[i] + colorCheckOffset);
#     cv2.line(image, (left, 0), (left, int(image.shape[0])), (0, 0, 255), 2);
#     cv2.line(image, (right, 0), (right, int(image.shape[0])), (0, 0, 255), 2);
    
# print(avgHeight, height)

baseLine = avgY - avgHeight * 1.9;
rowHeight = avgHeight * 1.3

board = [
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""]
]

for i in range(len(board)):
    for j in range(len(board[i])):
        board[i][j] = ".";

for i in range(0, 11):
    y = int(baseLine - i * rowHeight);
    if i % 2 == 0:
      # cv2.line(image, (0, y), (int(image.shape[1]), y), (255, 0, 0), 2); # 6
      for j in range(6):
          col = cols[j] + avgGap / 4;
          left = int(col - colorCheckOffsetX);
          right = int(col + colorCheckOffsetX)
          top = int(y - colorCheckOffsetY);
          bottom = int(y + colorCheckOffsetY);

          colors = [];
          colors.append(image[y, left]);
          colors.append(image[y, right]);
          colors.append(image[top, int(col)]);
          colors.append(image[bottom, int(col)]);
          color = matchColors(colors);
          if (color != ""):
              board[i][j] = color;
              drawColor = getColor(color);
              cv2.circle(output, (int(col), y), 5, drawColor, -1);
    else:
      # cv2.line(image, (0, y), (int(image.shape[1]), y), (0, 255, 0), 2); # 7
      for j in range(7):
          col = cols[j];
          left = int(col - colorCheckOffsetX);
          right = int(col + colorCheckOffsetX);
          top = int(y - colorCheckOffsetY);
          bottom = int(y + colorCheckOffsetY);

          colors = [];
          colors.append(image[y, left]);
          colors.append(image[y, right]);
          colors.append(image[top, int(col)]);
          colors.append(image[bottom, int(col)]);
          color = matchColors(colors);
          if (color != ""):
              board[i][j] = color;
              drawColor = getColor(color);
              cv2.circle(output, (int(col), y), 5, drawColor, -1);

for i in range(len(board) - 1, -1, -1):
    if i % 2 == 0:
        print(" ", end="");
    for j in range(len(board[i])):
        print(f" {board[i][j]}", end="");
    print("");

showImage(output);
