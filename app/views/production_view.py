def run_production_menu(production_line_controller) -> None:
    while True:
        print("1. 현재 생산 현황")
        print("2. 생산 대기열 조회")
        print("3. 생산 완료 처리")
        print("4. 이전 메뉴로")
        choice = input("선택: ")

        if choice == "1":
            result = production_line_controller.current_production()
            if result is None:
                print("현재 생산 중인 시료가 없습니다.")
            else:
                print(
                    f"{result['order'].id} | 부족분 {result['shortfall']} | "
                    f"실생산량 {result['actual_production']} | "
                    f"총생산시간 {result['total_production_time']}"
                )
        elif choice == "2":
            orders = production_line_controller.waiting_orders()
            if not orders:
                print("대기 중인 생산이 없습니다.")
            else:
                for o in orders:
                    print(f"{o.id} | {o.sample_id} | {o.quantity}")
        elif choice == "3":
            order = production_line_controller.complete_current_production()
            if order is None:
                print("완료할 생산이 없습니다.")
            else:
                print(f"생산 완료 처리: {order.id} ({order.status})")
        elif choice == "4":
            return
        else:
            print("잘못된 입력입니다.")
