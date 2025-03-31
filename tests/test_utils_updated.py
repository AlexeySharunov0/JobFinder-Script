import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import time
from unittest.mock import MagicMock, patch
from main_JF import random_sleep, random_mouse_action, calculate_similarity, find_user_skills_in_description, start_automation, parsing_for_all_jobs, create_database, save_to_database

def test_random_sleep():
    with patch('time.sleep', return_value=None) as mock_sleep:
        random_sleep(1, 2)
        mock_sleep.assert_called_once()

def test_random_mouse_action():
    driver_mock = MagicMock()
    element_mock = MagicMock()
    random_mouse_action(driver_mock, element_mock)
    element_mock.click.assert_called_once()  # Assuming click is one of the actions

def test_calculate_similarity():
    user_skills = "Python, Java"
    description = "Looking for a Python developer"
    similarity = calculate_similarity(user_skills, description)
    assert similarity >= 0  # Similarity should be a non-negative value

def test_find_user_skills_in_description():
    user_skills = "Python, Java"
    description = "We need a Python developer"
    found_skills = find_user_skills_in_description(user_skills, description)
    assert "python" in [skill.lower() for skill in found_skills]

@patch('main_JF.webdriver.Chrome')
@patch('main_JF.create_database')
def test_start_automation(create_database_mock, webdriver_mock):
    login = "test@gmail.com"
    password = "password"
    parameters = "developer"
    start_page = 1
    end_page = 1
    user_skills = "Python"
    
    # Mock the webdriver and its methods
    driver_mock = MagicMock()
    webdriver_mock.return_value = driver_mock
    
    # Call the function
    job_titles, job_links, job_descriptions, job_matching_percentage = start_automation(login, password, parameters, start_page, end_page, user_skills)
    
    # Assertions can be added based on expected outcomes
    assert isinstance(job_titles, list)

@patch('main_JF.sqlite3.connect')
def test_save_to_database(connect_mock):
    job_titles = ["Job1"]
    job_links = ["http://example.com/job1"]
    job_descriptions = ["Description of Job1"]
    job_matching_percentage = [90.0]
    
    save_to_database(job_titles, job_links, job_descriptions, job_matching_percentage)
    connect_mock.assert_called_once()

def test_create_database():
    create_database()  # Just call the function to ensure it runs without error

# Additional tests for tkinter_part and on_submit can be added as needed

if __name__ == "__main__":
    pytest.main()
