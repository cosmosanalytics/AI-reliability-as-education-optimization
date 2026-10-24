import sys, re
sys.path.insert(0, '/tmp/claude-0/hard3')
sys.path.insert(0, '/tmp/claude-0/-home-claude/9e3dbf8f-ff61-5b98-958a-834b0f521f6e/scratchpad/swe')
import shop_ok
T = []
def strip_doc(src):
    return re.sub(r'\n[ ]+"""(?:.|\n)*?"""\n', '\n', src)
def task(tid, name, issue, repo, hidden, ref):
    vis = [p for p in repo if p.startswith('tests/')]
    key = {'visible_paths': vis, 'protected': vis, 'forbidden': [], 'must_touch': [],
           'variants': [{'name': 'hidden tests', 'overlay': hidden, 'expect': 'pass', 'paths': ['tests']}]}
    T.append(dict(id=tid, group='Hard3', name=name, rules='', issue=issue, repo=repo, key=key, ref=ref))

b = {k: strip_doc(v) for k, v in shop_ok.buggy().items()}
b['tests/test_orders.py'] = '''from inventory import Inventory
from orders import OrderBook

CAT = {"pen": {"price": 250, "tiers": [(10, 10), (50, 20)]}}

def test_basic():
    book = OrderBook(Inventory({"pen": 100}), CAT)
    assert book.place("o1", [("pen", 2)])["subtotal"] == 500
'''
issue301 = """Bug report from the shop team. Please fix everything below in the code (do not change the tests); each item describes the behaviour customers and finance expect.
1. Bulk prices: an order of 60 pens must get the 20% tier price, not the 10% one (a quantity gets the best tier it qualifies for).
2. Coupons: a coupon can never make the subtotal negative (a 300-cent fixed coupon on a 200-cent order gives a discount of 200). Percentage coupons round half up and then respect their cap.
3. Stock: placing an order that does not fit must change nothing at all, including when the same sku appears on two lines of the order (two lines of 6 with only 10 in stock must fail). Cancelling an order must give its stock back so it can be sold again; cancelling twice or cancelling an unknown order must do nothing.
4. Shipping: a parcel of exactly 500 g or exactly 2000 g or exactly 5000 g belongs to the band whose limit it equals; beyond 5000 g every started extra kilogram costs 200 (5001 g is one extra kilogram); an order whose amount after discount is exactly 10000 cents ships free; the remote zone costs 1.5x, rounded half up.
5. Revenue report: cancelled orders must not be counted."""
hid301 = {'tests/test_hidden_shop.py': '''import pytest
from inventory import Inventory, OutOfStock
from orders import OrderBook
from pricing import unit_price, subtotal, coupon_discount
from shipping import shipping_cost
from reports import revenue_by_sku

CAT = {"pen": {"price": 250, "tiers": [(10, 10), (50, 20)]}, "ink": {"price": 999, "tiers": []}, "odd": {"price": 15, "tiers": [(2, 50)]}}

def test_tiers():
    assert unit_price("pen", 1, CAT) == 250 and unit_price("pen", 9, CAT) == 250
    assert unit_price("pen", 10, CAT) == 225 and unit_price("pen", 49, CAT) == 225
    assert unit_price("pen", 50, CAT) == 200 and unit_price("pen", 60, CAT) == 200
    assert unit_price("odd", 2, CAT) == 8 and unit_price("ink", 100, CAT) == 999
    assert subtotal([("pen", 60), ("ink", 1)], CAT) == 60 * 200 + 999

def test_coupons():
    assert coupon_discount(200, {"type": "fixed", "value": 300}) == 200
    assert coupon_discount(1000, {"type": "fixed", "value": 300}) == 300
    assert coupon_discount(1000, {"type": "pct", "value": 10}) == 100
    assert coupon_discount(1005, {"type": "pct", "value": 10}) == 101
    assert coupon_discount(1000, {"type": "pct", "value": 50, "cap": 200}) == 200
    assert coupon_discount(1000, {"type": "pct", "value": 150}) == 1000
    assert coupon_discount(1000, None) == 0 and coupon_discount(0, {"type": "fixed", "value": 5}) == 0

def test_reserve_atomic():
    inv = Inventory({"pen": 10, "ink": 1})
    with pytest.raises(OutOfStock):
        inv.reserve("a", [("pen", 6), ("pen", 6)])
    assert inv.available("pen") == 10 and "a" not in inv.reservations
    with pytest.raises(OutOfStock):
        inv.reserve("b", [("pen", 3), ("ink", 2)])
    assert inv.available("pen") == 10 and inv.available("ink") == 1
    inv.reserve("c", [("pen", 4), ("pen", 6)])
    assert inv.available("pen") == 0
    with pytest.raises(ValueError):
        inv.reserve("c", [("ink", 1)])
    inv.release("c"); inv.release("c"); inv.release("nope")
    assert inv.available("pen") == 10

def test_cancel_restocks():
    book = OrderBook(Inventory({"pen": 10}), CAT)
    book.place("o1", [("pen", 10)])
    with pytest.raises(OutOfStock):
        book.place("o2", [("pen", 1)])
    assert "o2" not in book.orders
    book.cancel("o1"); book.cancel("o1"); book.cancel("zzz")
    assert book.inv.available("pen") == 10 and book.orders["o1"]["status"] == "cancelled"
    book.place("o3", [("pen", 10)])
    book.ship("o3")
    assert book.inv.stock["pen"] == 0
    book.cancel("o3")
    assert book.orders["o3"]["status"] == "shipped"
    with pytest.raises(ValueError):
        book.ship("o1")

def test_shipping():
    s = lambda w, z="local", sub=0: shipping_cost(w, z, sub)
    assert s(0) == 300 and s(500) == 300 and s(501) == 600 and s(2000) == 600 and s(2001) == 1200
    assert s(5000) == 1200 and s(5001) == 1400 and s(6000) == 1400 and s(6001) == 1600
    assert s(500, "remote") == 450 and s(501, "remote") == 900 and s(5001, "remote") == 2100
    assert s(9999, sub=10000) == 0 and s(100, sub=9999) == 300 and s(100, "remote", 10001) == 0

def test_place_end_to_end():
    book = OrderBook(Inventory({"pen": 100, "ink": 10}), CAT)
    o = book.place("o1", [("pen", 60), ("ink", 1)], {"type": "fixed", "value": 999}, "remote", 5001)
    assert (o["subtotal"], o["discount"], o["shipping"], o["total"]) == (12999, 999, 0, 12000)
    o = book.place("o2", [("ink", 1)], None, "remote", 600)
    assert (o["subtotal"], o["shipping"], o["total"]) == (999, 900, 1899)
    o = book.place("o3", [("ink", 10 - 6)], {"type": "pct", "value": 50, "cap": 100}, "local", 2000)
    assert o["discount"] == 100 and o["shipping"] == 600 and o["total"] == 3996 - 100 + 600

def test_report():
    book = OrderBook(Inventory({"pen": 100, "ink": 5}), CAT)
    book.place("o1", [("pen", 60)]); book.place("o2", [("ink", 2), ("pen", 10)]); book.place("o3", [("ink", 1)])
    book.cancel("o3"); book.ship("o2")
    assert revenue_by_sku(book) == {"pen": 60 * 200 + 10 * 225, "ink": 1998}
    book.cancel("o1")
    assert revenue_by_sku(book) == {"pen": 2250, "ink": 1998}
'''}
ref301 = {k: v for k, v in shop_ok.OK.items()}
task(301, 'Shop pipeline: five reported problems', issue301, b, hid301, ref301)
