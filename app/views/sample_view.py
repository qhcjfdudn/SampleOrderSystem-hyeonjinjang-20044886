def run_sample_menu(sample_controller) -> None:
    while True:
        print("1. 시료 등록")
        print("2. 시료 조회")
        print("3. 시료 검색")
        print("4. 이전 메뉴로")
        choice = input("선택: ")

        if choice == "1":
            id = input("시료 ID: ")
            name = input("이름: ")
            avg_production_time = input("평균 생산시간: ")
            yield_rate = input("수율: ")
            sample = sample_controller.register(
                id, name, int(avg_production_time), float(yield_rate)
            )
            print(f"등록되었습니다: {sample.id} | {sample.name}")
        elif choice == "2":
            samples = sample_controller.list_samples()
            if not samples:
                print("등록된 시료가 없습니다.")
            else:
                for s in samples:
                    print(f"{s.id} | {s.name} | 재고 {s.stock}")
        elif choice == "3":
            keyword = input("검색어: ")
            samples = sample_controller.search_by_name(keyword)
            if not samples:
                print("일치하는 시료가 없습니다.")
            else:
                for s in samples:
                    print(f"{s.id} | {s.name} | 재고 {s.stock}")
        elif choice == "4":
            return
        else:
            print("잘못된 입력입니다.")
