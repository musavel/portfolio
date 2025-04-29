import os
import streamlit as st
import torch
import numpy as np
import cv2
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
from matplotlib import font_manager as fm
from yolo import CustomModel
from evaluate_JS import Base_evaluate
from translate_JM import make_sentence

torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]        

def get_korean_font():
    font_candidates = ["NanumGothic", "Malgun Gothic", "AppleGothic", "Droid Sans Fallback"]
    for font_name in font_candidates:
        font_path = fm.findSystemFonts(fontpaths=None, fontext='ttf')
        for path in font_path:
            if font_name in path:
                return path
    return None

font_path = get_korean_font()
font = ImageFont.truetype(font_path, 40)

st.set_page_config(
    # page_title="DeePrint : AI HTP 검사 지원 서비스",
    page_icon="🔍",
    layout="wide"
)

def get_custom_yolo(image_type):
    htp_dict = {
        '집': 'House',
        '나무': 'Tree',
        '남자사람': 'Male',
        '여자사람': 'Female'
    }

    htp = htp_dict[image_type]
    
    yolo = CustomModel(htp)    
    label_names = yolo.class_dict[htp]
    
    # if (yolo.target == 'Male') or (yolo.target == 'Female'):
    #     question_json = f'./script/question_person.json'
    # else:
    #     question_json = f'./script/question_{yolo.target}.json'

    # with open(question_json, encoding='utf-8') as js:
    #     questions = json.load(js)
    
    with open(yolo.json_path, 'r') as js:
        json_data = json.load(js)
    
    if not yolo.target in json_data['trained']:
        print(f"There is no model trained with {yolo.target}")
    else:
        model = YOLO(json_data['trained'][yolo.target])
        
    # return label_names, questions, model
    return label_names, model
    
def detect_objects(model, image):
    results = model(image)  # 객체 탐지 수행
    return results

def main():
    ss = st.session_state
    
    if "image_type" not in ss:
        ss.image_type = '선택'
    if "uploaded_image" not in ss:
        ss.uploaded_image = None
    if "view_option" not in ss:
        ss.view_option = '모두 보기'
    if "selected_labels" not in ss:
        ss.selected_labels = None
    if "view_mode" not in ss:
        ss.view_mode = False
    if "output_image" not in ss:
        ss.output_image = None
    if "eval_mode" not in ss:
        ss.eval_mode = False
    if "final_mode" not in ss:
        ss.final_mode = False
    
    st.title("DeePrint : AI HTP 검사 지원 서비스")
    
    # 이미지 유형 선택
    image_types = ['선택', '집', '나무', '남자사람', '여자사람']

    image_type_option = st.selectbox(
        label="업로드 할 그림의 종류를 선택하세요."
        , options=image_types
    )
    
    if ss.image_type != image_type_option:
        ss.uploaded_image = None
        ss.view_option = '모두 보기'
        ss.view_mode = False
        ss.output_image = None
        ss.eval_mode = False
        ss.selected_labels = None
        ss.final_mode = False
        ss.image_type = image_type_option
    
    if ss.image_type == '선택':
        st.warning("먼저 업로드할 그림의 종류를 선택하세요.")
    else:
        st.success(f"{ss.image_type} 이미지를 업로드할 수 있습니다!")
        # label_names, questions, model = get_custom_yolo(ss.image_type)
        label_names,model = get_custom_yolo(ss.image_type)
        kor_labels = label_names[0]
        eng_labels = label_names[1]
        
        image_uploader = st.file_uploader(
            label=f"{ss.image_type} 그림 업로드 (.jpg /.jpeg / .png)"
            , type=["jpg", "png", "jpeg"]
        )
        
        if ss.uploaded_image != image_uploader:
            ss.view_option = '모두 보기'
            ss.view_mode = False
            ss.output_image = None
            ss.eval_mode = False
            ss.selected_labels = None
            ss.final_mode = False
            ss.uploaded_image = image_uploader
        
        if not ss.uploaded_image:
            st.warning("이미지를 업로드 하세요.")
        else:
            st.success("이미지가 업로드 되었습니다!")
            image = Image.open(ss.uploaded_image)
            image_np = np.array(image)
            results = model(image_np)
            
            view_options = ['모두 보기', '선택 보기']
            ss.view_option = st.selectbox(
                label=f"{ss.image_type} 그림에 표시할 항목를 선택하세요."
                , options=view_options
                , index=view_options.index(ss.view_option)
            )
                
            if ss.view_option == '모두 보기':
                selected_labels = kor_labels
                st.write("✅ 모든 항목이 선택되었습니다.")
            else:
                selected_labels = st.multiselect(
                    "표시할 항목을 선택하세요.",
                    kor_labels
                )
                st.write(f"✅ 선택된 항목: [{', '.join(selected_labels)}]")
            
            if ss.selected_labels != selected_labels:
                ss.eval_mode = False
                ss.view_mode = False
                ss.final_mode = False
                ss.selected_labels = selected_labels
            
            detect_button = st.button("탐지 결과 및 AI 분석 결과 확인하기", type='primary', use_container_width=True)
            if detect_button:
                ss.view_mode = True
                ss.eval_mode = False
                ss.final_mode = False
            
            if ss.view_mode:
                detected_classes = []
                analysis_labels = {eng_labels[kor_labels.index(label)]:[] for label in selected_labels}
                final_labels = {eng_labels[kor_labels.index(label)]:[] for label in kor_labels}
            
                for result in results:
                    for box in result.boxes:
                        cls_id = int(box.cls[0].item())
                        kor_label = kor_labels[cls_id]
                        eng_label = eng_labels[kor_labels.index(kor_label)]
                        
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        x1_norm = round(x1 / image_np.shape[1], 2)
                        y1_norm = round(y1 / image_np.shape[0], 2)
                        x2_norm = round(x2 / image_np.shape[1], 2)
                        y2_norm = round(y2 / image_np.shape[0], 2)
                        xy_norm = round((x2 * y2) / (image_np.shape[1] * image_np.shape[0]), 2)
                        
                        final_labels[eng_label].append([x1_norm, y1_norm, x2_norm, y2_norm, xy_norm])
                        
                        if kor_label in selected_labels:
                            analysis_labels[eng_label].append([x1_norm, y1_norm, x2_norm, y2_norm, xy_norm])
                            detected_classes.append([x1, y1, x2, y2, kor_label])
                
                # print(analysis_labels)
                output_image = Image.fromarray(image_np)
                draw = ImageDraw.Draw(output_image)
            
                for x1, y1, x2, y2, label in detected_classes:
                    draw.rectangle([(x1, y1), (x2, y2)], outline="blue", width=3)
                    if font_path:
                        draw.text((x1, y1 - 40), label, font=font, fill="black")
                
                ss.output_image = output_image
            
                if ss.output_image:
                    left, right = st.columns([2,1])
                    
                    with left:
                        st.image(ss.output_image, caption="탐지 결과")
                        
                    with right:
                        eval = Base_evaluate(result=analysis_labels)
                        
                        if not ss.selected_labels:
                            st.warning("평가할 항목을 선택해주세요.")
                        else:
                            text = ""
                            for label in selected_labels:
                                eng_label = eng_labels[kor_labels.index(label)]
                                sub_dict = {eng_label:eval.private_dict[eng_label]}
                                # print(sub_dict)
                                sentences = make_sentence(sub_dict)
                                # print(sentences)
                                
                                text += f"✔ {label}에 대한 평가\n- "
                                if sentences:
                                    text += '\n- '.join(sentences)
                                    text += '\n'
                                else:
                                    # if analysis_labels[eng_label]:
                                    text += '현재 버전에서는 이 항목에 대한 평가 정보가 없습니다.\n'
                                    # else:
                                    #     text += f'{label}이 탐지되지 않았습니다..\n'
                                text += "\n"
                            
                            st.text_area(
                                "💡 AI 간편 요약",
                                text,
                                height=975,
                            )
                            final = st.button("전체 요약 보기", type='primary', use_container_width=True)
                            if final:
                                ss.final_mode = True
                    if ss.final_mode:
                        final = Base_evaluate(result=final_labels)
                        # print(final.private_dict)
                        
                        api_url = "http://192.168.20.126:8000/process"
                        data = {"output":final.private_dict}
                        response = requests.post(api_url,json=data)

                        if response.status_code == 200:
                            response_text = response.text
                            
                            response_dict = json.loads(response_text)
                            actual_text = response_dict["response_text"]
                            
                            st.subheader("💡 AI 전체 요약 결과")
                            st.markdown(actual_text)

if __name__ == '__main__':
    main()