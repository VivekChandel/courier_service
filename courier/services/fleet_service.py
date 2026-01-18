from typing import List
from courier.models import Package, Vehicle
from courier.services.shipment_service import ShipmentService
from decimal import Decimal, ROUND_DOWN


def _trunc2(x: float) -> float:
    '''Truncate to 2 decimal places using Decimal(ROUND_DOWN) to avoid binary FP drift.'''
    d = Decimal(str(x))
    return float(d.quantize(Decimal('0.00'), rounding=ROUND_DOWN))


class FleetService:
    def __init__(self, vehicles: List[Vehicle]) -> None:
        # Deterministic order by id
        self.vehicles = sorted(vehicles, key=lambda v: v.v_id)

    def process_deliveries(self, packages: List[Package]) -> None:
        '''
        Assign packages to vehicles and compute delivery times.
        Each vehicle takes the best shipment available when it becomes free.
        Delivery time per package = vehicle.available_at + TRUNC(distance/speed, 2)
        Vehicle return time increment = 2 * TRUNC(max_distance_in_shipment/speed, 2)
        '''
        remaining = packages[:]
        while remaining:
            # pick next available vehicle (and lowest v_id if tie)
            self.vehicles.sort(key=lambda v: (v.available_at, v.v_id))
            v = self.vehicles[0]

            shipment = ShipmentService.get_best_shipment(remaining, v.max_weight)
            if not shipment:
                # No feasible shipment left; break to avoid infinite loop
                break

            # Compute times and update vehicle availability
            furthest = 0
            for pkg in shipment:
                one_way = _trunc2(pkg.distance / v.max_speed)
                from decimal import Decimal, ROUND_DOWN
                _a = Decimal(str(v.available_at)).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
                _b = Decimal(str(one_way)).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
                delivery_time = float((_a + _b).quantize(Decimal('0.00'), rounding=ROUND_DOWN))
                pkg.estimated_delivery_time = delivery_time
                furthest = max(furthest, pkg.distance)

            # Remove shipped packages from the pool
            shipped_ids = {p.pkg_id for p in shipment}
            remaining = [p for p in remaining if p.pkg_id not in shipped_ids]

            # Update vehicle availability using *truncated* one-way time for the furthest distance
            furthest_one_way = _trunc2(furthest / v.max_speed)
            round_trip = furthest_one_way * 2.0
            from decimal import Decimal, ROUND_DOWN
            _av = Decimal(str(v.available_at)).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
            _rt = Decimal(str(round_trip)).quantize(Decimal('0.00'), rounding=ROUND_DOWN)
            v.available_at = float((_av + _rt).quantize(Decimal('0.00'), rounding=ROUND_DOWN))
