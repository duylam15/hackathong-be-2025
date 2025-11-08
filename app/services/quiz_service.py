from typing import List, Dict, Tuple
from app.schemas.quiz import QuizResult, Answer

# Hardcoded questions based on Plog's Model (10 questions, 3 layers)
QUESTIONS = [
    # Layer 1: Motivation (3 questions)
    {"id": 1, "question": "Điều gì thúc đẩy bạn đi du lịch nhất?", "options": [
        "A: Khám phá nơi mới lạ, chưa ai biết", "B: Học hỏi văn hóa, lịch sử",
        "C: Thời gian chất lượng với gia đình", "D: Nghỉ ngơi, tránh stress hàng ngày"
    ], "layer": 1, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
    {"id": 2, "question": "Kỳ nghỉ lý tưởng của bạn là?", "options": [
        "A: Ngắn, đầy thử thách địa hình", "B: Trung bình, tập trung trải nghiệm địa phương",
        "C: Linh hoạt, phù hợp lịch gia đình", "D: Dài ngày, thư giãn quen thuộc"
    ], "layer": 1, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
    {"id": 3, "question": "Bạn mong đợi cảm xúc gì từ chuyến đi?", "options": [
        "A: Adrenaline, phấn khích rủi ro", "B: Khám phá sâu sắc, kiến thức mới",
        "C: Kết nối, an toàn nhóm", "D: Bình yên, không lo lắng"
    ], "layer": 1, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
    
    # Layer 2: Attitudes (4 questions)
    {"id": 4, "question": "Bạn thích điểm đến như thế nào?", "options": [
        "A: Off-beaten path, hoang dã", "B: Địa phương độc đáo, ít du lịch",
        "C: Nổi tiếng, tiện nghi gia đình", "D: Quen thuộc, gần nhà"
    ], "layer": 2, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
    {"id": 5, "question": "Với phương tiện di chuyển?", "options": [
        "A: Phiêu lưu (xe máy, off-road)", "B: Linh hoạt, địa phương",
        "C: An toàn, tour nhóm", "D: Tiết kiệm, công cộng"
    ], "layer": 2, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
    {"id": 6, "question": "Ưu tiên ăn uống/hoạt động?", "options": [
        "A: Thử thách ẩm thực đường phố", "B: Tour văn hóa ẩm thực",
        "C: Món quen thuộc cho mọi người", "D: Ăn tại resort thoải mái"
    ], "layer": 2, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
    {"id": 7, "question": "Ngân sách & rủi ro?", "options": [
        "A: Linh hoạt cho trải nghiệm độc", "B: Trung bình, giá trị văn hóa",
        "C: Phải chăng, an toàn", "D: Tối thiểu, tránh phát sinh"
    ], "layer": 2, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
    
    # Layer 3: Preferences (3 questions)
    {"id": 8, "question": "Đi với ai & phong cách?", "options": [
        "A: Một mình/nhóm bạn mạo hiểm", "B: Cặp đôi khám phá",
        "C: Gia đình, hoạt động chung", "D: Nhóm quen, nghỉ dưỡng"
    ], "layer": 3, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
    {"id": 9, "question": "Thời tiết & mùa?", "options": [
        "A: Bất kỳ, kể cả thử thách", "B: Mùa lễ hội văn hóa",
        "C: Thời gian gia đình tiện", "D: Mùa thoải mái, dự đoán được"
    ], "layer": 3, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
    {"id": 10, "question": "Yếu tố quyết định tour?", "options": [
        "A: Độ mới mẻ, độc đáo", "B: Giá trị văn hóa sâu",
        "C: An toàn, dễ dàng", "D: Tiết kiệm, quen thuộc"
    ], "layer": 3, "novelty_map": {"A": 1.0, "B": 0.5, "C": 0.0, "D": 0.0}},
]

# Suggested tours by type (hardcoded; integrate with destination_service later)
SUGGESTED_TOURS = {
    "Adventure Seeker": [
        {"name": "Trekking Sapa", "description": "Leo núi hoang dã", "price": "15M VND"},
        {"name": "Lặn biển Phú Quốc", "description": "Khám phá đại dương", "price": "12M VND"}
    ],
    "Cultural Explorer": [
        {"name": "Tour Huế cổ kính", "description": "Lịch sử và lễ hội", "price": "10M VND"},
        {"name": "Chợ nổi Mekong", "description": "Văn hóa sông nước", "price": "8M VND"}
    ],
    "Family-Friendly": [
        {"name": "Vịnh Hạ Long gia đình", "description": "An toàn cho trẻ em", "price": "11M VND"},
        {"name": "Sun World giải trí", "description": "Hoạt động nhóm", "price": "9M VND"}
    ],
    "Relaxation Lover": [
        {"name": "Resort Nha Trang", "description": "Spa và bãi biển", "price": "14M VND"},
        {"name": "Du thuyền Hạ Long", "description": "Thư giãn sang trọng", "price": "13M VND"}
    ],
    "Budget Traveler": [
        {"name": "Backpacker Hội An", "description": "Homestay tiết kiệm", "price": "5M VND"},
        {"name": "Xe buýt miền Trung", "description": "Di chuyển rẻ", "price": "4M VND"}
    ]
}

def get_questions() -> Dict:
    """GET: Return quiz questions grouped by layer."""
    questions_by_layer = {}
    for q in QUESTIONS:
        layer = q["layer"]
        if layer not in questions_by_layer:
            questions_by_layer[layer] = []
        questions_by_layer[layer].append({
            "id": q["id"],
            "question": q["question"],
            "options": q["options"]
        })
    return {"layers": questions_by_layer}

def classify_user(answers: List[Answer]) -> QuizResult:
    """POST: Calculate novelty score and classify user."""
    num_answers = len(answers)
    if num_answers == 0:
        raise ValueError("No answers provided")
    novelty_score = 0.0
    for answer in answers:
        q_id = answer.question_id
        choice = answer.choice.upper()  # Normalize to A/B/C/D
        
        # Find question
        question = next((q for q in QUESTIONS if q["id"] == q_id), None)
        if not question:
            raise ValueError(f"Invalid question_id: {q_id}")
        
        # Add novelty points
        novelty_score += question["novelty_map"].get(choice, 0.0)
        
    scaled_novelty = (novelty_score / num_answers) * 10 if num_answers < 10 else novelty_score
    # Classify based on score (0-10)
    if scaled_novelty > 7:
        user_type = "Adventure Seeker"
    elif 5 <= scaled_novelty <= 7:
        user_type = "Cultural Explorer"  # Can add sub-logic for Family if needed
    elif 3 < scaled_novelty < 5:
        user_type = "Family-Friendly"
    elif 1 <= scaled_novelty <= 3:
        user_type = "Relaxation Lover"
    else:
        user_type = "Budget Traveler"
    
    # Description based on Plog's Model
    descriptions = {
        "Adventure Seeker": "Bạn là Allocentric: Thích rủi ro và khám phá mới mẻ (Plog, 1974).",
        "Cultural Explorer": "Bạn là Near-Allocentric: Tìm kiếm văn hóa sâu sắc.",
        "Family-Friendly": "Bạn là Midcentric: Cân bằng an toàn và nhóm.",
        "Relaxation Lover": "Bạn là Near-Psychocentric: Ưu tiên thư giãn quen thuộc.",
        "Budget Traveler": "Bạn là Psychocentric: Tiết kiệm và routine-oriented."
    }
    
    suggested = SUGGESTED_TOURS.get(user_type, [])
    
    return QuizResult(
        user_type=user_type,
        novelty_score=round(scaled_novelty, 1),
        description=descriptions.get(user_type, ""),
        suggested_tours=suggested
    )