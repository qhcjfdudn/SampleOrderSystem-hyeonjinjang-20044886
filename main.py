from config import Config
from app.controllers.monitoring_controller import MonitoringController
from app.controllers.order_controller import OrderController
from app.controllers.production_line_controller import ProductionLineController
from app.controllers.sample_controller import SampleController
from app.models.order_repository import OrderRepository
from app.models.sample_repository import SampleRepository
from app.views.monitoring_view import run_monitoring_menu
from app.views.order_view import run_order_approval_menu, run_order_menu, run_release_menu
from app.views.production_view import run_production_menu
from app.views.sample_view import run_sample_menu


def main():
    sample_repository = SampleRepository(Config.SAMPLES_FILE)
    order_repository = OrderRepository(Config.ORDERS_FILE)
    sample_controller = SampleController(sample_repository)
    order_controller = OrderController(order_repository, sample_repository)
    production_line_controller = ProductionLineController(order_repository, sample_repository)
    monitoring_controller = MonitoringController(order_repository, sample_repository)

    while True:
        samples = sample_controller.list_samples()
        total_stock = sum(sample.stock for sample in samples)
        total_orders = len(order_repository.find_all())
        producing_count = monitoring_controller.order_status_counts()["PRODUCING"]

        print(
            f"등록 시료 수: {len(samples)} | 총 재고: {total_stock} | "
            f"전체 주문 건수: {total_orders} | 생산라인 대기 건수: {producing_count}"
        )
        print("1. 시료 관리")
        print("2. 시료 주문")
        print("3. 주문 승인/거절")
        print("4. 생산 라인 조회")
        print("5. 출고 처리")
        print("6. 모니터링")
        print("7. 종료")
        choice = input("선택: ")

        if choice == "1":
            run_sample_menu(sample_controller)
        elif choice == "2":
            run_order_menu(order_controller)
        elif choice == "3":
            run_order_approval_menu(order_controller)
        elif choice == "4":
            run_production_menu(production_line_controller)
        elif choice == "5":
            run_release_menu(order_controller)
        elif choice == "6":
            run_monitoring_menu(monitoring_controller)
        elif choice == "7":
            return
        else:
            print("잘못된 입력입니다.")


if __name__ == "__main__":
    main()
