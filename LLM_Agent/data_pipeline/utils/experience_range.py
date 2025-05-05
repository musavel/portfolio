import re

def parse_experience_range(raw_exp: str):
    # 신입 케이스 처리
    if '신입' in raw_exp:
        # 숫자 추출
        numbers = re.findall(r'\d+', raw_exp)
        if not numbers:
            if '이상' in raw_exp:
                return 0, 50  # 신입 이상인 경우
            return 0, 0  # 신입만 있는 경우
        return 0, max(int(n) for n in numbers)
    
    # 숫자 추출
    numbers = re.findall(r'\d+', raw_exp)
    if not numbers:
        return 0, 50  # 숫자가 없는 경우 기본값
    
    numbers = [int(n) for n in numbers]
    
    # "N년 이상" 패턴 처리
    if '이상' in raw_exp:
        return min(numbers), 50
    
    # "N-M년" 패턴 처리
    if len(numbers) >= 2:
        return min(numbers), max(numbers)
    
    # 그 외의 경우
    return min(numbers), 50
    