from tools.segment.predict import run

run(
    weights="tools/best.pt",  # model.pt path(s)
    source="/Users/deu/Downloads/test.jpg",  # file/dir/URL/glob/screen/0(webcam)
    #data=ROOT / "data/coco128.yaml",  # dataset.yaml path
    imgsz=(1280, 1280),  # inference size (height, width)
    conf_thres=0.25,  # confidence threshold
    iou_thres=0.45,  # NMS IOU threshold
    max_det=3000,  # maximum detections per image
    device="mps",  # cuda device, i.e. 0 or 0,1,2,3 or cpu
    view_img=True,  # show results
    save_txt=False,  # save results to *.txt
    save_conf=False,  # save confidences in --save-txt labels
    save_crop=False,  # save cropped prediction boxes
    nosave=True,  # do not save images/videos
    classes=None,  # filter by class: --class 0, or --class 0 2 3
    agnostic_nms=False,  # class-agnostic NMS
    augment=False,  # augmented inference
    visualize=True,  # visualize features
    update=False,  # update all models
    project="runs/predict-seg",  # save results to project/name
    name="exp",  # save results to project/name
    exist_ok=False,  # existing project/name ok, do not increment
    line_thickness=3,  # bounding box thickness (pixels)
    hide_labels=False,  # hide labels
    hide_conf=False,  # hide confidences
    half=True,  # use FP16 half-precision inference
    dnn=False,  # use OpenCV DNN for ONNX inference
    vid_stride=1,  # video frame-rate stride
    retina_masks=True,
)