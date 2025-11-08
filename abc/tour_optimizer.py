"""
==============================================================================
HỆ THỐNG GỢI Ý TOUR DU LỊCH CÁ NHÂN HÓA
==============================================================================
Module chính tích hợp các thành phần:
- Đọc dữ liệu địa điểm từ JSON
- Tính điểm cá nhân hóa cho từng địa điểm
- Tối ưu lộ trình với OR-Tools
- In kết quả chi tiết
"""

import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


# ==============================================================================
# MODULE 1: DATA LOADER - Đọc và xử lý dữ liệu
# ==============================================================================

class DestinationLoader:
    """Lớp quản lý việc đọc và xử lý dữ liệu địa điểm"""
    
    @staticmethod
    def load_destinations(file_path: str) -> List[Dict]:
        """
        Đọc dữ liệu địa điểm từ file JSON
        
        Args:
            file_path: Đường dẫn file JSON
            
        Returns:
            Danh sách các địa điểm (dict)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                destinations = json.load(f)
            print(f"✅ Đọc thành công {len(destinations)} địa điểm từ {file_path}")
            return destinations
        except FileNotFoundError:
            print(f"❌ Không tìm thấy file: {file_path}")
            return []
        except json.JSONDecodeError:
            print(f"❌ File JSON không hợp lệ: {file_path}")
            return []
    
    @staticmethod
    def filter_active_destinations(destinations: List[Dict]) -> List[Dict]:
        """Lọc chỉ các địa điểm đang hoạt động"""
        return [d for d in destinations if d.get('is_active', True)]
    
    @staticmethod
    def parse_opening_hours(opening_hours: str) -> Tuple[int, int]:
        """
        Chuyển đổi giờ mở cửa từ string sang phút
        
        Args:
            opening_hours: Chuỗi dạng "08:00-17:30"
            
        Returns:
            Tuple (start_minutes, end_minutes) tính từ 00:00
        """
        try:
            start, end = opening_hours.split('-')
            start_h, start_m = map(int, start.split(':'))
            end_h, end_m = map(int, end.split(':'))
            return (start_h * 60 + start_m, end_h * 60 + end_m)
        except:
            return (0, 1440)  # Mặc định cả ngày


# ==============================================================================
# MODULE 2: SCORING ENGINE - Tính điểm cá nhân hóa
# ==============================================================================

class ScoringEngine:
    """Lớp tính toán điểm cá nhân hóa cho từng địa điểm"""
    
    # Trọng số cho các yếu tố (tổng = 1.0)
    WEIGHTS = {
        'type': 0.30,      # Khớp loại địa điểm với loại user
        'tags': 0.40,      # Độ tương đồng tags/sở thích
        'price': 0.20,     # Khả năng chi trả
        'time_fit': 0.10   # Thời gian phù hợp
    }
    
    @classmethod
    def calculate_score(cls, user: Dict, place: Dict) -> float:
        """
        Tính điểm cá nhân hóa cho một địa điểm
        
        Args:
            user: Thông tin user (type, preference, budget, time_available)
            place: Thông tin địa điểm
            
        Returns:
            Điểm score từ 0.0 đến 1.0
        """
        score = 0.0
        
        # 1. Type matching - Khớp loại địa điểm với loại user
        user_type = user.get('type', '').lower()
        place_type = place.get('type', '').lower()
        if user_type in place_type or place_type in user_type:
            score += cls.WEIGHTS['type']
        
        # 2. Tag similarity - Độ tương đồng tags
        user_prefs = set([p.lower() for p in user.get('preference', [])])
        place_tags = set([t.lower() for t in place.get('tags', [])])
        if place_tags:
            tag_match = len(user_prefs & place_tags) / len(place_tags)
            score += tag_match * cls.WEIGHTS['tags']
        
        # 3. Price affordability - Khả năng chi trả
        price = place.get('price', 0)
        budget = user.get('budget', float('inf'))
        if budget > 0:
            price_score = max(0, 1 - (price / budget))
            score += price_score * cls.WEIGHTS['price']
        else:
            score += cls.WEIGHTS['price'] if price == 0 else 0
        
        # 4. Time fit - Thời gian phù hợp
        visit_time = place.get('visit_time', 60)
        time_available = user.get('time_available', 480) * 60  # Convert hours to minutes
        if time_available > 0:
            time_fit = min(visit_time / time_available, 1.0)
            score += time_fit * cls.WEIGHTS['time_fit']
        
        return round(score, 3)
    
    @classmethod
    def rank_destinations(cls, user: Dict, destinations: List[Dict], top_n: int = None) -> List[Tuple[Dict, float]]:
        """
        Xếp hạng các địa điểm theo điểm
        
        Args:
            user: Thông tin user
            destinations: Danh sách địa điểm
            top_n: Số lượng địa điểm top cần lấy (None = tất cả)
            
        Returns:
            Danh sách tuple (destination, score) đã sắp xếp
        """
        scored = [(dest, cls.calculate_score(user, dest)) for dest in destinations]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        if top_n:
            return scored[:top_n]
        return scored


# ==============================================================================
# MODULE 3: DISTANCE CALCULATOR - Tính khoảng cách và thời gian
# ==============================================================================

class DistanceCalculator:
    """Lớp tính toán khoảng cách và thời gian di chuyển"""
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Tính khoảng cách Haversine giữa 2 điểm (km)
        
        Args:
            lat1, lon1: Tọa độ điểm 1
            lat2, lon2: Tọa độ điểm 2
            
        Returns:
            Khoảng cách (km)
        """
        R = 6371  # Bán kính Trái Đất (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def calculate_travel_time(distance_km: float, speed_kmh: float = 40) -> int:
        """
        Tính thời gian di chuyển (phút)
        
        Args:
            distance_km: Khoảng cách (km)
            speed_kmh: Tốc độ trung bình (km/h)
            
        Returns:
            Thời gian (phút)
        """
        return int((distance_km / speed_kmh) * 60)
    
    @classmethod
    def build_distance_matrix(cls, locations: List[Dict], include_start: bool = True) -> List[List[int]]:
        """
        Xây dựng ma trận khoảng cách (thời gian di chuyển) giữa các địa điểm
        
        Args:
            locations: Danh sách các địa điểm có lat/lon
            include_start: True nếu điểm đầu là điểm khởi hành (hotel)
            
        Returns:
            Ma trận thời gian di chuyển (phút)
        """
        n = len(locations)
        matrix = [[0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = cls.haversine_distance(
                        locations[i]['latitude'],
                        locations[i]['longitude'],
                        locations[j]['latitude'],
                        locations[j]['longitude']
                    )
                    matrix[i][j] = cls.calculate_travel_time(dist)
        
        return matrix


# ==============================================================================
# MODULE 4: ROUTE OPTIMIZER - Tối ưu lộ trình với OR-Tools
# ==============================================================================

class RouteOptimizer:
    """Lớp tối ưu hóa lộ trình du lịch sử dụng OR-Tools VRP"""
    
    def __init__(self, destinations: List[Dict], user: Dict, start_location: Dict):
        """
        Khởi tạo optimizer
        
        Args:
            destinations: Danh sách các địa điểm đã được chọn
            user: Thông tin user
            start_location: Vị trí khởi hành (hotel)
        """
        self.destinations = destinations
        self.user = user
        self.start_location = start_location
        
        # Thêm start location vào đầu danh sách
        self.all_locations = [start_location] + destinations
        
        # Build distance matrix
        self.distance_matrix = DistanceCalculator.build_distance_matrix(self.all_locations)
        
        # Build time windows
        self.time_windows = self._build_time_windows()
        
        # Build visit times
        self.visit_times = [0] + [d.get('visit_time', 60) for d in destinations]
        
        # Build costs
        self.costs = [0] + [d.get('price', 0) for d in destinations]
        
        # Build scores
        self.scores = [0] + [d.get('_score', 0) for d in destinations]
    
    def _build_time_windows(self) -> List[Tuple[int, int]]:
        """Xây dựng time windows cho từng địa điểm"""
        windows = [(0, 1440)]  # Start location: cả ngày
        
        for dest in self.destinations:
            opening_hours = dest.get('opening_hours', '00:00-23:59')
            windows.append(DestinationLoader.parse_opening_hours(opening_hours))
        
        return windows
    
    def optimize(self) -> Dict:
        """
        Thực hiện tối ưu lộ trình
        
        Returns:
            Dictionary chứa lộ trình tối ưu và thông tin liên quan
        """
        # Tạo routing index manager
        manager = pywrapcp.RoutingIndexManager(
            len(self.distance_matrix),
            1,  # Số lượng vehicle (tour)
            0   # Depot (điểm xuất phát)
        )
        
        # Tạo routing model
        routing = pywrapcp.RoutingModel(manager)
        
        # ===== 1. Distance callback =====
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self.distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # ===== 2. Time dimension với time windows =====
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = self.distance_matrix[from_node][to_node]
            service_time = self.visit_times[from_node]
            return travel_time + service_time
        
        time_callback_index = routing.RegisterTransitCallback(time_callback)
        
        max_time = self.user.get('time_available', 8) * 60  # Convert hours to minutes
        routing.AddDimension(
            time_callback_index,
            30,  # Slack time (phút) - thời gian buffer
            max_time,  # Tổng thời gian tối đa
            False,  # Start cumul to zero
            'Time'
        )
        
        time_dimension = routing.GetDimensionOrDie('Time')
        
        # Thêm time windows constraints (soft constraints via penalties)
        # Không dùng hard constraints vì có thể làm bài toán không khả thi
        for location_idx, time_window in enumerate(self.time_windows):
            if location_idx == 0:  # Skip depot
                continue
            index = manager.NodeToIndex(location_idx)
            # Thêm soft time windows bằng cách set min/max feasible
            time_dimension.CumulVar(index).SetMin(0)
            time_dimension.CumulVar(index).SetMax(max_time)
        
        # ===== 3. Budget constraint =====
        def cost_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return self.costs[from_node]
        
        cost_callback_index = routing.RegisterUnaryTransitCallback(cost_callback)
        
        max_budget = self.user.get('budget', float('inf'))
        routing.AddDimension(
            cost_callback_index,
            0,  # Không có slack
            int(max_budget),
            True,  # Start cumul to zero
            'Cost'
        )
        
        # ===== 4. Max locations constraint =====
        max_locations = self.user.get('max_locations', len(self.destinations))
        routing.solver().Add(
            routing.solver().Sum([
                routing.ActiveVar(manager.NodeToIndex(i))
                for i in range(1, len(self.all_locations))
            ]) <= max_locations
        )
        
        # ===== 5. Disjunctions - cho phép bỏ qua một số địa điểm =====
        penalty = 10000  # Penalty khi bỏ qua địa điểm
        for node in range(1, len(self.all_locations)):
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
        
        # ===== Search parameters =====
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 10
        
        # ===== Solve =====
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            return self._extract_solution(manager, routing, solution)
        else:
            return {
                'success': False,
                'message': 'Không tìm thấy lộ trình khả thi với các ràng buộc đã cho.'
            }
    
    def _extract_solution(self, manager, routing, solution) -> Dict:
        """Trích xuất thông tin từ solution"""
        time_dimension = routing.GetDimensionOrDie('Time')
        cost_dimension = routing.GetDimensionOrDie('Cost')
        
        route = []
        index = routing.Start(0)
        total_distance = 0
        total_time = 0
        total_cost = 0
        total_score = 0
        
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            cost_var = cost_dimension.CumulVar(index)
            
            arrival_time = solution.Value(time_var)
            current_cost = solution.Value(cost_var)
            
            if node > 0:  # Skip depot trong output
                location = self.all_locations[node]
                route.append({
                    'id': location.get('id'),
                    'name': location.get('name'),
                    'arrival_time': arrival_time,
                    'visit_time': self.visit_times[node],
                    'cost': self.costs[node],
                    'score': self.scores[node]
                })
                total_cost += self.costs[node]
                total_score += self.scores[node]
            
            # Next location
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            
            if not routing.IsEnd(index):
                from_node = manager.IndexToNode(previous_index)
                to_node = manager.IndexToNode(index)
                total_distance += self.distance_matrix[from_node][to_node]
        
        # Total time = arrival time tại điểm cuối
        final_index = previous_index
        time_var = time_dimension.CumulVar(final_index)
        total_time = solution.Value(time_var)
        
        return {
            'success': True,
            'route': route,
            'total_locations': len(route),
            'total_distance': total_distance,
            'total_time': total_time,
            'total_cost': total_cost,
            'total_score': round(total_score, 2),
            'avg_score': round(total_score / len(route), 2) if route else 0
        }


# ==============================================================================
# MODULE 5: TOUR PLANNER - Tích hợp toàn bộ pipeline
# ==============================================================================

class TourPlanner:
    """Lớp tích hợp toàn bộ pipeline gợi ý tour"""
    
    def __init__(self, destinations_file: str):
        """
        Khởi tạo tour planner
        
        Args:
            destinations_file: Đường dẫn file JSON chứa dữ liệu địa điểm
        """
        self.destinations = DestinationLoader.load_destinations(destinations_file)
        self.destinations = DestinationLoader.filter_active_destinations(self.destinations)
    
    def plan_tour(self, user: Dict, start_location: Dict = None) -> Dict:
        """
        Lên kế hoạch tour cho user
        
        Args:
            user: Thông tin user
            start_location: Vị trí khởi hành (mặc định: Hà Nội)
            
        Returns:
            Dictionary chứa kết quả tour
        """
        print("\n" + "="*70)
        print("🗺️  TOUR PLANNER - GỢI Ý TOUR DU LỊCH CÁ NHÂN HÓA")
        print("="*70)
        
        # Default start location
        if start_location is None:
            start_location = {
                'id': 0,
                'name': 'Điểm Khởi Hành',
                'latitude': 21.0285,
                'longitude': 105.8542,
                'visit_time': 0,
                'price': 0
            }
        
        # BƯỚC 1: Tính điểm và lọc địa điểm
        print("\n📊 BƯỚC 1: TÍNH ĐIỂM VÀ LỌC ĐỊA ĐIỂM")
        print("-" * 70)
        
        top_n = user.get('max_locations', 10) * 2  # Lấy gấp đôi để có nhiều lựa chọn
        scored_destinations = ScoringEngine.rank_destinations(user, self.destinations, top_n)
        
        print(f"✅ Đã tính điểm cho {len(self.destinations)} địa điểm")
        print(f"✅ Chọn top {len(scored_destinations)} địa điểm khả thi")
        
        # Lưu score vào destination để dùng sau
        for dest, score in scored_destinations:
            dest['_score'] = score
        
        # Lọc theo budget
        budget = user.get('budget', float('inf'))
        feasible_destinations = [
            dest for dest, score in scored_destinations 
            if dest.get('price', 0) <= budget
        ]
        
        print(f"✅ Sau khi lọc budget: còn {len(feasible_destinations)} địa điểm")
        
        if not feasible_destinations:
            return {
                'success': False,
                'message': 'Không tìm thấy địa điểm nào phù hợp với budget.'
            }
        
        # BƯỚC 2: Tối ưu lộ trình
        print("\n🚀 BƯỚC 2: TỐI ƯU LỘ TRÌNH VỚI OR-TOOLS")
        print("-" * 70)
        
        optimizer = RouteOptimizer(feasible_destinations, user, start_location)
        result = optimizer.optimize()
        
        if result['success']:
            print("✅ Tìm thấy lộ trình tối ưu!")
        else:
            print("❌ Không tìm thấy lộ trình khả thi")
        
        return result
    
    @staticmethod
    def format_time(minutes: int) -> str:
        """Chuyển phút thành định dạng HH:MM"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    @staticmethod
    def print_tour_result(result: Dict, user: Dict):
        """In kết quả tour chi tiết"""
        if not result.get('success'):
            print(f"\n❌ {result.get('message', 'Lỗi không xác định')}")
            return
        
        print("\n" + "="*70)
        print("🎉 KẾT QUẢ TOUR TỐI ƯU")
        print("="*70)
        
        print(f"\n👤 User: {user.get('name', 'Unknown')}")
        print(f"🎯 Loại: {user.get('type')}")
        print(f"💰 Budget: {user.get('budget', 0):,.0f} VNĐ")
        print(f"⏰ Thời gian có: {user.get('time_available', 0)} giờ")
        
        print("\n📈 TỔNG QUAN:")
        print(f"  • Số địa điểm: {result['total_locations']}")
        print(f"  • Tổng quãng đường: {result['total_distance']} phút di chuyển")
        print(f"  • Tổng thời gian: {result['total_time']} phút ({result['total_time']//60}h {result['total_time']%60}m)")
        print(f"  • Tổng chi phí: {result['total_cost']:,.0f} VNĐ")
        print(f"  • Tổng điểm: {result['total_score']}")
        print(f"  • Điểm TB: {result['avg_score']}/1.0")
        
        print("\n🗺️  LỘ TRÌNH CHI TIẾT:")
        print("-" * 70)
        
        for i, stop in enumerate(result['route'], 1):
            arrival = TourPlanner.format_time(stop['arrival_time'])
            departure = TourPlanner.format_time(stop['arrival_time'] + stop['visit_time'])
            
            print(f"\n{i}. {stop['name']} (ID: {stop['id']})")
            print(f"   ⏰ Đến: {arrival} | Rời: {departure} | Thời gian tham quan: {stop['visit_time']} phút")
            print(f"   💰 Chi phí: {stop['cost']:,.0f} VNĐ | ⭐ Điểm: {stop['score']}")
        
        print("\n" + "="*70)


# ==============================================================================
# MAIN - Chương trình chính
# ==============================================================================

def main():
    """Hàm chính để chạy chương trình"""
    
    # ===== KHỞI TẠO PLANNER =====
    planner = TourPlanner('destinations_data.json')
    
    # ===== ĐỊNH NGHĨA USER PROFILES =====
    users = [
        {
            'name': 'Nguyễn Văn A',
            'type': 'Adventure',
            'preference': ['nature', 'adventure', 'hiking', 'photography'],
            'budget': 1000000,  # 1 triệu VNĐ
            'time_available': 10,  # 10 giờ
            'max_locations': 5
        },
        {
            'name': 'Trần Thị B',
            'type': 'Cultural',
            'preference': ['culture', 'history', 'museum', 'art'],
            'budget': 500000,
            'time_available': 6,
            'max_locations': 4
        },
        {
            'name': 'Lê Gia Đình C',
            'type': 'Family',
            'preference': ['family', 'kids', 'park', 'safe'],
            'budget': 800000,
            'time_available': 8,
            'max_locations': 4
        },
        {
            'name': 'Phạm Thư Giãn D',
            'type': 'Relaxation',
            'preference': ['relaxation', 'spa', 'cafe', 'peaceful'],
            'budget': 600000,
            'time_available': 5,
            'max_locations': 3
        },
        {
            'name': 'Hoàng Tiết Kiệm E',
            'type': 'Budget',
            'preference': ['budget', 'local', 'street_food', 'market'],
            'budget': 200000,
            'time_available': 7,
            'max_locations': 5
        }
    ]
    
    # ===== CHẠY PLANNING CHO TỪNG USER =====
    for user in users:
        result = planner.plan_tour(user)
        TourPlanner.print_tour_result(result, user)
        print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
