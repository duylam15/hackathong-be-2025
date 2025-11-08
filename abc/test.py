# Import thư viện OR-Tools (Constraint Solver)
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


# =========================================
# 1️⃣ TẠO DỮ LIỆU MẪU
# =========================================
def create_data():
    data = {}

    # Ma trận khoảng cách giữa các điểm (distance_matrix[i][j] = khoảng cách từ i -> j)
    data['distance_matrix'] = [
        [0, 10, 12, 8, 20],   # Điểm 0 đến các điểm khác
        [10, 0, 5, 6, 15],    # Điểm 1 ...
        [12, 5, 0, 4, 10],
        [8, 6, 4, 0, 7],
        [20, 15, 10, 7, 0],
    ]

    # Thời gian mở cửa (time windows) cho từng địa điểm
    # (min_time, max_time) — nghĩa là phải đến trong khoảng này
    data['time_windows'] = [
        (0, 600),   # Điểm 0 (Hotel) — không giới hạn
        (480, 1020),# Điểm 1 (Museum) — 8h -> 17h
        (360, 1200),# Điểm 2 (Park) — 6h -> 20h
        (420, 1320),# Điểm 3 (Cafe) — 7h -> 22h
        (540, 1080) # Điểm 4 (Art Street) — 9h -> 18h
    ]

    # Điểm hấp dẫn (score) của từng điểm — càng cao càng “đáng đi”
    data['scores'] = [0.0, 0.9, 0.7, 0.8, 0.95]

    # Chi phí mỗi điểm (có thể hiểu là vé vào cửa, tiền xăng, v.v.)
    data['cost'] = [0, 15, 5, 10, 0]

    # Số lượng xe (tour guide / nhóm khách)
    data['num_vehicles'] = 1

    # Điểm khởi hành (depot) — thường là khách sạn hoặc bến xe
    data['depot'] = 0
    return data


# =========================================
# 2️⃣ HÀM CHÍNH
# =========================================
def main():
    data = create_data()

    # Quản lý các node (điểm) và số lượng xe
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),  # Tổng số điểm
        data['num_vehicles'],          # Số lượng xe
        data['depot']                  # Điểm xuất phát (depot)
    )

    # Mô hình định tuyến (Routing Model)
    routing = pywrapcp.RoutingModel(manager)


    # -----------------------------------------
    # 🔹 Callback cho khoảng cách (chi phí di chuyển giữa 2 điểm)
    # -----------------------------------------
    def distance_callback(from_index, to_index):
        # Lấy ID thật từ chỉ số nội bộ
        f, t = manager.IndexToNode(from_index), manager.IndexToNode(to_index)

        # Khoảng cách gốc giữa hai điểm
        base_distance = data['distance_matrix'][f][t]

        # Giảm chi phí nếu điểm đến hấp dẫn (score cao)
        # → score cao => (1 - score) nhỏ => attraction_bonus nhỏ => đường đó “rẻ” hơn
        attraction_bonus = int((1 - data['scores'][t]) * 5)

        return base_distance + attraction_bonus

    # Đăng ký callback vào hệ thống định tuyến
    dist_cb_idx = routing.RegisterTransitCallback(distance_callback)

    # Dùng hàm này làm “hàm chi phí” cho tất cả các xe
    routing.SetArcCostEvaluatorOfAllVehicles(dist_cb_idx)


    # -----------------------------------------
    # 🔹 Thêm ràng buộc thời gian (time dimension)
    # -----------------------------------------
    time_cb_idx = routing.RegisterTransitCallback(distance_callback)
    routing.AddDimension(
        time_cb_idx,     # Callback cho thời gian
        1000,            # Slack tối đa (cho phép chờ)
        2000,            # Tổng thời gian tối đa (giới hạn tour)
        True,             # True: cho phép chờ đợi khi tới sớm
        'Time'            # Tên dimension
    )

    # Lấy đối tượng Dimension “Time”
    time_dim = routing.GetDimensionOrDie('Time')

    # Gán ràng buộc giờ mở cửa cho từng điểm
    for i, window in enumerate(data['time_windows']):
        index = manager.NodeToIndex(i)
        time_dim.CumulVar(index).SetRange(window[0], window[1])


    # -----------------------------------------
    # 🔹 Thêm ràng buộc chi phí (budget dimension)
    # -----------------------------------------
    def cost_callback(from_index):
        # Mỗi lần ghé điểm này thì tốn bấy nhiêu tiền
        f = manager.IndexToNode(from_index)
        return int(data['cost'][f])

    # Đăng ký callback chi phí
    cost_cb_idx = routing.RegisterUnaryTransitCallback(cost_callback)

    # Tạo “dimension” để giới hạn tổng chi phí <= 50$
    routing.AddDimensionWithVehicleCapacity(
        cost_cb_idx,  # Callback
        0,            # Không cho âm
        [50],         # Ngân sách tối đa của mỗi xe
        True,         # Tích lũy từ điểm xuất phát
        'Budget'      # Tên dimension
    )


    # -----------------------------------------
    # 🔹 Cấu hình chiến lược tìm lời giải
    # -----------------------------------------
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    # Dùng chiến lược “đi cạnh rẻ nhất trước”
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Giải bài toán tối ưu
    solution = routing.SolveWithParameters(search_params)


    # -----------------------------------------
    # 🔹 In kết quả ra màn hình
    # -----------------------------------------
    if solution:
        index = routing.Start(0)  # Bắt đầu từ depot
        plan = []
        total_cost = 0
        total_time = 0
        time_dim = routing.GetDimensionOrDie('Time')

        # Duyệt qua từng điểm trong hành trình
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            t = solution.Min(time_dim.CumulVar(index))  # Thời gian tại điểm đó
            plan.append((node, t))
            total_cost += data['cost'][node]
            index = solution.Value(routing.NextVar(index))

        # Quay lại điểm xuất phát
        plan.append((manager.IndexToNode(index), solution.Min(time_dim.CumulVar(index))))

        # In ra kết quả
        print("🗺️ Lộ trình tối ưu:")
        for node, t in plan:
            print(f"  - Điểm {node} (thời gian: {t} phút)")
        print("💰 Tổng chi phí:", total_cost)
    else:
        print("❌ Không tìm được lộ trình hợp lệ")


# =========================================
# 3️⃣ CHẠY CHƯƠNG TRÌNH
# =========================================
if __name__ == '__main__':
    main()