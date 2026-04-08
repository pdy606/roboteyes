# 1. 초경량 파이썬 베이스 이미지 사용
FROM python:3.10-slim

# 2. 파이썬 환경 변수 설정 (바이트코드(.pyc) 생성 방지, 버퍼링 방지)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 의존성 설치 및 시스템 라이브러리 추가 (OpenCV/Ultralytics 필수 요소)
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드 및 학습 데이터 복사
COPY ./app ./app
COPY ./data ./data

# 필요한 각종 폴더 생성
RUN mkdir -p data/uploads models runs

# 6. Deployment 과정에서 자동 AI 학습 진행 (모델 가중치 best.pt 구워넣기)
RUN python app/train.py

# 7. 보안을 위해 일반 유저(robot_user) 생성 및 권한 부여
RUN addgroup --system robotgroup && \
    adduser --system --group robot_user && \
    chown -R robot_user:robotgroup /app

USER robot_user

# 8. 포트 개방
EXPOSE 8000

# 9. 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
