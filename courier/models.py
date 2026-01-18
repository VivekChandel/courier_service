
from dataclasses import dataclass

@dataclass
class Package:
    pkg_id: str
    weight: int
    distance: int
    offer_code: str
    discount_amount: float = 0.0
    total_cost: float = 0.0
    estimated_delivery_time: float = -1.0

    def __hash__(self) -> int:
        # Hash by ID to allow set/dict usage
        return hash(self.pkg_id)

@dataclass
class Vehicle:
    v_id: int
    max_speed: int
    max_weight: int
    available_at: float = 0.0  # time when vehicle returns to base

@dataclass
class OfferConfig:
    code: str
    discount_percentage: float
    min_distance: int
    max_distance: int
    min_weight: int
    max_weight: int
