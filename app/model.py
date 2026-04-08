import time
import os
import random

# 우리 가게 기본 4종 메뉴 설정
MENU_LIST = ["제육볶음", "돈까스", "김치찌개", "된장찌개"]

class ModelManager:
    """
    무중단 배포를 위한 전역 모델 매니저 객체
    """
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        self.current_model = None
        self.model_version = "기본 모델 (학습 전)"
        self.load_latest_model()

    def load_latest_model(self):
        if os.path.exists(self.model_dir):
            models = sorted([f for f in os.listdir(self.model_dir) if f.endswith(".pt")], reverse=True)
            if models:
                self.load_model(os.path.join(self.model_dir, models[0]))
            else:
                print("⚠️ [안내] 저장된 모델이 없습니다. 기초 모델로 대기합니다.")
                
    def load_model(self, model_path: str):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ⚙️ 모델 교체 작업 시작... 👉 {model_path}")
        time.sleep(1) 
        self.current_model = "Loaded Neural Network Data" 
        self.model_version = os.path.basename(model_path)
        print(f"✅ [성공] 새 모델 '{self.model_version}' 이 메모리에 올라갔습니다. (서버 재시작 필요 없음!)")

    def predict(self, filename: str) -> str:
        """
        가상의 이미지 인식 AI 로직
        사장님 테스트 편의성을 위해 아무 사진이나 올려도 기본 4종 메뉴 중 하나를 무작위로 판별합니다.
        """
        # 실제라면 self.current_model(image) 처럼 딥러닝 망을 거치게 됩니다.
        random.seed(len(filename) + time.time()) # 예측때마다 조금씩 바뀌게 랜덤 부여
        predicted_menu = random.choice(MENU_LIST)
        return predicted_menu
