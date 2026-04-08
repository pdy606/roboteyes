import os
import shutil
from ultralytics import YOLO

def train_model(data_dir: str, model_dir: str) -> str:
    """
    모인 데이터(data_dir)를 읽어와 YOLOv8 분류 모델을 학습하고,
    결과 가중치를 model_dir 에 저장합니다.
    """
    print("🚀 [학습 로직 시작] 사장님이 준비하신 사진들로 YOLOv8 학습을 시작합니다 (CPU 전용)...")
    
    # 1. 초기 모델 로드 (Pre-trained YOLOv8 Nano Classification)
    model = YOLO("yolov8n-cls.pt")
    
    # 2. 학습 실행
    # data: 클래스별 폴더가 들어있는 최상위 경로 (data/uploads)
    # epochs: 짧게(5회) 설정하여 빠른 피드백 제공
    # imgsz: 이미지 크기 224
    # device: CPU 강제 사용
    print(f"📁 [데이터 경로 확인] {os.path.abspath(data_dir)}")
    
    results = model.train(
        data=data_dir, 
        epochs=5, 
        imgsz=224, 
        device='cpu', 
        project='runs', 
        name='classify_train', 
        exist_ok=True,
        verbose=True
    )
    
    # 3. 학습 결과 파일(best.pt) 확인 및 복사
    best_pt_path = os.path.join("runs", "classify_train", "weights", "best.pt")
    
    if os.path.exists(best_pt_path):
        target_path = os.path.join(model_dir, "best.pt")
        os.makedirs(model_dir, exist_ok=True)
        shutil.copy(best_pt_path, target_path)
        print(f"✨ [학습 완료] YOLOv8이 메뉴 인식을 마스터했습니다!")
        print(f"💾 [모델 업데이트 완료] 최신 가중치가 {target_path} 에 저장되었습니다.")
        return target_path
    
    print("❌ [오류] 학습 결과 파일(best.pt)을 찾을 수 없습니다. 학습이 정상적으로 완료되지 않았을 가능성이 있습니다.")
    return None
