"""
==============================================================================
TOUR RECOMMENDATION SERVICE - Dịch vụ gợi ý tour du lịch cá nhân hóa
==============================================================================
Service tích hợp các thành phần:
- Tính điểm cá nhân hóa cho từng địa điểm
- Tối ưu lộ trình với OR-Tools
- Tạo tour recommendations
"""

import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any, Optional
from sqlalchemy.orm import Session
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from app.models.destination import Destination


# ==============================================================================
# SCORING ENGINE - Tính điểm cá nhân hóa
# ==============================================================================

class ScoringEngine:
    """Lớp tính toán điểm cá nhân hóa cho từng địa điểm"""
    
    # Trọng số cho các yếu tố (tổng = 1.0)
    WEIGHTS = {
        'type': 0.30,      # Khớp loại địa điểm
        'tags': 0.40,      # Độ tương đồng tags
        'price': 0.20,     # Phù hợp budget
        'time_fit': 0.10   # Phù hợp thời gian
    }
    
    @classmethod
    def calculate_score(cls, user: Dict, place: Dict) -> float:
        """
        Tính điểm cho một địa điểm với user profile cụ thể
        
        Args:
            user: User profile {type, preference, budget, time_available}
            place: Destination data
            
        Returns:
            float: Điểm từ 0.0 đến 1.0
        """
        score = 0.0
        
        # 1. Type matching (30%)
        user_type = user.get('type', '').lower()
        place_type = place.get('type', '').lower()
        if user_type in place_type or place_type in user_type:
            score += cls.WEIGHTS['type']
        
        # 2. Tag similarity (40%)
        user_prefs = set([p.lower() for p in user.get('preference', [])])
        place_tags = set([t.lower() for t in place.get('tags', [])])
        
        if user_prefs and place_tags:
            intersection = len(user_prefs & place_tags)
            union = len(user_prefs | place_tags)
            tag_similarity = intersection / union if union > 0 else 0
            score += cls.WEIGHTS['tags'] * tag_similarity
        
        # 3. Price fit (20%)
        price = place.get('price', 0)
        budget = user.get('budget', float('inf'))
        if budget > 0:
            if price <= budget * 0.3:  # Rẻ hơn 30% budget
                score += cls.WEIGHTS['price']
            elif price <= budget * 0.5:  # Trong 50% budget
                score += cls.WEIGHTS['price'] * 0.8
            elif price <= budget:  # Trong budget
                score += cls.WEIGHTS['price'] * 0.5
        else:
            score += cls.WEIGHTS['price'] * 0.5
        
        # 4. Time fit (10%)
        visit_time = place.get('visit_time', 60)
        time_available = user.get('time_available', 480) * 60  # Convert to minutes
        if time_available > 0:
            time_ratio = min(visit_time / time_available, 1.0)
            score += cls.WEIGHTS['time_fit'] * (1 - time_ratio * 0.5)
        
        return round(score, 3)
    
    @classmethod
    def rank_destinations(
        cls,
        user: Dict,
        destinations: List[Dict],
        top_n: Optional[int] = None
    ) -> List[Tuple[Dict, float]]:
        """
        Tính điểm và xếp hạng các địa điểm
        
        Args:
            user: User profile
            destinations: Danh sách địa điểm
            top_n: Số lượng top muốn lấy (None = tất cả)
            
        Returns:
            List[(destination, score)] đã sắp xếp theo điểm giảm dần
        """
        scored = []
        for dest in destinations:
            score = cls.calculate_score(user, dest)
            scored.append((dest, score))
        
        # Sắp xếp theo điểm giảm dần
        scored.sort(key=lambda x: x[1], reverse=True)
        
        if top_n:
            return scored[:top_n]
        return scored


# ==============================================================================
# DISTANCE CALCULATOR - Tính khoảng cách và thời gian
# ==============================================================================

class DistanceCalculator:
    """Lớp tính toán khoảng cách và thời gian di chuyển"""
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Tính khoảng cách giữa 2 điểm trên bề mặt trái đất (Haversine formula)
        
        Returns:
            float: Khoảng cách (km)
        """
        R = 6371  # Bán kính trái đất (km)
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def calculate_travel_time(distance_km: float, speed_kmh: float = 40) -> int:
        """
        Tính thời gian di chuyển
        
        Args:
            distance_km: Khoảng cách (km)
            speed_kmh: Tốc độ trung bình (km/h)
            
        Returns:
            int: Thời gian (phút)
        """
        if distance_km <= 0:
            return 0
        time_hours = distance_km / speed_kmh
        return int(time_hours * 60)
    
    @classmethod
    def build_distance_matrix(
        cls,
        locations: List[Dict],
        speed_kmh: float = 40
    ) -> Tuple[List[List[int]], List[List[int]]]:
        """
        Xây dựng ma trận khoảng cách và thời gian
        
        Returns:
            (distance_matrix, time_matrix)
        """
        n = len(locations)
        distance_matrix = [[0] * n for _ in range(n)]
        time_matrix = [[0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = cls.haversine_distance(
                        locations[i]['latitude'],
                        locations[i]['longitude'],
                        locations[j]['latitude'],
                        locations[j]['longitude']
                    )
                    distance_matrix[i][j] = dist
                    time_matrix[i][j] = cls.calculate_travel_time(dist, speed_kmh)
        
        return distance_matrix, time_matrix


# ==============================================================================
# ROUTE OPTIMIZER - Tối ưu lộ trình với OR-Tools
# ==============================================================================

class RouteOptimizer:
    """Lớp tối ưu hóa lộ trình du lịch sử dụng OR-Tools VRP"""
    
    def __init__(self, destinations: List[Dict], user: Dict, start_location: Dict):
        """
        Args:
            destinations: Danh sách địa điểm đã có điểm
            user: User profile
            start_location: Điểm khởi hành
        """
        self.user = user
        self.start_location = start_location
        
        # Thêm start location vào đầu danh sách
        self.locations = [start_location] + destinations
        self.num_locations = len(self.locations)
        
        # Build matrices
        self.distance_matrix, self.time_matrix = DistanceCalculator.build_distance_matrix(
            self.locations
        )
        
        # Điểm của từng địa điểm (start location có điểm 0)
        self.scores = [0.0] + [dest.get('score', 0.0) for dest in destinations]
        
        # Time windows
        self.time_windows = self._build_time_windows()
        
        # Constraints
        self.max_time = user.get('time_available', 8) * 60  # Convert to minutes
        self.max_budget = user.get('budget', float('inf'))
        self.max_locations = user.get('max_locations', 5)
    
    def _build_time_windows(self) -> List[Tuple[int, int]]:
        """Xây dựng time windows từ opening_hours"""
        windows = []
        for loc in self.locations:
            opening = loc.get('opening_hours', '00:00-23:59')
            if opening and '-' in opening:
                start_str, end_str = opening.split('-')
                start_h, start_m = map(int, start_str.split(':'))
                end_h, end_m = map(int, end_str.split(':'))
                windows.append((start_h * 60 + start_m, end_h * 60 + end_m))
            else:
                windows.append((0, 24 * 60))
        return windows
    
    def optimize(self) -> Dict:
        """
        Chạy OR-Tools để tối ưu lộ trình
        
        Returns:
            Dict với 'success', 'route', 'total_time', 'total_distance', 'total_score', 'total_cost'
        """
        # Tạo routing model
        manager = pywrapcp.RoutingIndexManager(
            self.num_locations,  # Số locations
            1,                   # Số vehicles (1 tour)
            0                    # Depot (start location)
        )
        routing = pywrapcp.RoutingModel(manager)
        
        # ===== Callback cho distance (for objective) =====
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(self.distance_matrix[from_node][to_node] * 100)  # Convert to int
        
        distance_callback_index = routing.RegisterTransitCallback(distance_callback)
        
        # ===== Callback cho travel time =====
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel_time = self.time_matrix[from_node][to_node]
            visit_time = self.locations[to_node].get('visit_time', 60)
            return travel_time + visit_time
        
        time_callback_index = routing.RegisterTransitCallback(time_callback)
        
        # ===== Time dimension với time windows =====
        routing.AddDimension(
            time_callback_index,
            0,  # Slack
            self.max_time * 3,  # Max total time - increase để dễ tìm solution hơn
            True,  # Start cumul to zero
            'Time'
        )
        
        time_dimension = routing.GetDimensionOrDie('Time')
        
        # Chỉ set time window cho depot (start location)
        # Không set cho các địa điểm khác vì có thể gây conflict với constraints
        depot_index = manager.NodeToIndex(0)
        time_dimension.CumulVar(depot_index).SetRange(0, self.max_time)
        
        # ===== Budget dimension =====
        # Tạm thời comment out để test
        def cost_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return self.locations[from_node].get('price', 0)
        
        cost_callback_index = routing.RegisterUnaryTransitCallback(cost_callback)
        routing.AddDimensionWithVehicleCapacity(
            cost_callback_index,
            0,  # Null slack
            [self.max_budget],  # Max budget
            True,
            'Budget'
        )
        
        # ===== Objective: Minimize distance =====
        # Sử dụng distance callback đã định nghĩa ở trên
        routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)
        
        # Note: Không dùng giới hạn số địa điểm bằng AddConstantDimension 
        # vì có thể gây conflict. Đã filter top N trước khi optimize.
        
        # ===== Search parameters =====
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.AUTOMATIC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.AUTOMATIC
        )
        search_parameters.time_limit.seconds = 30
        search_parameters.log_search = True  # Debug logging
        
        # ===== Solve =====
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            return self._extract_solution(manager, routing, solution)
        else:
            return {
                'success': False,
                'message': 'Không tìm thấy lộ trình phù hợp với các ràng buộc'
            }
    
    def _extract_solution(self, manager, routing, solution) -> Dict:
        """Trích xuất kết quả từ solution"""
        route = []
        total_time = 0
        total_distance = 0.0
        total_score = 0.0
        total_cost = 0
        
        index = routing.Start(0)
        prev_node = None
        
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            location = self.locations[node]
            
            # Tính travel time từ location trước
            travel_time = 0
            if prev_node is not None:
                travel_time = self.time_matrix[prev_node][node]
                travel_distance = self.distance_matrix[prev_node][node]
                total_distance += travel_distance
            
            # Lấy thông tin location
            visit_time = location.get('visit_time', 60)
            price = location.get('price', 0)
            score = self.scores[node]
            
            # Add vào route (bỏ qua start location trong output)
            if node > 0:  # Không add start location
                route.append({
                    'id': location.get('id'),
                    'name': location.get('name'),
                    'type': location.get('type'),
                    'latitude': location.get('latitude'),
                    'longitude': location.get('longitude'),
                    'location_address': location.get('location_address'),
                    'price': price,
                    'visit_time': visit_time,
                    'travel_time': travel_time,
                    'score': score,
                    'opening_hours': location.get('opening_hours'),
                    'facilities': location.get('facilities', []),
                    'images': location.get('images', [])
                })
                
                total_time += visit_time + travel_time
                total_cost += price
                total_score += score
            
            prev_node = node
            index = solution.Value(routing.NextVar(index))
        
        return {
            'success': True,
            'route': route,
            'total_locations': len(route),
            'total_time': total_time,
            'total_distance': round(total_distance, 2),
            'total_score': round(total_score, 3),
            'total_cost': total_cost,
            'avg_score': round(total_score / len(route), 3) if route else 0
        }


# ==============================================================================
# TOUR RECOMMENDATION SERVICE - Service chính
# ==============================================================================

class TourRecommendationService:
    """Service chính cho tour recommendation"""
    
    @staticmethod
    def get_tour_recommendations(
        db: Session,
        user_profile: Dict,
        start_location: Optional[Dict] = None
    ) -> Dict:
        """
        Tạo gợi ý tour cho user
        
        Args:
            db: Database session
            user_profile: {
                'type': 'Adventure' | 'Cultural' | 'Family' | 'Relaxation' | 'Budget',
                'preference': ['nature', 'hiking', ...],
                'budget': 1000000,
                'time_available': 8,  # hours
                'max_locations': 5
            }
            start_location: Điểm khởi hành (optional)
            
        Returns:
            Dict với tour recommendations
        """
        # 1. Lấy tất cả destinations từ database
        destinations = db.query(Destination).filter(
            Destination.is_active == True
        ).all()
        
        if not destinations:
            return {
                'success': False,
                'message': 'Không có địa điểm nào trong hệ thống'
            }
        
        # Convert to dict
        destinations_dict = [dest.to_dict() for dest in destinations]
        print(f"DEBUG: Found {len(destinations_dict)} destinations")
        
        # 2. Tính điểm cho từng địa điểm
        scored_destinations = ScoringEngine.rank_destinations(
            user_profile,
            destinations_dict,
            top_n=min(8, len(destinations_dict))  # Giảm xuống 8 để dễ optimize hơn
        )
        print(f"DEBUG: Scored destinations: {len(scored_destinations)}")
        
        # 3. Prepare destinations for routing
        routing_destinations = []
        for dest, score in scored_destinations:
            dest_copy = dest.copy()
            dest_copy['score'] = score
            routing_destinations.append(dest_copy)
        
        print(f"DEBUG: Routing destinations: {len(routing_destinations)}")
        
        # 4. Set default start location nếu không có
        if not start_location:
            start_location = {
                'id': 0,
                'name': 'Điểm khởi hành',
                'latitude': 10.7769,
                'longitude': 106.7009,
                'visit_time': 0,
                'price': 0
            }
        
        # 5. Optimize route
        optimizer = RouteOptimizer(routing_destinations, user_profile, start_location)
        result = optimizer.optimize()
        
        return result
    
    @staticmethod
    def analyze_destination_scores(
        db: Session,
        user_profile: Dict,
        top_n: int = 10
    ) -> Dict:
        """
        Phân tích điểm của các địa điểm cho user
        
        Returns:
            Dict với top destinations và scores
        """
        destinations = db.query(Destination).filter(
            Destination.is_active == True
        ).all()
        
        destinations_dict = [dest.to_dict() for dest in destinations]
        
        scored = ScoringEngine.rank_destinations(
            user_profile,
            destinations_dict,
            top_n=top_n
        )
        
        result = []
        for dest, score in scored:
            result.append({
                'id': dest['id'],
                'name': dest['name'],
                'type': dest['type'],
                'tags': dest['tags'],
                'price': dest['price'],
                'score': score
            })
        
        return {
            'success': True,
            'user_profile': user_profile,
            'top_destinations': result
        }
