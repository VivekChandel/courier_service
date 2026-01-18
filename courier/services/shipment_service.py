
from itertools import combinations
from typing import List
from courier.models import Package

class ShipmentService:
    @staticmethod
    def get_best_shipment(packages: List[Package], max_weight: int) -> List[Package]:
        '''
        Select the best subset of packages constrained by max_weight with the rules:
        1) Maximize number of packages.
        2) If tie, maximize total weight.
        3) If tie, minimize the furthest distance (i.e., smaller max distance first).
        '''
        if not packages:
            return []

        possible = []
        n = len(packages)
        for r in range(1, n + 1):
            for combo in combinations(packages, r):
                wt = sum(p.weight for p in combo)
                if wt <= max_weight:
                    possible.append(combo)

        if not possible:
            return []

        # Multi-criteria sort in one key; sort desc on first two, asc on third
        possible.sort(
            key=lambda combo: (
                len(combo),
                sum(p.weight for p in combo),
                -max(p.distance for p in combo),  # negative so reverse=True makes it ascending
            ),
            reverse=True,
        )
        return list(possible[0])
