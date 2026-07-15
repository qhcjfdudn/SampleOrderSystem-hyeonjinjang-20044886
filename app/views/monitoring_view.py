def run_monitoring_menu(monitoring_controller) -> None:
    while True:
        print("1. 상태별 주문 현황")
        print("2. 시료별 재고 현황")
        print("3. 이전 메뉴로")
        choice = input("선택: ")

        if choice == "1":
            counts = monitoring_controller.order_status_counts()
            for status, count in counts.items():
                print(f"{status}: {count}건")
        elif choice == "2":
            entries = monitoring_controller.sample_stock_status()
            if not entries:
                print("등록된 시료가 없습니다.")
            else:
                for entry in entries:
                    sample = entry["sample"]
                    print(
                        f"{sample.id} | {sample.name} | 재고 {sample.stock} | "
                        f"수요 {entry['demand']} | {entry['status']}"
                    )
        elif choice == "3":
            return
        else:
            print("잘못된 입력입니다.")
