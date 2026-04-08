from pydantic import BaseModel
from typing import List, Optional
import time

class OrderItem(BaseModel):
    order_id: int
    table_number: int  # 1번부터 6번까지
    menu_name: str
    status: str = "pending"  # 대기중: "pending", 서빙완료: "served"
    timestamp: float

class OrderManager:
    """메모리 상에서 주문 큐(Queue)를 관리하는 매니저. 서버가 꺼지면 초기화됩니다."""
    def __init__(self):
        self.orders: List[OrderItem] = []
        self.order_counter = 1
        
    def add_order(self, table_number: int, menu_name: str, quantity: int = 1) -> List[OrderItem]:
        if table_number < 1 or table_number > 6:
            raise ValueError("테이블 번호는 1번부터 6번까지만 가능합니다.")
        if quantity < 1:
            raise ValueError("수량은 1 이상이어야 합니다.")
            
        new_items = []
        base_timestamp = time.time()
        
        for i in range(quantity):
            new_order = OrderItem(
                order_id=self.order_counter,
                table_number=table_number,
                menu_name=menu_name,
                # 만약 수량이 여러개일 경우 순차적으로 먼저 배달가기 위해 미세하게 시간차를 둠
                timestamp=base_timestamp + (i * 0.001) 
            )
            self.orders.append(new_order)
            self.order_counter += 1
            new_items.append(new_order)
            
        return new_items
        
    def get_pending_orders(self) -> List[OrderItem]:
        """주문이 아직 안 나간 예약(대기) 상태의 주문만 조회"""
        return [order for order in self.orders if order.status == "pending"]

    def pop_oldest_order_by_menu(self, menu_name: str) -> Optional[OrderItem]:
        """
        AI가 메뉴를 인식했을 때 호출됩니다.
        대기열에서 해당 메뉴를 가장 먼저 시킨 테이블의 주문을 찾아 서빙 완료 처리 후 반환합니다.
        """
        pending_orders = self.get_pending_orders()
        # 들어온 시간(timestamp) 기준 오름차순(가장 오래된 주문 먼저)으로 정렬
        pending_orders.sort(key=lambda x: x.timestamp)
        
        for order in pending_orders:
            if order.menu_name == menu_name:
                # 서빙 시작 상태로 전환 (이제 밀린 주문 목록에서 사라집니다)
                order.status = "served"
                return order
                
        # 아무도 이 메뉴를 시키지 않았거나, 이미 다 배달 나간 경우
        return None
