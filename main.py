import torch, cv2
import numpy as np

model = torch.hub.load( 'ultralytics/yolov5', 
                        'custom', 
                        '/Users/deu/translator/best.pt', 
                        device='mps',
                        autoshape=False)

img = torch.rand(1, 3, 640, 640).to("mps")

model.eval()
with torch.no_grad():
    pred = model(img)

img_path = '/Users/deu/Downloads/test.jpg'
img0 = cv2.imread(img_path)  # BGR
h, w = img0.shape[:2]
# Ensure dimensions are divisible by model stride (e.g., 32)
stride = model.stride  # Typically 32
h = h - (h % stride)
w = w - (w % stride)
img0 = cv2.resize(img0, (w, h))  # Resize to stride-compatible dimensions
img = img0.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
img = np.ascontiguousarray(img)
img = torch.from_numpy(img).to(model.device).float() / 255.0
img = img[None]  # [1, 3, h, w]

model.eval()
with torch.no_grad():
    pred, proto = model(img)  # Get predictions and proto for segmentation


def process_mask_native(protos, masks_in, bboxes, shape):
    _, c, mh, mw, d = protos.shape  # [1, 3, 120, 160, 46]
    protos = protos.squeeze(0)  # [3, 120, 160, 46]
    masks = (masks_in @ protos.float().view(c * d, mh * mw)).sigmoid().view(-1, mh, mw)
    gain = min(mh / shape[0], mw / shape[1])
    pad = (mw - shape[1] * gain) / 2, (mh - shape[0] * gain) / 2
    top, left = int(pad[1]), int(pad[0])
    bottom, right = int(mh - pad[1]), int(mw - pad[0])
    masks = masks[:, top:bottom, left:right]
    masks = torch.nn.functional.interpolate(masks[None], shape, mode='bilinear', align_corners=False)[0]
    return masks.gt_(0.5)

masks = process_mask_native(proto[0], pred[0][:, 6:], pred[0][:, :4], img0.shape[:2])
results = []
for i, (det, mask) in enumerate(zip(pred[0], masks)):
    if len(det):
        box = scale_boxes(img.shape[2:], det[:4], img0.shape).round().int()
        x1, y1, x2, y2 = box.tolist()
        conf = det[4].item()
        cls = int(det[5].item())
        mask_np = mask.cpu().numpy()  # Binary mask
        results.append({
            'bbox': [x1, y1, x2, y2],
            'confidence': conf,
            'class': cls,
            'mask': mask_np
        })

for res in results:
    print(f"Class: {res['class']}, Conf: {res['confidence']:.2f}, BBox: {res['bbox']}")


for res in results:
    x1, y1, x2, y2 = res['bbox']
    cv2.rectangle(img0, (x1, y1), (x2, y2), (0, 255, 0), 2)
    mask = res['mask'] * 255
    img0[y1:y2, x1:x2][mask[y1:y2, x1:x2]] = [0, 0, 255]
cv2.imwrite('output.jpg', img0)
        
#results = model('/Users/deu/Downloads/test.jpg')

#results.show()
