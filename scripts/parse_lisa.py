import os
import argparse
from PIL import Image
import random


def convert(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

parser = argparse.ArgumentParser(description='Mark or crop each annotation.',
                                 epilog='This program will create a directory called \'annotations\' and save the output there. The directory will be created in the folder where the annotation file is located. If the directory exists already, that will be used, and any existing files will be overwritten.')
parser.add_argument('path', metavar='filename.csv', type=str,
                    help='The path to the csv-file containing the annotations.')
args = parser.parse_args()

if not os.path.isfile(args.path):
    print("The given annotation file does not exist.\nSee annotateVisually.py -h for more info.")
    exit()

categories = ["addedLane", "curveRight", "dip", "intersection", "laneEnds", "merge", "pedestrianCrossing", "signalAhead",
              "slow", "stopAhead", "thruMergeLeft", "thruMergeRight", "turnLeft", "turnRight", "yieldAhead","doNotPass",
              "keepRight", "rightLaneMustTurn", "speedLimit15", "speedLimit25", "speedLimit30", "speedLimit35",
              "speedLimit40", "speedLimit45", "speedLimit50", "speedLimit55", "speedLimit65", "truckSpeedLimit55",
              'rampSpeedAdvisory50', 'school', 'rampSpeedAdvisory40', 'rampSpeedAdvisoryUrdbl', 'noLeftTurn',
              'rampSpeedAdvisory45', 'noRightTurn', 'stop', 'zoneAhead25', 'yield', 'curveLeft', 'rampSpeedAdvisory20',
              'doNotEnter', 'rampSpeedAdvisory35', 'speedLimitUrdbl', 'roundabout', 'schoolSpeedLimit25', 'zoneAhead45',
              'thruTrafficMergeLeft']
'''
'rampSpeedAdvisory50', 'school', 'rampSpeedAdvisory40', 'rampSpeedAdvisoryUrdbl', 'noLeftTurn', 'rampSpeedAdvisory45', 'noRightTurn', 'stop', 'zoneAhead25', 'yield', 'curveLeft', 'rampSpeedAdvisory20', 'doNotEnter', 'rampSpeedAdvisory35', 'speedLimitUrdbl', 'roundabout', 'schoolSpeedLimit25', 'zoneAhead45', 'thruTrafficMergeLeft'
'''
unsupportedCategories = set([])
csv = open(os.path.abspath(args.path), 'r')
csv.readline()  # Discard the header-line.
csv = csv.readlines()
csv.sort()

basePath = os.path.dirname(args.path)
savePath = os.path.join(basePath, 'annotations')
if not os.path.isdir(savePath):
    os.mkdir(savePath)

wd = os.getcwd()
train_file = open('%s/train.txt' % wd, 'w')
test_file = open('%s/test.txt' % wd, 'w')

im = Image.new('RGB', (1,1))
counter = 0
counterPerFile = 0
previousFile = ''
for line in csv:
    fields = line.split(";")
    (nameWithoutExtention, extention) = os.path.splitext(os.path.basename(fields[0]))
    if(nameWithoutExtention == 'stop_1330545910.avi_image0'):
        print('Debugging:')
    if fields[0] != previousFile:  # Save the drawn annotations and open the next file.
        if previousFile == 'stop_1330545910.avi_image0':
            exit(-1)
        """ Open output text files """
        basePath = os.path.dirname(fields[0])
        savePath = os.path.join(basePath, 'annotations')
        if not os.path.isdir(savePath):
            os.mkdir(savePath)
        txt_outpath = os.path.join(savePath, nameWithoutExtention + ".txt")
        counterPerFile = 0
        print("New label file:" + txt_outpath)
        txt_outfile = open(txt_outpath, "w")
        im = Image.open(os.path.join(wd, fields[0]))

    width = int(im.size[0]);
    height = int(im.size[1]);
    box = [int(fields[2]), int(fields[4]), int(fields[3]), int(fields[5])]
    print("Before convertion (width, height) and box (minX, maxX, minY, maxY): " + str((width, height)) + " " + str(box))
    bb = convert((width, height), box)
    print("YOLO box: " + str(bb))
    '''
    Filename;Annotation tag;Upper left corner X;Upper left corner Y;Lower right corner X;Lower right corner Y;Occluded
    '''
    if fields[1] not in categories:
        unsupportedCategories.add(fields[1])
        continue;

    cls_id = categories.index(fields[1])

    print(bb)
    txt_outfile.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
    print("Adding more box: " + txt_outpath)
    previousFile = fields[0]
    counter += 1
    counterPerFile += 1
    """ Save those images with bb into list"""
    probo = random.randint(1, 100)
    print("Probobility: %d" % probo)
    if(probo > 75):
        print("Adding %s to test set" % fields[0])
        test_file.write('%s/%s.png\n' % (wd, nameWithoutExtention))
    else:
        print("Adding %s to training set" % fields[0])
        train_file.write('%s/%s.png\n' % (wd, nameWithoutExtention))

train_file.close()
test_file.close()
if len(unsupportedCategories) > 0:
    print('Found unsupported categories: ' + str(unsupportedCategories))
print()
print("Done. Processed %d annotations." % (counter + 1))
