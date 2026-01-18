
from abc import ABC, abstractmethod
from typing import Dict, List
from courier.models import Package, OfferConfig

class OfferStrategy(ABC):
    @abstractmethod
    def get_discount(self, package: Package) -> float:
        '''Return discount percentage (0..100) for a given package.'''
        raise NotImplementedError

class StandardOfferStrategy(OfferStrategy):
    def __init__(self, config: OfferConfig) -> None:
        self.config = config

    def get_discount(self, package: Package) -> float:
        dist_ok = self.config.min_distance <= package.distance <= self.config.max_distance
        wt_ok = self.config.min_weight <= package.weight <= self.config.max_weight
        return self.config.discount_percentage if (dist_ok and wt_ok) else 0.0

class CostService:
    def __init__(self, base_delivery_cost: int) -> None:
        self.base_cost = base_delivery_cost
        self.offers: Dict[str, OfferStrategy] = self._initialize_offers()

    def _initialize_offers(self) -> Dict[str, OfferStrategy]:
        # Could come from config/DB; hard-coded for the challenge
        configs: List[OfferConfig] = [
            OfferConfig("OFR001", 10, 0, 200, 70, 200),
            OfferConfig("OFR002", 7, 50, 150, 100, 250),
            OfferConfig("OFR003", 5, 50, 250, 10, 150),
        ]
        return {cfg.code: StandardOfferStrategy(cfg) for cfg in configs}

    def calculate_cost(self, package: Package) -> None:
        delivery_cost = self.base_cost + (package.weight * 10) + (package.distance * 5)
        discount_percent = 0.0
        strategy = self.offers.get(package.offer_code)
        if strategy:
            discount_percent = strategy.get_discount(package)
        discount_amount = (discount_percent / 100.0) * delivery_cost
        total_cost = delivery_cost - discount_amount
        package.discount_amount = discount_amount
        package.total_cost = total_cost
