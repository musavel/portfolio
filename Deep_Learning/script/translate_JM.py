# 한영 번역 클래스 
class KorEngTranslator:
    def __init__(self):
        self.kor2eng_dict = {
            'Female': {
                'Female': '사람전체', 'Head': '머리', 'Face': '얼굴', 'Eye': '눈',
                'Nose': '코', 'Mouth': '입', 'Ear': '귀', 'Hair': '머리카락',
                'Neck': '목', 'Upper_Body': '상체', 'Arm': '팔', 'Hand': '손',
                'Leg': '다리', 'Foot': '발', 'Button': '단추', 'Pocket': '주머니',
                'Sneakers': '운동화', 'Shoes': '여자구두'
            },
            'Male': {
                'Male': '사람전체', 'Head': '머리', 'Face': '얼굴', 'Eye': '눈',
                'Nose': '코', 'Mouth': '입', 'Ear': '귀', 'Hair': '머리카락',
                'Neck': '목', 'Upper_Body': '상체', 'Arm': '팔', 'Hand': '손',
                'Leg': '다리', 'Foot': '발', 'Button': '단추', 'Pocket': '주머니',
                'Sneakers': '운동화', 'Shoes': '남자구두'
            },
            'House': {
                'House': '집전체', 'Roof': '지붕', 'Wall': '집벽', 'Door': '문',
                'Window': '창문', 'Chimney': '굴뚝', 'Smoke': '연기', 'Fence': '울타리',
                'Path': '길', 'Pond': '연못', 'Mountain': '산', 'Tree': '나무',
                'Flower': '꽃', 'Grass': '잔디', 'Sun': '태양'
            },
            'Tree': {
                'Tree': '나무전체', 'Pillar': '기둥', 'Crown': '수관', 'Branch': '가지',
                'Root': '뿌리', 'Leaf': '나뭇잎', 'Flower': '꽃', 'Fruit': '열매',
                'Swing': '그네', 'Bird': '새', 'Squirrel': '다람쥐', 'Cloud': '구름',
                'Moon': '달', 'Star': '별'
            },
            'Emotion': {
                'Aggression': '공격성', 'Social Anxiety': '사회 불안', 'Depression': '우울',
                'Interpersonal Avoidance': '대인회피', 'Self Esteem': '자존감 문제',
                'Emotional Instability': '정서불안', 'Affection Deficit': '애정결핍',
                'Inferiority': '열등감', 'Regression': '퇴행'
            },
            'Description': {
                'small':'지나치게 작다', 'big':'지나치게 크다', 
                'left':'좌측에 치우쳐져 있다', 'right':'우측에 치우쳐져 있다', 'bottom':'하단에 치우쳐져 있다',
                'many':'많다.', 'few':'적다',
            },
            'Category': {
                'size': '크기',
                'place':'위치',
                'exist':'존재 여부',
                'count':'개수'
            }
        }

    def eng_to_kor(self, category: str, kor_word: str) -> str:
        """영어 → 한글 변환"""
        return self.kor2eng_dict.get(category, {}).get(kor_word, kor_word)

    def kor_to_eng(self, category: str, eng_word: str) -> str:
        """한글 → 영어 변환"""
        eng_to_kor = {v: k for k, v in self.kor2eng_dict.get(category, {}).items()}
        return eng_to_kor.get(eng_word, eng_word)

# 감정 요소 추출 함수
def extract_emotions(data):
    # 감정 요소 레이블
    emotion_labels = [
        "Aggression", "Social Anxiety", "Depression", "Avoidance",
        "Self Esteem", "Emotional Instability", "Affection Deficit",
        "Inferiority", "Regression"
    ]
    return [[emotion_labels[i] for i, score in enumerate(value) if score == 1] for value in data]

# 문장 생성 함수 
def make_sentence (output) :
    result_list = []
    translator = KorEngTranslator()
    for class_name in output.keys():
        result_str = "" 
        for attribute in output[class_name]:
            # text_values = output[class_name][attribute]['text']
            text_values = output.get(class_name, {}).get(attribute, {}).get('text', [])
            # score_values = output[class_name][attribute]['score']
            score_values = output.get(class_name, {}).get(attribute, {}).get('score', [])
            str1 = translator.eng_to_kor(class_name,class_name)
            str2 = translator.eng_to_kor('Category',attribute)

            score_emotions = extract_emotions(score_values)

            for text in text_values:
                str3 = translator.eng_to_kor('Description',text)
                result_str += f"그림에서 {str1} 의 {str2}가 {str3}. 이는 "
            
            for item in score_emotions:
                for i,emotion in enumerate(item):
                    if i == 0 :
                        result_str += f"{translator.eng_to_kor('Emotion',emotion)}"
                    else:
                        result_str += f", {translator.eng_to_kor('Emotion',emotion)}"
                    # if i < len(score_emotions) : 
                    #     result_str += ", "
            
            result_str += "을 표현한 것으로 볼 수 있다."
            result_list.append(result_str)
    return result_list