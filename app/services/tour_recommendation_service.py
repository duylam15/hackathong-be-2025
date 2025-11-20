"""
==============================================================================
TOUR RECOMMENDATION SERVICE - Dịch vụ gợi ý tour du lịch cá nhân hóa
==============================================================================
Service tích hợp các thành phần:
- Tính điểm cá nhân hóa cho từng địa điểm (Content-Based)
- Collaborative Filtering (User behavior learning)
- Hybrid Scoring (CB + CF)
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
from app.services.collaborative_filtering_service import CollaborativeFilteringService


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
    
    @classmethod
    def rank_destinations_hybrid(
        cls,
        user: Dict,
        destinations: List[Dict],
        db: Session,
        user_id: Optional[int] = None,
        use_cf: bool = True,
        top_n: Optional[int] = None
    ) -> List[Tuple[Dict, float, Dict]]:
        """
        Tính điểm hybrid (Content-Based + Collaborative Filtering) và xếp hạng
        
        Args:
            user: User profile
            destinations: Danh sách địa điểm
            db: Database session
            user_id: User ID (None = anonymous, chỉ dùng CB)
            use_cf: Enable CF (False = CB only)
            top_n: Số lượng top muốn lấy
            
        Returns:
            List[(destination, final_score, metadata)] đã sắp xếp theo điểm giảm dần
        """
        scored = []
        
        # Step 1: Content-Based Scoring (Always)
        for dest in destinations:
            cb_score = cls.calculate_score(user, dest)
            dest['cb_score'] = cb_score
        
        # Step 2: Collaborative Filtering Scoring (if user_id provided)
        if use_cf and user_id:
            try:
                cf_service = CollaborativeFilteringService(db)
                dest_ids = [d['id'] for d in destinations]
                
                # Get CF scores batch
                cf_scores = cf_service.get_cf_scores_for_destinations(user_id, dest_ids)
                
                # Get user activity level for adaptive weighting
                activity = cf_service.get_user_activity_level(user_id)
                cf_weight = activity['recommended_cf_weight']
                cb_weight = 1 - cf_weight
                
                print(f"DEBUG CF: User activity level: {activity['activity_level']}, "
                      f"CF weight: {cf_weight:.2f}, CB weight: {cb_weight:.2f}")
                
                # Hybrid scoring
                for dest in destinations:
                    dest_id = dest['id']
                    cb_score = dest['cb_score']
                    
                    if dest_id in cf_scores:
                        cf_data = cf_scores[dest_id]
                        cf_score = cf_data['cf_score']
                        cf_confidence = cf_data['confidence']
                        
                        # Adjust weight based on CF confidence
                        if cf_confidence > 0.7:
                            # High confidence → trust CF more
                            alpha_cb = 0.3
                            alpha_cf = 0.7
                        elif cf_confidence > 0.4:
                            # Medium confidence → use recommended weights
                            alpha_cb = cb_weight
                            alpha_cf = cf_weight
                        else:
                            # Low confidence → rely on CB
                            alpha_cb = 0.8
                            alpha_cf = 0.2
                        
                        # Calculate hybrid score
                        final_score = alpha_cb * cb_score + alpha_cf * cf_score
                        
                        metadata = {
                            'cb_score': round(cb_score, 3),
                            'cf_score': round(cf_score, 3),
                            'cf_confidence': round(cf_confidence, 2),
                            'cf_method': cf_data['method'],
                            'alpha_cb': round(alpha_cb, 2),
                            'alpha_cf': round(alpha_cf, 2),
                            'scoring_method': 'hybrid'
                        }
                    else:
                        # No CF score available, use CB only
                        final_score = cb_score
                        metadata = {
                            'cb_score': round(cb_score, 3),
                            'scoring_method': 'content_based'
                        }
                    
                    scored.append((dest, final_score, metadata))
                
                print(f"DEBUG CF: Hybrid scoring completed for {len(scored)} destinations")
                
            except Exception as e:
                print(f"ERROR CF: Collaborative filtering failed: {str(e)}")
                # Fallback to content-based only
                for dest in destinations:
                    scored.append((dest, dest['cb_score'], {
                        'cb_score': round(dest['cb_score'], 3),
                        'scoring_method': 'content_based',
                        'cf_error': str(e)
                    }))
        else:
            # Content-based only (no user_id or CF disabled)
            for dest in destinations:
                scored.append((dest, dest['cb_score'], {
                    'cb_score': round(dest['cb_score'], 3),
                    'scoring_method': 'content_based'
                }))
        
        # Sort by final score descending
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
# HEURISTIC OPTIMIZER - Thuật toán tham lam đơn giản (Fallback)
# ==============================================================================

class HeuristicOptimizer:
    """
    Lớp tối ưu hóa lộ trình sử dụng thuật toán tham lam (greedy heuristic)
    Được dùng khi OR-Tools không tìm được solution
    """
    
    def __init__(self, destinations: List[Dict], user: Dict, start_location: Dict):
        """
        Args:
            destinations: Danh sách địa điểm đã có điểm
            user: User profile
            start_location: Điểm khởi hành
        """
        self.user = user
        self.start_location = start_location
        self.destinations = destinations
        
        # Constraints
        self.max_time = user.get('time_available', 8) * 60  # Convert to minutes
        self.max_budget = user.get('budget', float('inf'))
        self.max_locations = user.get('max_locations', 5)
    
    def optimize_greedy(self) -> Dict:
        """
        Thuật toán tham lam: Chọn địa điểm gần nhất có điểm cao
        
        Strategy:
        1. Bắt đầu từ start location
        2. Chọn địa điểm chưa thăm có score/distance ratio cao nhất
        3. Kiểm tra constraints (time, budget)
        4. Lặp lại cho đến khi không thêm được địa điểm nào
        
        Returns:
            Dict với route đơn giản
        """
        route = []
        visited = set()
        current_location = self.start_location
        
        total_time = 0
        total_distance = 0.0
        total_score = 0.0
        total_cost = 0
        
        print(f"🔄 Fallback to Heuristic Optimizer (Greedy Algorithm)")
        
        while len(route) < self.max_locations:
            best_dest = None
            best_metric = -1
            best_travel_time = 0
            best_distance = 0
            
            # Tìm địa điểm tốt nhất chưa thăm
            for dest in self.destinations:
                dest_id = dest.get('id')
                
                if dest_id in visited:
                    continue
                
                # Tính khoảng cách và thời gian
                distance = DistanceCalculator.haversine_distance(
                    current_location['latitude'],
                    current_location['longitude'],
                    dest['latitude'],
                    dest['longitude']
                )
                
                travel_time = DistanceCalculator.calculate_travel_time(distance)
                visit_time = dest.get('visit_time', 60)
                price = dest.get('price', 0)
                score = dest.get('score', 0)
                
                # Kiểm tra constraints
                new_time = total_time + travel_time + visit_time
                new_cost = total_cost + price
                
                if new_time > self.max_time or new_cost > self.max_budget:
                    continue
                
                # Tính metric: score/distance (ưu tiên gần + điểm cao)
                # Thêm penalty cho khoảng cách xa
                distance_penalty = max(1, distance / 10)  # Divide by 10km
                metric = score / distance_penalty
                
                if metric > best_metric:
                    best_metric = metric
                    best_dest = dest
                    best_travel_time = travel_time
                    best_distance = distance
            
            # Nếu không tìm được địa điểm nào thỏa mãn -> dừng
            if best_dest is None:
                break
            
            # Thêm địa điểm vào route
            visited.add(best_dest['id'])
            
            route.append({
                'id': best_dest['id'],
                'name': best_dest['name'],
                'type': best_dest['type'],
                'latitude': best_dest['latitude'],
                'longitude': best_dest['longitude'],
                'location_address': best_dest.get('location_address'),
                'price': best_dest['price'],
                'visit_time': best_dest['visit_time'],
                'travel_time': best_travel_time,
                'score': best_dest['score'],
                'opening_hours': best_dest.get('opening_hours'),
                'facilities': best_dest.get('facilities', []),
                'images': best_dest.get('images', [])
            })
            
            # Update totals
            total_time += best_travel_time + best_dest['visit_time']
            total_distance += best_distance
            total_cost += best_dest['price']
            total_score += best_dest['score']
            
            # Update current location
            current_location = best_dest
        
        if not route:
            return {
                'success': False,
                'message': 'Không thể tạo tour với constraints hiện tại (quá chặt)'
            }
        
        return {
            'success': True,
            'route': route,
            'total_locations': len(route),
            'total_time': total_time,
            'total_distance': round(total_distance, 2),
            'total_score': round(total_score, 3),
            'total_cost': total_cost,
            'avg_score': round(total_score / len(route), 3) if route else 0,
            'optimizer_used': 'heuristic'  # Đánh dấu dùng heuristic
        }


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
            self.max_time,  # Max total time - increase để dễ tìm solution hơn
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
            result = self._extract_solution(manager, routing, solution)
            result['optimizer_used'] = 'ortools'  # Đánh dấu dùng OR-Tools
            return result
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
        start_location: Optional[Dict] = None,
        user_id: Optional[int] = None,  # NEW: User ID for CF
        use_cf: bool = True  # NEW: Enable/disable CF
    ) -> Dict:
        """
        Tạo gợi ý tour cho user với Hybrid Recommendation (CB + CF)
        
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
            user_id: User ID for collaborative filtering (None = anonymous, content-based only)
            use_cf: Enable collaborative filtering (False = content-based only)
            
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
        
        # 1.5. Filter destinations hợp lệ (tọa độ ở Việt Nam, visit_time hợp lý)
        valid_destinations = []
        for dest in destinations_dict:
            lat = dest.get('latitude', 0)
            lon = dest.get('longitude', 0)
            visit_time = dest.get('visit_time', 0)
            
            # Vietnam: latitude 8-24, longitude 102-110
            if (8 <= lat <= 24 and 102 <= lon <= 110 and 
                visit_time > 0 and visit_time <= 600):  # Max 10 hours per location
                valid_destinations.append(dest)
            else:
                print(f"DEBUG: Filtered out '{dest.get('name')}' - Invalid location ({lat}, {lon}) or visit_time ({visit_time})")
        
        print(f"DEBUG: Valid destinations after filtering: {len(valid_destinations)}")
        
        if not valid_destinations:
            return {
                'success': False,
                'message': 'Không có địa điểm hợp lệ trong hệ thống'
            }
        
        # 4. Set default start location nếu không có (Sài Gòn center)
        if not start_location:
            start_location = {
                'id': 0,
                'name': 'Điểm khởi hành',
                'latitude': 10.7769,
                'longitude': 106.7009,
                'visit_time': 0,
                'price': 0
            }
        
        # 2. Filter theo khoảng cách (chỉ giữ địa điểm trong bán kính hợp lý)
        start_lat = start_location.get('latitude', 10.7769)
        start_lon = start_location.get('longitude', 106.7009)
        
        nearby_destinations = []
        max_distance_km = 50  # Bán kính 50km
        
        for dest in valid_destinations:
            dist = DistanceCalculator.haversine_distance(
                start_lat, start_lon,
                dest['latitude'], dest['longitude']
            )
            if dist <= max_distance_km:
                nearby_destinations.append(dest)
            else:
                print(f"DEBUG: Filtered out '{dest['name']}' - Too far ({dist:.1f}km)")
        
        print(f"DEBUG: Nearby destinations: {len(nearby_destinations)}")
        
        if not nearby_destinations:
            # Nếu không có địa điểm gần, mở rộng bán kính
            print(f"DEBUG: No nearby destinations, expanding radius to 100km")
            max_distance_km = 100
            for dest in valid_destinations:
                dist = DistanceCalculator.haversine_distance(
                    start_lat, start_lon,
                    dest['latitude'], dest['longitude']
                )
                if dist <= max_distance_km:
                    nearby_destinations.append(dest)
        
        if not nearby_destinations:
            return {
                'success': False,
                'message': f'Không có địa điểm nào trong bán kính {max_distance_km}km'
            }
        
        # 3. Tính điểm HYBRID (Content-Based + Collaborative Filtering)
        max_locations = min(user_profile.get('max_locations', 5), 6)  # Max 6 locations
        
        if use_cf and user_id:
            # Use hybrid scoring (CB + CF)
            print(f"DEBUG: Using HYBRID scoring (CB + CF) for user {user_id}")
            scored_destinations = ScoringEngine.rank_destinations_hybrid(
                user_profile,
                nearby_destinations,
                db=db,
                user_id=user_id,
                use_cf=True,
                top_n=max_locations
            )
            
            # Prepare destinations for routing with metadata
            routing_destinations = []
            for dest, score, metadata in scored_destinations:
                dest_copy = dest.copy()
                dest_copy['score'] = score
                dest_copy['scoring_metadata'] = metadata
                routing_destinations.append(dest_copy)
                
            scoring_method = 'hybrid'
        else:
            # Use content-based only (original)
            print(f"DEBUG: Using CONTENT-BASED scoring only")
            scored_destinations = ScoringEngine.rank_destinations(
                user_profile,
                nearby_destinations,
                top_n=max_locations
            )
            
            # Prepare destinations for routing
            routing_destinations = []
            for dest, score in scored_destinations:
                dest_copy = dest.copy()
                dest_copy['score'] = score
                dest_copy['scoring_metadata'] = {
                    'cb_score': round(score, 3),
                    'scoring_method': 'content_based'
                }
                routing_destinations.append(dest_copy)
                
            scoring_method = 'content_based'
        
        print(f"DEBUG: Scored destinations: {len(routing_destinations)}, Method: {scoring_method}")
        
        print(f"DEBUG: Routing destinations: {len(routing_destinations)}")
        
        # 5. Try OR-Tools optimizer first
        print(f"DEBUG: Attempting OR-Tools optimization...")
        optimizer = RouteOptimizer(routing_destinations, user_profile, start_location)
        result = optimizer.optimize()
        
        # 6. Fallback to heuristic if OR-Tools fails
        if not result.get('success'):
            print(f"DEBUG: OR-Tools failed, falling back to Heuristic optimizer...")
            heuristic_optimizer = HeuristicOptimizer(
                routing_destinations, 
                user_profile, 
                start_location
            )
            result = heuristic_optimizer.optimize_greedy()
            
            # Thêm note cho user biết đang dùng fallback
            if result.get('success'):
                result['note'] = 'Sử dụng thuật toán tối ưu đơn giản (Greedy). Lộ trình có thể chưa tối ưu nhất.'
        
        # Add CF metadata to result
        if result.get('success'):
            result['recommendation_metadata'] = {
                'scoring_method': scoring_method,
                'user_id': user_id,
                'cf_enabled': use_cf and user_id is not None,
                'total_destinations_considered': len(nearby_destinations),
                'scored_destinations': len(routing_destinations)
            }
        
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
