import pytest
import time
from unittest.mock import MagicMock
from main_JF import random_sleep, random_mouse_action

def test_random_sleep():
    start_time = time.time()
    random_sleep()
    end_time = time.time()
    assert 0.5 <= (end_time - start_time) <= 3  

def test_random_mouse_action():
    driver_mock = MagicMock()
    random_mouse_action(driver_mock)  
    driver_mock.execute_script.assert_called()
