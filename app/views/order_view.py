from datetime import date


def _today():
    return date.today()


def run_order_menu(order_controller) -> None:
    while True:
        print("1. 시료 주문 접수")
        print("2. 이전 메뉴로")
        choice = input("선택: ")

        if choice == "1":
            sample_id = input("시료 ID: ")
            customer_name = input("고객명: ")
            quantity = input("주문 수량: ")
            order = order_controller.place_order(
                sample_id, customer_name, int(quantity), _today()
            )
            print(f"주문 접수 완료: {order.id} ({order.status})")
        elif choice == "2":
            return
        else:
            print("잘못된 입력입니다.")
