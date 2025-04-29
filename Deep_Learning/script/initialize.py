import os
import glob
import shutil
from pathlib import Path
import json
import click
import cv2
from tqdm import tqdm
import pandas as pd

class InitializeData:
    def __init__(self, target):
        self.target = target
        
        self.origin_dir = Path('./rawdata')
        self.data_path = Path('./data')
        
        self.initialize_directory()
        
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
        
    def initialize_directory(self):
        base_path = self.data_path / self.target
        
        ftypes = ['images', 'jsons', 'labels']
        
        self.train_paths = [base_path / 'train' / ftype for ftype in ftypes]
        self.valid_paths = [base_path / 'valid' / ftype for ftype in ftypes]
        self.test_paths = [base_path / 'test' / ftype for ftype in ftypes]
        
        for path in self.train_paths: self.make_directory(path)
        for path in self.valid_paths: self.make_directory(path)
        for path in self.test_paths: self.make_directory(path)
        
        return None
    
    def make_directory(self, path):
        if os.path.exists(path):
            pass
        else:
            os.makedirs(path)
            
        return None
    
    def conv_language(self, fname, option):
        kors = ['남자사람', '여자사람', '집', '나무']
        engs = ['Male', 'Female', 'House', 'Tree']
        
        if option == 'k2e':
            for kor in kors:
                if kor in fname:
                    conv_name = fname.replace(kor, engs[kors.index(kor)])
            if '남' in conv_name:
                conv_name = conv_name.replace('남', 'M')
            elif '여' in conv_name:
                conv_name = conv_name.replace('여', 'F')
        elif option == 'e2k':
            for eng in engs:
                if eng in fname:
                    conv_name = fname.replace(eng, kors[engs.index(eng)])
        
        return conv_name
    
    def copy_files(self, obj):
        print(f"Copy to Initialize : {self.target} ({obj})")
        kor_target = self.conv_language(self.target, 'e2k')
        
        if obj == 'train':
            origin_path = self.origin_dir / 'Training'
            image_list = glob.glob(f'{origin_path}/*/TS_{kor_target}/*.jpg')
            json_list = glob.glob(f'{origin_path}/*/TL_{kor_target}/*.json')
            dst = self.train_paths
        elif obj == 'valid':
            origin_path = self.origin_dir / 'Validation'
            image_list = glob.glob(f'{origin_path}/*/VS_{kor_target}/*.jpg')
            json_list = glob.glob(f'{origin_path}/*/VL_{kor_target}/*.json')
            dst = self.valid_paths
            
        print(f"Copy Image Files")
        for img in tqdm(image_list):
            file_path = Path(img)
            conv_name = self.conv_language(file_path.name, 'k2e')
            dst_path = dst[0] / conv_name
            shutil.copy(file_path, dst_path)
    
        print(f"Copy JSON Files")
        for js in tqdm(json_list):
            file_path = Path(js)
            conv_name = self.conv_language(file_path.name, 'k2e')
            dst_path = dst[1] / conv_name
            shutil.copy(file_path, dst_path)
            
        return None
    
    def make_label(self, obj):
        print(f"Convert the .json files to label(.txt). : {self.target} ({obj})")
        
        if obj == 'train':
            image_dir_path = self.train_paths[0]
            json_dir_path = self.train_paths[1]
            label_dir_path = self.train_paths[2]
        elif obj == 'valid':
            image_dir_path = self.valid_paths[0]
            json_dir_path = self.valid_paths[1]
            label_dir_path = self.valid_paths[2]
            
        for js in tqdm(os.listdir(json_dir_path)):
            fname = js.split('.')[0]
            img_name = fname + '.jpg'
            label_name = fname + '.txt'
            
            json_path = os.path.join(json_dir_path, js)
            image_path = os.path.join(image_dir_path, img_name)
            label_path = os.path.join(label_dir_path, label_name)
        
            with open(json_path, 'r', encoding='UTF-8') as js:
                json_data = json.load(js)
                
                label_list = [data['label'] for data in json_data['annotations']['bbox']]
                x_list = [data['x'] for data in json_data['annotations']['bbox']]
                y_list = [data['y'] for data in json_data['annotations']['bbox']]
                w_list = [data['w'] for data in json_data['annotations']['bbox']]
                h_list = [data['h'] for data in json_data['annotations']['bbox']]
            
            image_data = cv2.imread(image_path)
            
            height, width, _ = image_data.shape
            
            for idx in range(len(label_list)):
                encoding_label = self.class_dict[self.target][0].index(label_list[idx])
                xc = (x_list[idx] + (w_list[idx] / 2)) / width
                yc = (y_list[idx] + (h_list[idx] / 2)) / height
                w_ratio = w_list[idx] / width
                h_ratio = h_list[idx] / height
                label_string = f"{encoding_label} {xc} {yc} {w_ratio} {h_ratio}"
                
                with open(label_path, 'a') as f:
                    if idx != len(label_list) - 1:
                        f.write(f"{label_string}\n")
                    else:
                        f.write(f"{label_string}")
        
        return None
    
    def split_train(self):
        print(f"Split the train dataset to create test dataset. : {self.target}")
        train_image_dir = self.train_paths[0]
        train_json_dir = self.train_paths[1]
        train_label_dir = self.train_paths[2]
        
        test_image_dir = self.test_paths[0]
        test_json_dir = self.test_paths[1]
        test_label_dir = self.test_paths[2]
        
        image_list = sorted(glob.glob(f'{train_image_dir}/*.jpg'))
        json_list = sorted(glob.glob(f'{train_json_dir}/*.json'))
        label_list = sorted(glob.glob(f'{train_label_dir}/*.txt'))
        
        data_dict = {
            'images': [],
            'jsons': [],
            'labels': [],
            'age': [], 'gender': []
        }
        
        for idx in range(len(image_list)):
            img = Path(image_list[idx])
            js = Path(json_list[idx])
            lb = Path(label_list[idx])
            
            img_name = img.stem
            data_dict['images'].append(img)
            
            js_name = js.stem
            data_dict['jsons'].append(js)
            
            lb_name = lb.stem
            data_dict['labels'].append(lb)
            
            if (img_name != js_name) or (js_name != lb_name) or (lb_name != img_name):
                print(f"Image: {img_name}")
                print(f"Json: {js_name}")
                print(f"Label: {lb_name}")
            
            age, gender = img_name.split('_')[1], img_name.split('_')[2]
            
            data_dict['age'].append(age)
            data_dict['gender'].append(gender)
            
        df = pd.DataFrame(data_dict)
        df['composite'] = df['age'].astype(str) + '_' + df['gender'].astype(str)
        
        test_ratio = 0.125

        train_list = []
        test_list = []

        for group_name, group_df in df.groupby('composite'):
            test_sample = group_df.sample(frac=test_ratio, random_state=42)
            train_sample = group_df.drop(test_sample.index)
            
            test_list.append(test_sample)
            train_list.append(train_sample)

        train_df = pd.concat(train_list).reset_index(drop=True)
        test_df = pd.concat(test_list).reset_index(drop=True)

        if len(train_df) > 9800:
            remainder = train_df.iloc[9800:]
            train_df = train_df.iloc[:9800]
            test_df = pd.concat([test_df, remainder], axis=0).reset_index(drop=True)
        elif len(train_df) < 9800:
            remainder = test_df.iloc[1400:]
            train_df = pd.concat([train_df, remainder], axis=0).reset_index(drop=True)
            test_df = test_df.iloc[:1400]
            
        for i in tqdm(range(len(test_df))):
            image_path = test_df['images'].iloc[i]
            json_path = test_df['jsons'].iloc[i]
            label_path = test_df['labels'].iloc[i]
            
            shutil.move(image_path, test_image_dir)
            shutil.move(json_path, test_json_dir)
            shutil.move(label_path, test_label_dir)
        
        return None
    
    def make_yaml(self):
        output = self.data_path / self.target / 'data.yaml'
        class_name = self.class_dict[self.target][1]
    
        with open(output, 'w') as y:
            y.writelines(
                [
                    f'train: {os.path.abspath(self.train_paths[0])}\n',
                    f'val: {os.path.abspath(self.valid_paths[0])}\n',
                    f'test: {os.path.abspath(self.test_paths[0])}\n',
                    '\n',
                    f'nc: {len(class_name)}\n'
                    f'names: {class_name}\n'
                ]
            )
        
        return None

@click.option('-t', '--target', required=True, type=click.Choice(['Male', 'Female', 'House', 'Tree']), help='The target for which you want to Initialize')
@click.command()

def main(target):
    data = InitializeData(target)
    
    data.copy_files('train')
    data.copy_files('valid')
    
    data.make_label('train')
    data.make_label('valid')
    
    data.split_train()
    
    data.make_yaml()
    
if __name__ == '__main__':
    main()