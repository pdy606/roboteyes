from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Form, HTTPException, Body
from fastapi.responses import RedirectResponse, HTMLResponse
import shutil
import os
from enum import Enum
from pydantic import BaseModel
from typing import List
from .model import ModelManager, MENU_LIST
from .train import train_model
from .order import OrderManager

app = FastAPI(
    title="서빙 로봇 똑똑한 뇌 🧠", 
    description="메뉴 인식 MLOps와 주문별 자동 배차(Dispatch) 시스템이 결합된 종합 로봇 API",
    version="2.0.0"
)

class MenuEnum(str, Enum):
    JEYUK = "제육볶음"
    DONKAS = "돈까스"
    KIMCHI = "김치찌개"
    DOENJANG = "된장찌개"

class OrderItemRequest(BaseModel):
    menu_name: MenuEnum
    quantity: int

class CreateOrderRequest(BaseModel):
    table_number: int
    orders: List[OrderItemRequest]

@app.get("/", include_in_schema=False)
async def redirect_to_pos():
    return RedirectResponse(url="/pos")

DATA_DIR = "data/uploads"
MODEL_DIR = "models"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

model_manager = ModelManager(model_dir=MODEL_DIR)
order_manager = OrderManager()

# ==================== [ 사장님 시각적 포스기 UI ] ====================

@app.get("/pos", summary="프리미엄 포스기 화면", tags=["UI 디자인"])
async def get_pos_ui():
    """아주 예쁜 Glassmorphism 디자인의 웹 포스기를 불러옵니다."""
    file_path = os.path.join(os.path.dirname(__file__), "pos.html")
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# ==================== [ 주문 및 로봇 배차 시스템 ] ====================

@app.post("/order", summary="가게 포스기/테이블에서 단체 주문 넣기", tags=["1. 매장 주문 시스템"])
async def create_order(request: CreateOrderRequest):
    """
    여러 가지 메뉴를 장바구니에 담아서 한 번에 결제하듯 테이블 번호와 함께 전송합니다.
    """
    if request.table_number < 1 or request.table_number > 6:
        raise HTTPException(status_code=400, detail="사장님, 우리가게 테이블은 1번부터 6번까지만 있습니다!")
    
    total_added = 0
    # 장바구니에 담긴 메뉴별로 순회하며 내부 큐에 추가
    # 순차적으로 들어가므로 AI가 완벽하게 들어온 순서대로 배정합니다.
    for item in request.orders:
        if item.quantity < 1:
            continue
        order_manager.add_order(request.table_number, item.menu_name.value, item.quantity)
        total_added += item.quantity
        
    if total_added == 0:
         raise HTTPException(status_code=400, detail="주문할 메뉴를 그릇 이상 담아주세요!")
         
    return {"message": f"{request.table_number}번 테이블에 총 {total_added}그릇 주문이 (시간 순서대로) 접수되었습니다!"}

@app.get("/orders", summary="주방 대기열(밀린 주문) 확인", tags=["1. 매장 주문 시스템"])
async def view_orders():
    pending = order_manager.get_pending_orders()
    return {"pending_orders": pending}

@app.post("/serve", summary="🤖 (로봇용) 음식 인식 및 목적지 배차 지시", tags=["2. 로봇 두뇌 (자율 판단)"])
async def serve_food(file: UploadFile = File(..., description="로봇이 배달 칸에 놓인 음식을 찍은 사진")):
    predicted_menu = model_manager.predict(file.filename)
    
    target_order = order_manager.pop_oldest_order_by_menu(predicted_menu)
    
    if target_order is None:
        return {
            "ai_vision_result": predicted_menu,
            "robot_command": "STOP",
            "message": f"삐빅! 이 음식({predicted_menu})은 아무도 시키지 않았거나, 이미 완료되었습니다!"
        }
    
    return {
        "ai_vision_result": predicted_menu,
        "robot_command": f"Drive_to_Table_{target_order.table_number}",
        "message": f"🤖 [{predicted_menu}] 발견! 제일 먼저 시켰던 {target_order.table_number}번 테이블로 출발합니다!!"
    }

# ==================== [ MLOps 모듈 ] ====================

@app.post("/upload", summary="새 메뉴 사진 데이터 업로드", tags=["3. MLOps"])
async def upload_menu_image(menu_name: str = Form(...), file: UploadFile = File(...)):
    menu_dir = os.path.join(DATA_DIR, menu_name)
    os.makedirs(menu_dir, exist_ok=True)
    file_path = os.path.join(menu_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"[{menu_name}] AI 학습용 데이터가 업로드 됨.", "file_path": file_path}

def run_training_and_reload():
    new_model_path = train_model(DATA_DIR, MODEL_DIR)
    if new_model_path:
        model_manager.load_model(new_model_path)

@app.post("/train", summary="로봇 추가 재학습", tags=["3. MLOps"])
async def start_training(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_training_and_reload)
    return {"message": "로봇 백그라운드 재학습 진행. (무중단)"}
