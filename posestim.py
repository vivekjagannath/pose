import cv2
import time
import numpy as np
from random import randint
import math

#creating global variables to store the co-ordinates
x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5 = (
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
)

def advaykafunc():
    global x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5
    #index 0 for integrated web cam change to 1/2 accordingly for usb camera
    cap = cv2.VideoCapture(0)
    neck, ell, elr, pmr, pml, Rsho, Lsho = (
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
    )

    #path for the trianed models
    protoFile = "pose/coco/pose_deploy_linevec.prototxt"
    weightsFile = "pose/coco/pose_iter_440000.caffemodel"
    nPoints = 18

    # COCO Output Format
    keypointsMapping = [
        "Nose",
        "Neck",
        "R-Sho",
        "R-Elb",
        "R-Wr",
        "L-Sho",
        "L-Elb",
        "L-Wr",
        "R-Hip",
        "R-Knee",
        "R-Ank",
        "L-Hip",
        "L-Knee",
        "L-Ank",
        "R-Eye",
        "L-Eye",
        "R-Ear",
        "L-Ear",
    ]

    POSE_PAIRS = [
        [1, 2],
        [1, 5],
        [2, 3],
        [3, 4],
        [5, 6],
        [6, 7],
        [1, 8],
        [8, 9],
        [9, 10],
        [1, 11],
        [11, 12],
        [12, 13],
        [1, 0],
        [0, 14],
        [14, 16],
        [0, 15],
        [15, 17],
        [2, 17],
        [5, 16],
    ]

    # index of pafs correspoding to the POSE_PAIRS
    # e.g for POSE_PAIR(1,2), the PAFs are located at indices (31,32) of output, Similarly, (1,5) -> (39,40) and so on.

    mapIdx = [
        [31, 32],
        [39, 40],
        [33, 34],
        [35, 36],
        [41, 42],
        [43, 44],
        [19, 20],
        [21, 22],
        [23, 24],
        [25, 26],
        [27, 28],
        [29, 30],
        [47, 48],
        [49, 50],
        [53, 54],
        [51, 52],
        [55, 56],
        [37, 38],
        [45, 46],
    ]

    colors = [
        [0, 100, 255],
        [0, 100, 255],
        [0, 255, 255],
        [0, 100, 255],
        [0, 255, 255],
        [0, 100, 255],
        [0, 255, 0],
        [255, 200, 100],
        [255, 0, 255],
        [0, 255, 0],
        [255, 200, 100],
        [255, 0, 255],
        [0, 0, 255],
        [255, 0, 0],
        [200, 200, 0],
        [255, 0, 0],
        [200, 200, 0],
        [0, 0, 0],
    ]

    def getKeypoints(probMap, threshold=0.1):
        mapSmooth = cv2.GaussianBlur(probMap, (3, 3), 0, 0)
        mapMask = np.uint8(mapSmooth > threshold)
        keypoints = []
        # find the blobs
        im3, contours, _ = cv2.findContours(
            mapMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        # for each blob find the maxima
        for cnt in contours:
            blobMask = np.zeros(mapMask.shape)
            blobMask = cv2.fillConvexPoly(blobMask, cnt, 1)
            maskedProbMap = mapSmooth * blobMask
            _, maxVal, _, maxLoc = cv2.minMaxLoc(maskedProbMap)
            keypoints.append(maxLoc + (probMap[maxLoc[1], maxLoc[0]],))
        return keypoints

    # Find valid connections between the different joints of a all persons present

    def getValidPairs(output):
        valid_pairs = []
        invalid_pairs = []
        n_interp_samples = 10
        paf_score_th = 0.1
        conf_th = 0.7

        # loop for every POSE_PAIR
        for k in range(len(mapIdx)):
            # A->B constitute a limb
            pafA = output[0, mapIdx[k][0], :, :]
            pafB = output[0, mapIdx[k][1], :, :]
            pafA = cv2.resize(pafA, (frameWidth, frameHeight))
            pafB = cv2.resize(pafB, (frameWidth, frameHeight))

            # Find the keypoints for the first and second limb
            candA = detected_keypoints[POSE_PAIRS[k][0]]
            candB = detected_keypoints[POSE_PAIRS[k][1]]
            nA = len(candA)
            nB = len(candB)

            # If keypoints for the joint-pair is detected
            # check every joint in candA with every joint in candB
            # Calculate the distance vector between the two joints
            # Find the PAF values at a set of interpolated points between the joints
            # Use the above formula to compute a score to mark the connection valid

            if nA != 0 and nB != 0:
                valid_pair = np.zeros((0, 3))
                for i in range(nA):
                    max_j = -1
                    maxScore = -1
                    found = 0
                    for j in range(nB):
                        # Find d_ij
                        d_ij = np.subtract(candB[j][:2], candA[i][:2])
                        norm = np.linalg.norm(d_ij)
                        if norm:
                            d_ij = d_ij / norm
                        else:
                            continue
                        # Find p(u)
                        interp_coord = list(
                            zip(
                                np.linspace(
                                    candA[i][0], candB[j][0], num=n_interp_samples
                                ),
                                np.linspace(
                                    candA[i][1], candB[j][1], num=n_interp_samples
                                ),
                            )
                        )

                        # Find L(p(u))
                        paf_interp = []
                        for k in range(len(interp_coord)):
                            paf_interp.append(
                                    pafA[
                                        int(round(interp_coord[k][1])),
                                        int(round(interp_coord[k][0])),
                                    ],
                                    pafB[
                                        int(round(interp_coord[k][1])),
                                        int(round(interp_coord[k][0])),
                                    ],
                                ]
                            )

                        # Find E
                        paf_scores = np.dot(paf_interp, d_ij)
                        avg_paf_score = sum(paf_scores) / len(paf_scores)

                        # Check if the connection is valid
                        # If the fraction of interpolated vectors aligned with PAF is higher then threshold -> Valid Pair

                        if (
                            len(np.where(paf_scores > paf_score_th)[0])
                            / n_interp_samples
                        ) > conf_th:

                            if avg_paf_score > maxScore:
                                max_j = j
                                maxScore = avg_paf_score
                                found = 1

                    # Append the connection to the list
                    if found:
                        valid_pair = np.append(
                            valid_pair,
                            [[candA[i][3], candB[max_j][3], maxScore]],
                            axis=0,
                        )

                # Append the detected connections to the global list
                valid_pairs.append(valid_pair)
            else:  # If no keypoints are detected
                # print("No Connection : k = {}".format(k))
                invalid_pairs.append(k)
                valid_pairs.append([])
        return valid_pairs, invalid_pairs

    # This function creates a list of keypoints belonging to each person
    # For each detected valid pair, it assigns the joint(s) to a person

    def getPersonwiseKeypoints(valid_pairs, invalid_pairs):
        # the last number in each row is the overall score
        personwiseKeypoints = -1 * np.ones((0, 19))
        for k in range(len(mapIdx)):
            if k not in invalid_pairs:
                partAs = valid_pairs[k][:, 0]
                partBs = valid_pairs[k][:, 1]
                indexA, indexB = np.array(POSE_PAIRS[k])
                for i in range(len(valid_pairs[k])):
                    found = 0
                    person_idx = -1
                    for j in range(len(personwiseKeypoints)):
                        if personwiseKeypoints[j][indexA] == partAs[i]:
                            person_idx = j
                            found = 1
                            break
                    if found:
                        personwiseKeypoints[person_idx][indexB] = partBs[i]
                        personwiseKeypoints[person_idx][-1] += (
                            keypoints_list[partBs[i].astype(int), 2]
                            + valid_pairs[k][i][2]
                        )

                    # if find no partA in the subset, create a new subset

                    elif not found and k < 17:
                        row = -1 * np.ones(19)
                        row[indexA] = partAs[i]
                        row[indexB] = partBs[i]

                        # add the keypoint_scores for the two keypoints and the paf_score
                        row[-1] = (
                            sum(keypoints_list[valid_pairs[k][i, :2].astype(int), 2])
                            + valid_pairs[k][i][2]
                        )
                        personwiseKeypoints = np.vstack([personwiseKeypoints, row])
        return personwiseKeypoints

    frameWidth = 640
    frameHeight = 480
    t = time.time()
    net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

    # Fix the input Height and get the width according to the Aspect Ratio
    # inHeight = 368
    # inWidth = int((inHeight/frameHeight)*frameWidth)

    num = 1
    while True:
        ret, image1 = cap.read()
        #reduce the resize arguments for increase in speed and increase the arguments for increase in accuracy
        inpBlob = cv2.dnn.blobFromImage(
            image1, 1.0 / 255, (150, 150), (0, 0, 0), swapRB=False, crop=False
        )
        net.setInput(inpBlob)
        output = net.forward()

        # print("Time Taken in forward pass = {}".format(time.time() - t))

        detected_keypoints = []
        keypoints_list = np.zeros((0, 3))
        keypoint_id = 0
        threshold = 0.1
        for part in range(nPoints):
            probMap = output[0, part, :, :]
            probMap = cv2.resize(probMap, (image1.shape[1], image1.shape[0]))
            keypoints = getKeypoints(probMap, threshold)
            #assigning only neck,shoulders,elbows and wrists
            if len(keypoints) != 0:
                if keypointsMapping[part] == "Neck":
                    neck = (keypoints[0][0], keypoints[0][1])
                    
                    # print keypointsMapping[part],neck
                    x0, y0 = neck[0], neck[1]
                if keypointsMapping[part] == "R-Sho":
                    Rsho = (keypoints[0][0], keypoints[0][1])
                    # print keypointsMapping[part],Rsho
                    x1, y1 = Rsho[0], Rsho[1]
                if keypointsMapping[part] == "L-Sho":
                    Lsho = (keypoints[0][0], keypoints[0][1])
                    # print keypointsMapping[part],Lsho
                    x2, y2 = Lsho[0], Lsho[1]
                if keypointsMapping[part] == "R-Elb":
                    elr = (keypoints[0][0], keypoints[0][1])
                    # print keypointsMapping[part],elr
                    x3, y3 = elr[0], elr[1]
                if keypointsMapping[part] == "L-Elb":
                    ell = (keypoints[0][0], keypoints[0][1])
                    # print keypointsMapping[part],ell
                    x4, y4 = ell[0], ell[1]
                if keypointsMapping[part] == "R-Wr":
                    pmr = (keypoints[0][0], keypoints[0][1])
                    # print keypointsMapping[part],pmr
                    x5, y5 = pmr[0], pmr[1]
                if keypointsMapping[part] == "L-Wr":
                    pml = (keypoints[0][0], keypoints[0][1])
                    # print keypointsMapping[part],pml
                    x6, y6 = pml[0], pml[1]
            keypoints_with_id = []
            for i in range(len(keypoints)):
                keypoints_with_id.append(keypoints[i] + (keypoint_id,))
                keypoints_list = np.vstack([keypoints_list, keypoints[i]])
                keypoint_id += 1
            detected_keypoints.append(keypoints_with_id)
        frameClone = image1.copy()

        # for i in range(nPoints):
        #     for j in range(len(detected_keypoints[i])):
        #         cv2.circle(frameClone, detected_keypoints[i][j][0:2], 5, colors[i], -1, cv2.LINE_AA)
        # cv2.imshow("Keypoints",frameClone)

        valid_pairs, invalid_pairs = getValidPairs(output)
        personwiseKeypoints = getPersonwiseKeypoints(valid_pairs, invalid_pairs)
        for i in range(17):
            for n in range(len(personwiseKeypoints)):
                index = personwiseKeypoints[n][np.array(POSE_PAIRS[i])]
                if -1 in index:
                    continue
                B = np.int32(keypoints_list[index.astype(int), 0])
                A = np.int32(keypoints_list[index.astype(int), 1])
                cv2.line(
                    frameClone, (B[0], A[0]), (B[1], A[1]), colors[i], 3, cv2.LINE_AA
                )
        cv2.imshow("Detected Pose", frameClone)
        k = cv2.waitKey(1)
        if k == 27:
            cv2.destroyAllWindows()
        return x6, y6, x4, y4, x2, y2, x0, y0, x1, y1, x3, y3, x5, y5

    #         break
    #     elif k == ord("c"):
    #         name=str(num+1)+".jpg"
    #         cv2.imwrite(name,frameClone)
    #         break
    # #yi=cv2.imread(name)
    # #cv2.imshow("n",yi)
    # #cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # # def dis(x1,y1,x2,y2):
    # #     return math.hypot(x2 - x1, y2 - y1)
    # # l1 = dis(Lsho[0],Lsho[1],ell[0],ell[1])
    # # print ("l1",l1)
    # # l2 = dis(pml[0],pml[1],ell[0],ell[1])
    # # print ("l2",l2)
    # # r1 = dis(Rsho[0],Rsho[1],elr[0],elr[1])
    # # print ("r1",r1)
    # # r2 = dis(elr[0],elr[1],pmr[0],pmr[1])
    # # print ("r2",r2)
    # # s = dis(Lsho[0],Lsho[1],Rsho[0],Rsho[1])
    # # print ("s",s)
    # # print("r1/r2",r1/r2)
    # # print("l1/l2",l1/l2)
    # # print("s/l1",s/l1)
    # # print("s/r1",s/r1)
    # print (x6,y6,x4,y4,x2,y2,x0,y0,x1,y1,x3,y3,x5,y5)
