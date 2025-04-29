import os
import json
import click
import torch
import datetime
from pathlib import Path
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

class CustomModel:
    def __init__(self, target):
        self.target = target
        self.json_path = './script/model.json'
        
        self.data = f"./data/{target}/data.yaml"
        self.save_path = f'./model/{target}'
        
        self.class_dict = {
            'Female': [
                ['사람전체', '머리', '얼굴', '눈', '코', '입', '귀', '머리카락', '목', '상체', '팔', '손', '다리', '발', '단추', '주머니', '운동화', '여자구두'],
                ['Female', 'Head', 'Face', 'Eye', 'Nose', 'Mouth', 'Ear', 'Hair', 'Neck', 'Upper_Body', 'Arm', 'Hand', 'Leg', 'Foot', 'Button', 'Pocket', 'Sneakers', 'Shoes']
            ],
            'Male': [
                ['사람전체', '머리', '얼굴', '눈', '코', '입', '귀', '머리카락', '목', '상체', '팔', '손', '다리', '발', '단추', '주머니', '운동화', '남자구두'],
                ['Male', 'Head', 'Face', 'Eye', 'Nose', 'Mouth', 'Ear', 'Hair', 'Neck', 'Upper_Body', 'Arm', 'Hand', 'Leg', 'Foot', 'Button', 'Pocket', 'Sneakers', 'Shoes']
            ],
            'House': [
                ['집전체', '지붕', '집벽', '문', '창문', '굴뚝', '연기', '울타리', '길', '연못', '산', '나무', '꽃', '잔디', '태양'],
                ['House', 'Roof', 'Wall', 'Door', 'Window', 'Chimney', 'Smoke', 'Fence', 'Fence', 'Pond', 'Mountain', 'Tree', 'Flower', 'Grass', 'Sun']
            ],
            'Tree': [
                ['나무전체', '기둥', '수관', '가지', '뿌리', '나뭇잎', '꽃', '열매', '그네', '새', '다람쥐', '구름', '달', '별'],
                ['Tree', 'Pillar', 'Crown', 'Branch', 'Root', 'Leaf', 'Flower', 'Fruit', 'Swing', 'Bird', 'Squirrel', 'Cloud', 'Moon', 'Star']
            ]
        }
    
    def train(self, epochs, image_size, batch_size, base='yolo11n'):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        run_name = f'model/{self.target}/result_epoch{epochs}_imgsz{image_size}'
        
        with open(self.json_path, 'r') as js:
            self.json_data = json.load(js)
            base_model = Path(os.getcwd()) / Path(self.json_data['base'][base])
        self.model = YOLO(base_model)
            
        # self.model.train(
        #     data = self.data,
        #     epochs = epochs,
        #     imgsz = image_size,
        #     batch = batch_size,
        #     workers = 4,
        #     device = 'cuda' if torch.cuda.is_available() else 'cpu',
        #     project = self.save_path,
        #     name = run_name
        # )
        
        self.json_data['trained'][self.target] = f'{run_name}/weights/best.pt'
        
        with open(self.json_path, 'w') as js:
            json.dump(self.json_data, js, indent=4)
        
        return None
    
    def test(self, sample):
        with open(self.json_path, 'r') as js:
            json_data = json.load(js)
        
        if not self.target in json_data['trained']:
            print(f"There is no model trained with {self.target}")
        else:
            model = YOLO(json_data['trained'][self.target])
        
        # 원본 이미지
        label_sample = Path(
            os.path.join(
                os.getcwd(),
                f'./data/{self.target}/test/labels/{sample.stem}.txt'
            )
        )
        
        with open(label_sample, 'r') as lb:
            labels = lb.readlines()
        
        image = cv2.imread(sample)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        h, w, _ = image.shape
        
        origin_bboxes = []
        for label in labels:
            class_id, x_center, y_center, bbox_w, bbox_h = map(float, label.strip().split())
            
            x_min = int((x_center - (bbox_w / 2)) * w)
            y_min = int((y_center - (bbox_h / 2)) * h)
            x_max = int((x_center + (bbox_w / 2)) * w)
            y_max = int((y_center + (bbox_h / 2)) * h)
            
            # x_min = int(((x_center - bbox_w) / 2) * w)
            # y_min = int(((y_center - bbox_h) / 2) * h)
            # x_max = int(bbox_w * h)
            # y_max = int(bbox_h * h)
            
            origin_bboxes.append([x_min, y_min, x_max, y_max, int(class_id)])
        
        
        # 예측 이미지
        detect_boxes = []
        results = model(image)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_name = int(box.cls[0])
                conf = box.conf[0].item()
                
                detect_boxes.append([x1, y1, x2, y2, cls_name])
        
        def draw_bboxes(img, bboxes, color):
            img_copy = img.copy()
            for (x_min, y_min, x_max, y_max, class_id) in bboxes:
                cv2.rectangle(img_copy, (x_min, y_min), (x_max, y_max), color, 2)
                cv2.putText(
                    img_copy,
                    f"{self.class_dict[self.target][1][class_id]}",
                    (x_min, y_min + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 0),
                    2,
                    cv2.LINE_AA
                )
            return img_copy
            
        origin_img = draw_bboxes(image_rgb, origin_bboxes, (0, 0, 255))
        detect_img = draw_bboxes(image_rgb, detect_boxes, (255, 0, 0))
        
        fig, axes = plt.subplots(1, 2, figsize=(16,12))
        
        axes[0].imshow(origin_img)
        axes[0].set_title("Origin")
        axes[0].axis("off")
        
        axes[1].imshow(detect_img)
        axes[1].set_title("Detect")
        axes[1].axis("off")
        
        plt.show()
            
        return None

@click.option('-t', '--target', required=True, type=click.Choice(['Male', 'Female', 'House', 'Tree']), help='The target you want to perform the process on')
@click.option('-m', '--mode', required=True, default='all', type=click.Choice(['all', 'train', 'eval', 'test']), help='The target you want to perform the process on')
@click.option('-b', '--base_model', default='yolo11n', type=click.Choice(['yolo11n', 'yolo11s', 'yolo11m', 'yolo11l', 'yolo11x']), help='Base Model')
@click.command()

def main(target, mode, base_model):
    custom_model = CustomModel(target)
    
    if mode == 'all':
        custom_model.train(
            epochs=30,
            image_size=1280,
            batch_size=-1
        )
        # custom_model.eval()
    elif mode == 'train':
        custom_model.train(
            epochs=30,
            image_size=1280,
            batch_size=-1,
            base=base_model
        )
    elif mode == 'eval':
        # custom_model.eval()
        pass
    elif mode == 'test':
        image_sample = Path(
            os.path.join(
                os.getcwd(),
                f'./data/{custom_model.target}/test/images/',
                os.listdir(f'./data/{custom_model.target}/test/images/')[-1]
            )
        )
        
        custom_model.test(image_sample)

if __name__ == '__main__':
    main()