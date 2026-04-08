import os
import time
from ultralytics import YOLO

# 우리 가게 기본 5종 메뉴 설정 (YOLO 모델의 클래스와 일치해야 함)
MENU_LIST = ["제육볶음", "돈까스", "김치찌개", "된장찌개", "짜장면"]

class ModelManager:
    """
    YOLOv8 분류 모델을 관리하는 매니저.
    새로운 모델이 학습 완료되면 재시작 없이 바꿔치기(Hot-swap)합니다.
    """
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        self.model = None
        self.model_version = "기본 YOLO 모델 (학습 전)"
        self.load_latest_model()

    def load_latest_model(self):
        """가장 최신 가중치 파일(best.pt)을 찾아 로드합니다."""
        best_model_path = os.path.join(self.model_dir, "best.pt")
        
        if os.path.exists(best_model_path):
            self.load_model(best_model_path)
        else:
            # 초기 모델이 없을 경우 YOLO 기본 분류 모델 로드
            print("⚠️ [안내] 학습된 가중치가 없습니다. 기본 YOLOv8 모델을 준비합니다.")
            self.model = YOLO("yolov8n-cls.pt")
                
    def load_model(self, model_path: str):
        """새로운 모델 파일을 메모리에 올립니다."""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ⚙️ 모델 교체 작업 시작... 👉 {model_path}")
        
        # YOLO 모델 로드 (CPU 강제)
        self.model = YOLO(model_path)
        self.model_version = os.path.basename(model_path)
        
        print(f"✅ [성공] 새 모델 '{self.model_version}' 이 로드되었습니다. (CPU 사용)")

    def predict(self, image_path_or_file) -> str:
        """실제 YOLOv8 추론을 수행합니다 (CPU 전용)."""
        if self.model is None:
            return "모델 로딩 중..."
        
        # YOLOv8 추론 (이미지 한 장)
        # device='cpu'를 사용하여 서버 환경에서 안정적으로 동작하게 합니다.
        results = self.model.predict(source=image_path_or_file, device='cpu', verbose=False)
        
        # 분류 결과 가져오기 (가장 높은 확률의 클래스)
        top1_index = results[0].probs.top1
        predicted_name = results[0].names[top1_index]
        
        print(f"🤖 [인식 결과] {predicted_name} (확률: {results[0].probs.top1conf:.2f})")
        return predicted_name
