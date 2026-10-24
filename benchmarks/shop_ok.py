OK = {}
OK['utils.py'] = '''from decimal import Decimal, ROUND_HALF_UP


def round_half_up(x):
    """Round a number to an integer, halves away from zero for positives."""
    return int(Decimal(str(x)).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def clamp(x, lo, hi):
    return max(lo, min(hi, x))
'''
OK['pricing.py'] = '''from utils import round_half_up, clamp


def unit_price(sku, qty, catalog):
    """Per-unit price in cents after quantity tiers. catalog[sku] = {"price": cents, "tiers": [(min_qty, pct_off), ...]}."""
    item = catalog[sku]
    best = 0
    for min_qty, pct in item.get("tiers", []):
        if qty >= min_qty and pct > best:
            best = pct
    return round_half_up(item["price"] * (100 - best) / 100)


def subtotal(lines, catalog):
    """lines: list of (sku, qty). Total cents."""
    return sum(unit_price(s, q, catalog) * q for s, q in lines)


def coupon_discount(sub, coupon):
    """coupon: None, {"type": "pct", "value": 10, "cap": 500 (optional)} or {"type": "fixed", "value": 300}.
    Never more than the subtotal; pct discounts are rounded half up before the cap is applied."""
    if not coupon:
        return 0
    if coupon["type"] == "pct":
        d = round_half_up(sub * coupon["value"] / 100)
        if "cap" in coupon:
            d = min(d, coupon["cap"])
    else:
        d = coupon["value"]
    return clamp(d, 0, sub)
'''
OK['inventory.py'] = '''class OutOfStock(Exception):
    pass


class Inventory:
    def __init__(self, stock):
        self.stock = dict(stock)
        self.reservations = {}

    def reserved(self, sku):
        return sum(q for lines in self.reservations.values() for s, q in lines if s == sku)

    def available(self, sku):
        return self.stock.get(sku, 0) - self.reserved(sku)

    def reserve(self, order_id, lines):
        """All-or-nothing. Raises OutOfStock (and changes nothing) if any sku lacks availability, counting repeated skus
        in `lines` together. Reserving an order_id twice raises ValueError."""
        if order_id in self.reservations:
            raise ValueError("duplicate order")
        need = {}
        for s, q in lines:
            need[s] = need.get(s, 0) + q
        for s, q in need.items():
            if self.available(s) < q:
                raise OutOfStock(s)
        self.reservations[order_id] = list(lines)

    def release(self, order_id):
        """Drop a reservation; unknown or already released ids are a no-op."""
        self.reservations.pop(order_id, None)

    def commit(self, order_id):
        """Turn a reservation into a real stock decrease."""
        for s, q in self.reservations.pop(order_id):
            self.stock[s] -= q
'''
OK['shipping.py'] = '''from utils import round_half_up

BANDS = [(500, 300), (2000, 600), (5000, 1200)]
FREE_AT = 10000
ZONES = {"local": 1.0, "remote": 1.5}


def shipping_cost(weight_g, zone, sub):
    """Cents. Free when the subtotal is at least FREE_AT. Otherwise the first band whose limit is >= weight applies (a parcel of
    exactly 500 g is in the first band); above 5000 g it is 1200 plus 200 for every started extra kilogram. The zone multiplier
    is applied last and rounded half up."""
    if sub >= FREE_AT:
        return 0
    base = None
    for limit, cost in BANDS:
        if weight_g <= limit:
            base = cost
            break
    if base is None:
        extra = -(-(weight_g - 5000) // 1000)
        base = 1200 + 200 * extra
    return round_half_up(base * ZONES[zone])
'''
OK['orders.py'] = '''from inventory import OutOfStock
from pricing import subtotal, coupon_discount
from shipping import shipping_cost


class OrderBook:
    def __init__(self, inventory, catalog):
        self.inv = inventory
        self.catalog = catalog
        self.orders = {}

    def place(self, order_id, lines, coupon=None, zone="local", weight_g=0):
        """Reserve stock and price the order. On OutOfStock nothing is recorded and no stock stays reserved."""
        self.inv.reserve(order_id, lines)
        sub = subtotal(lines, self.catalog)
        disc = coupon_discount(sub, coupon)
        ship = shipping_cost(weight_g, zone, sub - disc)
        o = {"id": order_id, "lines": list(lines), "subtotal": sub, "discount": disc, "shipping": ship,
             "total": sub - disc + ship, "status": "placed"}
        self.orders[order_id] = o
        return o

    def cancel(self, order_id):
        """Cancel a placed order and give its stock back. Cancelling twice or an unknown id is a no-op."""
        o = self.orders.get(order_id)
        if o is None or o["status"] != "placed":
            return
        self.inv.release(order_id)
        o["status"] = "cancelled"

    def ship(self, order_id):
        o = self.orders[order_id]
        if o["status"] != "placed":
            raise ValueError("not shippable")
        self.inv.commit(order_id)
        o["status"] = "shipped"
'''
OK['reports.py'] = '''from pricing import unit_price


def revenue_by_sku(book):
    """Net line revenue in cents per sku for orders that are placed or shipped (not cancelled)."""
    out = {}
    for o in book.orders.values():
        if o["status"] == "cancelled":
            continue
        for s, q in o["lines"]:
            out[s] = out.get(s, 0) + unit_price(s, q, book.catalog) * q
    return out
'''
BUG = {
 'pricing.py': [("if qty >= min_qty and pct > best:\n            best = pct", "if qty >= min_qty:\n            best = pct"),
                ("return clamp(d, 0, sub)", "return d")],
 'inventory.py': [("        for s, q in need.items():\n            if self.available(s) < q:\n                raise OutOfStock(s)\n        self.reservations[order_id] = list(lines)",
                   "        for s, q in lines:\n            if self.available(s) < q:\n                raise OutOfStock(s)\n        self.reservations[order_id] = list(lines)")],
 'shipping.py': [("if sub >= FREE_AT:", "if sub > FREE_AT:"), ("if weight_g <= limit:", "if weight_g < limit:"),
                 ("extra = -(-(weight_g - 5000) // 1000)", "extra = (weight_g - 5000) // 1000")],
 'orders.py': [("        self.inv.release(order_id)\n        o[\"status\"] = \"cancelled\"", "        o[\"status\"] = \"cancelled\"")],
 'reports.py': [("        if o[\"status\"] == \"cancelled\":\n            continue\n", "")],
}
def buggy():
    r = dict(OK)
    for f, subs in BUG.items():
        for a, b in subs:
            assert a in r[f], (f, a)
            r[f] = r[f].replace(a, b)
    return r
