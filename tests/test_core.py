"""Tests for Sortbot."""
from src.core import Sortbot
def test_init(): assert Sortbot().get_stats()["ops"] == 0
def test_op(): c = Sortbot(); c.process(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Sortbot(); [c.process() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Sortbot(); c.process(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Sortbot(); r = c.process(); assert r["service"] == "sortbot"
