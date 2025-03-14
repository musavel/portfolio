# 서울 지하철 공실 해결을 위한 또타 스토리지 활용 분석

## 프로젝트 소개
본 프로젝트는 서울 지하철 내 상가 공실 문제를 해결하기 위해 '또타 스토리지'라는 셀프 스토리지 서비스의 효율적인 활용 방안을 분석했습니다. 특히 서울 내 1인 가구가 증가하고 있는 점을 고려하여 공실 지역을 대상으로 신설하거나 증설 가능한 지점을 제안하고자 합니다.

## 주요 목적
- 서울 지하철 상가의 공실 현황을 시각적으로 파악하고 문제점을 진단
- 현재 운영 중인 또타 스토리지의 위치를 분석하여 활용도 평가
- 서울시의 1인 가구 증가 현황 및 지역적 분포 분석
- 공실 데이터와 1인 가구 데이터를 위경도와 결합하여 효과적인 설치 및 증설 전략 수립

## 사용한 데이터
- 서울 지하철 상가 공실 데이터
- 서울시 또타 스토리지 설치 현황 데이터
- 서울시 1인 가구 인구 통계 데이터
- 지하철역 및 행정구역별 위경도 데이터

## 데이터 전처리 과정
- 결측치와 이상치를 확인하여 분석에 적합한 형태로 데이터를 정제
- 공실 및 인구 데이터와 지하철역 및 행정구역의 위경도 데이터를 병합하여 공간 분석 준비

## 분석 방법
1. **지하철 공실 현황 시각화**
   - Bar 및 Line 차트를 통해 서울 지하철 공실의 규모 및 변화 추이를 시각화
   - Folium 지도를 사용해 공실이 집중된 역과 지역을 지도 위에 표현

2. **또타 스토리지 설치 현황 분석**
   - Folium 지도를 이용해 서울 내 또타 스토리지의 위치를 시각적으로 표현

3. **1인 가구 현황 분석**
   - 서울시의 1인 가구 수와 증가 추이를 Bar 및 Line 차트로 표현
   - Folium 지도로 지역별 1인 가구 비율을 시각화하여 수요가 높은 지역 확인

4. **공실 데이터와 인구 데이터의 결합 분석**
   - 공실을 보유한 역과 1인 가구가 많은 지역을 결합하여, 또타 스토리지를 신규 설치하거나 기존 시설을 확장할 최적의 위치를 제안

## 분석 결과 및 제안
- 1인 가구 비율이 높은 지역에서 공실을 보유한 지하철 역을 중심으로
  - 또타 스토리지 미설치 역: 신규 설치를 제안
  - 또타 스토리지가 이미 설치된 역: 추가 증설을 제안

## 사용 기술
- Python (Pandas, Matplotlib, Folium)

## 주요 시각화 결과
- 지하철 공실 현황 차트 (Bar, Line)
- 또타 스토리지 위치 지도 (Folium)
- 서울시 1인 가구 분포 지도 시각화 (Folium)

## 참고자료
- 서울 열린데이터 광장
- Folium 공식 문서 (https://python-visualization.github.io/folium/)

