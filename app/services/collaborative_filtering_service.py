"""
==============================================================================
COLLABORATIVE FILTERING SERVICE - Core recommendation engine
==============================================================================
Implements hybrid recommendation using:
- User-User Collaborative Filtering (k-Nearest Neighbors)
- Item-Item Collaborative Filtering
- Cold start handling with quiz-based seeding
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.models.destination_rating import DestinationRating
from app.models.visit_log import VisitLog
from app.models.user_favorite import UserFavorite
from app.models.destination import Destination
from app.models.user import User

logger = logging.getLogger(__name__)


class CollaborativeFilteringService:
    """
    Collaborative Filtering for tour recommendations
    Supports: User-User CF, Item-Item CF, and Hybrid
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.user_item_matrix = None
        self.user_similarity = None
        self.item_similarity = None
        self.user_ids = []
        self.dest_ids = []
        
    # ==========================================
    # PART 1: DATA PREPARATION
    # ==========================================
    
    def build_interaction_matrix(self) -> Tuple[np.ndarray, List[int], List[int]]:
        """
        Build User-Item interaction matrix from ratings, visits, and favorites
        
        Combines multiple signals:
        - Explicit ratings (weight = 1.0)
        - Implicit: visits (pseudo-rating based on frequency)
        - Implicit: favorites (pseudo-rating = 4.5)
        
        Returns:
            matrix: (n_users, n_items) numpy array
            user_ids: List of user IDs (row index mapping)
            dest_ids: List of destination IDs (column index mapping)
        """
        logger.info("Building user-item interaction matrix...")
        
        # Get all explicit ratings
        ratings = self.db.query(
            DestinationRating.user_id,
            DestinationRating.destination_id,
            DestinationRating.rating
        ).all()
        
        # Get implicit feedback: visits without ratings
        visits = self.db.query(
            VisitLog.user_id,
            VisitLog.destination_id,
            func.count(VisitLog.log_id).label('visit_count')
        ).filter(
            VisitLog.completed == True
        ).group_by(
            VisitLog.user_id,
            VisitLog.destination_id
        ).all()
        
        # Get favorites
        favorites = self.db.query(
            UserFavorite.user_id,
            UserFavorite.destination_id
        ).all()
        
        # Combine signals into interaction dictionary
        interaction_dict = {}
        
        # 1. Explicit ratings (highest priority)
        for user_id, dest_id, rating in ratings:
            key = (user_id, dest_id)
            interaction_dict[key] = float(rating)
        
        # 2. Implicit: visits (convert to pseudo-rating)
        for user_id, dest_id, visit_count in visits:
            key = (user_id, dest_id)
            if key not in interaction_dict:  # Only if no explicit rating
                # Visit frequency → pseudo-rating
                # 1 visit = 3.0, 2 visits = 3.5, 3+ visits = 4.0 (capped at 5.0)
                pseudo_rating = min(3.0 + (visit_count - 1) * 0.5, 5.0)
                interaction_dict[key] = pseudo_rating
        
        # 3. Implicit: favorites (pseudo-rating = 4.5)
        for user_id, dest_id in favorites:
            key = (user_id, dest_id)
            if key not in interaction_dict:
                interaction_dict[key] = 4.5
        
        if not interaction_dict:
            logger.warning("No interaction data found!")
            return np.array([]), [], []
        
        # Build matrix indices
        unique_users = sorted(set(k[0] for k in interaction_dict.keys()))
        unique_dests = sorted(set(k[1] for k in interaction_dict.keys()))
        
        user_idx_map = {uid: idx for idx, uid in enumerate(unique_users)}
        dest_idx_map = {did: idx for idx, did in enumerate(unique_dests)}
        
        # Initialize matrix
        n_users = len(unique_users)
        n_dests = len(unique_dests)
        matrix = np.zeros((n_users, n_dests))
        
        # Fill matrix
        for (user_id, dest_id), rating in interaction_dict.items():
            i = user_idx_map[user_id]
            j = dest_idx_map[dest_id]
            matrix[i, j] = rating
        
        density = np.count_nonzero(matrix) / (n_users * n_dests) if n_users * n_dests > 0 else 0
        logger.info(f"Matrix built: {n_users} users × {n_dests} destinations, density: {density:.2%}")
        
        return matrix, unique_users, unique_dests
    
    # ==========================================
    # PART 2: USER-USER COLLABORATIVE FILTERING
    # ==========================================
    
    def compute_user_similarity(self, matrix: np.ndarray) -> np.ndarray:
        """
        Compute user-user similarity using cosine similarity
        
        Similarity = cos(θ) = (A · B) / (||A|| ||B||)
        
        Args:
            matrix: (n_users, n_items) interaction matrix
            
        Returns:
            similarity: (n_users, n_users) similarity matrix
        """
        logger.info("Computing user-user similarity matrix...")
        
        # Use sparse matrix for efficiency
        sparse_matrix = csr_matrix(matrix)
        similarity = cosine_similarity(sparse_matrix)
        
        # Set diagonal to 0 (user shouldn't be similar to themselves)
        np.fill_diagonal(similarity, 0)
        
        logger.info(f"User similarity matrix computed: {similarity.shape}")
        return similarity
    
    def predict_user_based(
        self,
        user_id: int,
        destination_id: int,
        matrix: np.ndarray,
        user_ids: List[int],
        dest_ids: List[int],
        k: int = 20
    ) -> Optional[float]:
        """
        Predict rating using User-User CF (k-Nearest Neighbors)
        
        Formula:
        r̂(u,i) = Σ(sim(u,v) × r(v,i)) / Σ|sim(u,v)|
        where v ∈ top-k similar users who rated item i
        
        Args:
            user_id: Target user ID
            destination_id: Target destination ID
            matrix: User-Item matrix
            user_ids: List mapping row index → user_id
            dest_ids: List mapping col index → dest_id
            k: Number of similar users to consider
            
        Returns:
            Predicted rating (1-5) or None if can't predict
        """
        try:
            user_idx = user_ids.index(user_id)
            dest_idx = dest_ids.index(destination_id)
        except ValueError:
            # User or destination not in training data
            return None
        
        # If user already rated, return actual rating
        actual_rating = matrix[user_idx, dest_idx]
        if actual_rating > 0:
            return actual_rating
        
        # Compute similarity if not cached
        if self.user_similarity is None:
            self.user_similarity = self.compute_user_similarity(matrix)
        
        # Get similarities for target user
        similarities = self.user_similarity[user_idx]
        
        # Find k most similar users
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        # Weighted average of similar users' ratings
        numerator = 0.0
        denominator = 0.0
        
        for similar_user_idx in top_k_indices:
            rating = matrix[similar_user_idx, dest_idx]
            if rating > 0:  # Only consider users who rated this destination
                sim_score = similarities[similar_user_idx]
                numerator += sim_score * rating
                denominator += abs(sim_score)
        
        if denominator == 0:
            return None  # No similar users rated this destination
        
        predicted_rating = numerator / denominator
        return np.clip(predicted_rating, 1.0, 5.0)
    
    # ==========================================
    # PART 3: ITEM-ITEM COLLABORATIVE FILTERING
    # ==========================================
    
    def compute_item_similarity(self, matrix: np.ndarray) -> np.ndarray:
        """
        Compute item-item similarity (destinations)
        
        "Destinations that are rated similarly by users are similar"
        """
        logger.info("Computing item-item similarity matrix...")
        
        # Transpose for item-item
        sparse_matrix = csr_matrix(matrix.T)
        similarity = cosine_similarity(sparse_matrix)
        
        np.fill_diagonal(similarity, 0)
        
        logger.info(f"Item similarity matrix computed: {similarity.shape}")
        return similarity
    
    def predict_item_based(
        self,
        user_id: int,
        destination_id: int,
        matrix: np.ndarray,
        user_ids: List[int],
        dest_ids: List[int],
        k: int = 20
    ) -> Optional[float]:
        """
        Predict rating using Item-Item CF
        
        Formula:
        r̂(u,i) = Σ(sim(i,j) × r(u,j)) / Σ|sim(i,j)|
        where j ∈ top-k similar items rated by user u
        
        Logic: "Users who liked destination A also liked B"
        """
        try:
            user_idx = user_ids.index(user_id)
            dest_idx = dest_ids.index(destination_id)
        except ValueError:
            return None
        
        # Check if already rated
        actual_rating = matrix[user_idx, dest_idx]
        if actual_rating > 0:
            return actual_rating
        
        # Compute item similarity if not cached
        if self.item_similarity is None:
            self.item_similarity = self.compute_item_similarity(matrix)
        
        # Get similarities for target destination
        similarities = self.item_similarity[dest_idx]
        
        # Find k most similar destinations
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        
        # Weighted average of user's ratings on similar destinations
        numerator = 0.0
        denominator = 0.0
        
        for similar_dest_idx in top_k_indices:
            rating = matrix[user_idx, similar_dest_idx]
            if rating > 0:
                sim_score = similarities[similar_dest_idx]
                numerator += sim_score * rating
                denominator += abs(sim_score)
        
        if denominator == 0:
            return None
        
        predicted_rating = numerator / denominator
        return np.clip(predicted_rating, 1.0, 5.0)
    
    # ==========================================
    # PART 4: HYBRID PREDICTION
    # ==========================================
    
    def predict_rating(
        self,
        user_id: int,
        destination_id: int,
        method: str = 'hybrid'
    ) -> Dict[str, any]:
        """
        Predict rating with specified method
        
        Args:
            user_id: User ID
            destination_id: Destination ID
            method: 'user_based', 'item_based', or 'hybrid'
            
        Returns:
            {
                'predicted_rating': float (1-5),
                'confidence': float (0-1),
                'method_used': str
            }
        """
        # Build matrix if not cached
        if self.user_item_matrix is None:
            matrix, user_ids, dest_ids = self.build_interaction_matrix()
            if len(user_ids) == 0:
                # No data available
                return {
                    'predicted_rating': 3.0,
                    'confidence': 0.0,
                    'method_used': 'no_data'
                }
            self.user_item_matrix = matrix
            self.user_ids = user_ids
            self.dest_ids = dest_ids
        else:
            matrix = self.user_item_matrix
            user_ids = self.user_ids
            dest_ids = self.dest_ids
        
        if method == 'user_based':
            pred = self.predict_user_based(user_id, destination_id, matrix, user_ids, dest_ids)
            return {
                'predicted_rating': pred if pred else 3.0,
                'confidence': 0.7 if pred else 0.3,
                'method_used': 'user_based'
            }
        
        elif method == 'item_based':
            pred = self.predict_item_based(user_id, destination_id, matrix, user_ids, dest_ids)
            return {
                'predicted_rating': pred if pred else 3.0,
                'confidence': 0.7 if pred else 0.3,
                'method_used': 'item_based'
            }
        
        else:  # hybrid
            user_pred = self.predict_user_based(user_id, destination_id, matrix, user_ids, dest_ids)
            item_pred = self.predict_item_based(user_id, destination_id, matrix, user_ids, dest_ids)
            
            if user_pred and item_pred:
                # Both available → weighted average
                final_pred = 0.5 * user_pred + 0.5 * item_pred
                confidence = 0.9
                method_used = 'hybrid'
            elif user_pred:
                final_pred = user_pred
                confidence = 0.6
                method_used = 'user_based'
            elif item_pred:
                final_pred = item_pred
                confidence = 0.6
                method_used = 'item_based'
            else:
                # Fallback: use destination average
                dest = self.db.query(Destination).filter(
                    Destination.destination_id == destination_id
                ).first()
                
                if dest and dest.avg_rating and dest.avg_rating > 0:
                    final_pred = float(dest.avg_rating)
                    confidence = 0.3
                    method_used = 'baseline_avg'
                else:
                    final_pred = 3.0  # Global default
                    confidence = 0.1
                    method_used = 'baseline_default'
            
            return {
                'predicted_rating': float(final_pred),
                'confidence': confidence,
                'method_used': method_used
            }
    
    # ==========================================
    # PART 5: BATCH RECOMMENDATIONS
    # ==========================================
    
    def get_cf_scores_for_destinations(
        self,
        user_id: int,
        destination_ids: List[int]
    ) -> Dict[int, Dict]:
        """
        Get CF scores for multiple destinations (for integration with tour optimizer)
        
        Args:
            user_id: User ID
            destination_ids: List of destination IDs to score
            
        Returns:
            {
                dest_id: {
                    'cf_score': float (0-1),  # Normalized to [0,1]
                    'predicted_rating': float (1-5),
                    'confidence': float (0-1),
                    'method': str
                }
            }
        """
        results = {}
        
        for dest_id in destination_ids:
            prediction = self.predict_rating(user_id, dest_id, method='hybrid')
            
            # Normalize rating from [1,5] to [0,1] for integration
            cf_score = (prediction['predicted_rating'] - 1) / 4.0
            
            results[dest_id] = {
                'cf_score': cf_score,
                'predicted_rating': prediction['predicted_rating'],
                'confidence': prediction['confidence'],
                'method': prediction['method_used']
            }
        
        return results
    
    # ==========================================
    # PART 6: USER ACTIVITY LEVEL
    # ==========================================
    
    def get_user_activity_level(self, user_id: int) -> Dict[str, any]:
        """
        Get user's activity level to determine CF weight
        
        Returns:
            {
                'rating_count': int,
                'visit_count': int,
                'favorite_count': int,
                'activity_level': str,  # 'cold', 'warm', 'hot'
                'recommended_cf_weight': float  # 0.0-1.0
            }
        """
        rating_count = self.db.query(DestinationRating).filter(
            DestinationRating.user_id == user_id
        ).count()
        
        visit_count = self.db.query(VisitLog).filter(
            VisitLog.user_id == user_id,
            VisitLog.completed == True
        ).count()
        
        favorite_count = self.db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id
        ).count()
        
        total_interactions = rating_count + visit_count + favorite_count
        
        # Determine activity level
        if total_interactions == 0:
            activity_level = 'cold'
            cf_weight = 0.2  # 20% CF, 80% content-based
        elif total_interactions < 5:
            activity_level = 'warm'
            cf_weight = 0.5  # 50% CF, 50% content-based
        else:
            activity_level = 'hot'
            cf_weight = 0.7  # 70% CF, 30% content-based
        
        return {
            'rating_count': rating_count,
            'visit_count': visit_count,
            'favorite_count': favorite_count,
            'total_interactions': total_interactions,
            'activity_level': activity_level,
            'recommended_cf_weight': cf_weight
        }
