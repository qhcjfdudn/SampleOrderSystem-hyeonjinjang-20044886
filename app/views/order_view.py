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


def run_order_approval_menu(order_controller) -> None:
    while True:
        print("1. 접수된 주문 목록 조회")
        print("2. 주문 승인")
        print("3. 주문 거절")
        print("4. 이전 메뉴로")
        choice = input("선택: ")

        if choice == "1":
            orders = order_controller.list_reserved_orders()
            if not orders:
                print("접수된 주문이 없습니다.")
            else:
                for o in orders:
                    print(f"{o.id} | {o.sample_id} | {o.customer_name} | {o.quantity}")
        elif choice == "2":
            order_id = input("주문번호: ")
            order = order_controller.approve_order(order_id)
            print(f"승인 처리 완료: {order.id} ({order.status})")
        elif choice == "3":
            order_id = input("주문번호: ")
            order = order_controller.reject_order(order_id)
            print(f"거절 처리 완료: {order.id} ({order.status})")
        elif choice == "4":
            return
        else:
            print("잘못된 입력입니다.")


def run_release_menu(order_controller) -> None:
    while True:
        print("1. CONFIRMED 주문 목록 조회")
        print("2. 출고 처리")
        print("3. 이전 메뉴로")
        choice = input("선택: ")

        if choice == "1":
            orders = order_controller.list_confirmed_orders()
            if not orders:
                print("출고 대기 중인 주문이 없습니다.")
            else:
                for o in orders:
                    print(f"{o.id} | {o.sample_id} | {o.customer_name} | {o.quantity}")
        elif choice == "2":
            order_id = input("주문번호: ")
            order = order_controller.release_order(order_id)
            print(f"출고 처리 완료: {order.id} ({order.status})")
        elif choice == "3":
            return
        else:
            print("잘못된 입력입니다.")
