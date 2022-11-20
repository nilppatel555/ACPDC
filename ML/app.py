import cv2
import layoutparser as lp
from paddleocr import PaddleOCR,draw_ocr
import tensorflow as tf
import numpy as np

def OCR(img):

  image = cv2.imread(img)
  image = image[..., ::-1]

  # load model
  model = lp.PaddleDetectionLayoutModel(config_path="lp://PubLayNet/ppyolov2_r50vd_dcn_365e_publaynet/config",
                                  threshold=0.5,
                                  label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"},
                                  enforce_cpu=True)
  # detect
  layout = model.detect(image)
  print(layout)

  for l in layout:
          x_1=int(l.block.x_1)
          y_1=int(l.block.y_1)
          x_2=int(l.block.x_2)
          y_2=int(l.block.y_2)
          break

  im=cv2.imread(img)
  cv2.imwrite("op.jpg",im[y_1:y_2,x_1:x_2])

  ocr = PaddleOCR(lang='en', use_gpu=False, use_angle_cls=True)
  image_path = 'op.jpg'
  image_cv = cv2.imread(image_path)
  image_height = image_cv.shape[0]
  image_width = image_cv.shape[1]
  output = ocr.ocr(image_path, cls=True)

  print(output)

  boxes = [line[0] for line in output[0]]
  texts = [line[1][0] for line in output[0]]
  probabilities = [line[1][1] for line in output[0]]

  image_boxes = image_cv.copy()

  for box,text in zip(boxes,texts):
    cv2.rectangle(image_boxes, (int(box[0][0]),int(box[0][1])), (int(box[2][0]),int(box[2][1])),(0,0,255),1)
    cv2.putText(image_boxes, text,(int(box[0][0]),int(box[0][1])),cv2.FONT_HERSHEY_SIMPLEX,1,(222,0,0),1)

  cv2.imwrite('detections.jpg', image_boxes)

  im = image_cv.copy()

  horiz_boxes = []
  vert_boxes = []

  for box in boxes:
    x_h, x_v = 0,int(box[0][0])
    y_h, y_v = int(box[0][1]),0
    width_h,width_v = image_width, int(box[2][0]-box[0][0])
    height_h,height_v = int(box[2][1]-box[0][1]),image_height

    horiz_boxes.append([x_h,y_h,x_h+width_h,y_h+height_h])
    vert_boxes.append([x_v,y_v,x_v+width_v,y_v+height_v])

    cv2.rectangle(im,(x_h,y_h), (x_h+width_h,y_h+height_h),(0,0,255),1)
    cv2.rectangle(im,(x_v,y_v), (x_v+width_v,y_v+height_v),(0,255,0),1)
    
    cv2.imwrite('horiz_vert.jpg',im)

  horiz_out = tf.image.non_max_suppression(
      horiz_boxes,
      probabilities,
      max_output_size = 1000,
      iou_threshold=0.1,
      score_threshold=float('-inf'),
      name=None
  )

  horiz_lines = np.sort(np.array(horiz_out))
  print(horiz_lines)

  im_nms = image_cv.copy()

  for val in horiz_lines:
    cv2.rectangle(im_nms, (int(horiz_boxes[val][0]),int(horiz_boxes[val][1])), (int(horiz_boxes[val][2]),int(horiz_boxes[val][3])),(0,0,255),1)
    
  cv2.imwrite('im_nms.jpg',im_nms)

  vert_out = tf.image.non_max_suppression(
      vert_boxes,
      probabilities,
      max_output_size = 1000,
      iou_threshold=0.1,
      score_threshold=float('-inf'),
      name=None
  )

  print(vert_out)

  vert_lines = np.sort(np.array(vert_out))
  print(vert_lines)

  for val in vert_lines:
    cv2.rectangle(im_nms, (int(vert_boxes[val][0]),int(vert_boxes[val][1])), (int(vert_boxes[val][2]),int(vert_boxes[val][3])),(255,0,0),1)
    
  cv2.imwrite('im_nms.jpg',im_nms)

  out_array = [["" for i in range(len(vert_lines))] for j in range(len(horiz_lines))]
  print(np.array(out_array).shape)
  print(out_array)

  unordered_boxes = []

  for i in vert_lines:
    print(vert_boxes[i])
    unordered_boxes.append(vert_boxes[i][0])

  ordered_boxes = np.argsort(unordered_boxes)
  print(ordered_boxes)

  def intersection(box_1, box_2):
    return [box_2[0], box_1[1],box_2[2], box_1[3]]

  def iou(box_1, box_2):

    x_1 = max(box_1[0], box_2[0])
    y_1 = max(box_1[1], box_2[1])
    x_2 = min(box_1[2], box_2[2])
    y_2 = min(box_1[3], box_2[3])

    inter = abs(max((x_2 - x_1, 0)) * max((y_2 - y_1), 0))
    if inter == 0:
        return 0
        
    box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
    box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))
    
    return inter / float(box_1_area + box_2_area - inter)

  for i in range(len(horiz_lines)):
    for j in range(len(vert_lines)):
      resultant = intersection(horiz_boxes[horiz_lines[i]], vert_boxes[vert_lines[ordered_boxes[j]]] )

      for b in range(len(boxes)):
        the_box = [boxes[b][0][0],boxes[b][0][1],boxes[b][2][0],boxes[b][2][1]]
        if(iou(resultant,the_box)>0.1):
          out_array[i][j] = texts[b]

  out_array=np.array(out_array)

  output_list=out_array.tolist()
  for i in output_list:
    for j in i:
      if j=='':
        i.remove(j)
  #print(output_list)
  e=[]
  m=[]
  s=[]
  for i in output_list:
    print(i)
    for j in i:
      if "statement of marks" in j.lower() or "statement of" in j.lower():
        i2=output_list.index(i)+1
        for j1 in output_list[i2]:
          if "this is to certify that" in j1.lower() or "this is to" in j1.lower() or "to certify that" in j1.lower() or "certify that" in j1.lower() or "is to certify" in j1.lower() or "is to" in j1.lower() or "Chis" in j1.lower():
              name=output_list[i2+1][0]
              print(f"Name: {output_list[i2+1][0]}")
              if(output_list[i2+1][0] is not None):
                break
          else:
              name=output_list[i2][0]
              print(f"Name: {output_list[i2][0]}")
              if(output_list[i2][0] is not None):
                break
      if "seatno" in j.lower() or "seat no" in j.lower() or "seat" in j.lower():
        i2=output_list.index(i)+1
        for j1 in output_list[i2]:
          if len(j1)==8 and j1.isnumeric()==False:
            seat=j1
            print(f"seat:{seat}")
      if "name of student" in j.lower():
        name= j[j.index("dent")+4:]
        print(f"Name:{name}")
      if "roll no." in j.lower() or "roll " in j.lower():
        print(j)
        seat=j[j.index("No.")+3:]
        print(f"Seat:{seat}")
        break

    i = list(dict.fromkeys(i))
    i.pop(0)
    for j in i:
      #print(i)
      
      if "english" in j.lower() or "eng" in j.lower() or "lish" in j.lower():
        for marks in i:
              if '#' in marks:
                i.append(marks[0:marks.index("#")])
              if '*' in marks:
                i.append(marks[0:marks.index("*")])
              if marks.isnumeric()==True and int(marks)<=100:
                e.append(int(marks))
        english_marks=max(e)
        print(f"ENGLISH: {english_marks}")
          
      if "math" in j.lower():
        for marks in i:
            if '#' in marks:
              i.append(marks[0:marks.index("#")])
            if '*' in marks:
              i.append(marks[0:marks.index("*")])
            if marks.isnumeric()==True and int(marks)<=100:
              m.append(int(marks))
        maths_marks=max(m)
        print(f"MATHS: {maths_marks}")

      if "science" in j.lower() or "sci" in j.lower() or "ence" in j.lower():
        if "social" not in j.lower() or "soc" not in j.lower() or "ial" not in j.lower():
          for marks in i:
            if '#' in marks:
              i.append(marks[0:marks.index("#")])
            if '*' in marks:
              i.append(marks[0:marks.index("*")])
            if marks.isnumeric()==True and int(marks)<=100:
              s.append(int(marks))
          science_marks=max(s)
          print(f"SCIENCE: {science_marks}")
  return english_marks,maths_marks,science_marks,name,seat
  