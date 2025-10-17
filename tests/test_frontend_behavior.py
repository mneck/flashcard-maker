"""
Test frontend behavior for flashcards app.
This test verifies that example sentences and explanations are hidden until after clicking Check.
"""

import pytest
from playwright.sync_api import sync_playwright, Page, Browser
import os
import time


@pytest.fixture(scope="session")
def browser():
    """Start browser for frontend tests"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser):
    """Create a new page for each test"""
    page = browser.new_page()
    yield page
    page.close()


def test_example_sentence_hidden_until_check_clicked(page: Page):
    """
    Test that example sentences and explanations are hidden until user clicks Check.
    
    Steps:
    1. Navigate to frontend
    2. Verify no example sentence/explanation is visible initially
    3. Click Check button
    4. Verify example sentence/explanation becomes visible
    """
    # Navigate to frontend
    frontend_url = "http://localhost:3000"
    page.goto(frontend_url)
    
    # Wait for page to load
    page.wait_for_selector("input[placeholder*='Type']", timeout=10000)
    
    # Verify no example sentence is visible initially
    example_elements = page.query_selector_all("text=/Example:/")
    explained_elements = page.query_selector_all("text=/Explained:/")
    
    # Should not see any example or explained text initially
    assert len(example_elements) == 0, "Example sentence should be hidden initially"
    assert len(explained_elements) == 0, "Explained text should be hidden initially"
    
    # Type something in the input (doesn't matter if correct or not)
    input_field = page.query_selector("input[placeholder*='Type']")
    assert input_field is not None, "Input field should be present"
    input_field.fill("test answer")
    
    # Click Check button
    check_button = page.query_selector("button:has-text('Check')")
    assert check_button is not None, "Check button should be present"
    check_button.click()
    
    # Wait a moment for the response
    time.sleep(1)
    
    # Now example sentence and explanation should be visible
        
    # Verify example content is now visible in the detailed panel
    example_in_panel = page.query_selector("text=/Example:/")
    assert example_in_panel is not None, "Example should be visible in detailed panel after Check"
    
    # Verify Continue button appears
    continue_button = page.query_selector("button:has-text('Continue')")
    assert continue_button is not None, "Continue button should appear after clicking Check"


def test_continue_button_fetches_new_card(page: Page):
    """
    Test that Continue button fetches a new random card.
    
    Steps:
    1. Navigate to frontend
    2. Answer a question (correct or incorrect)
    3. Click Continue
    4. Verify a new card appears
    """
    # Navigate to frontend
    frontend_url = "http://localhost:3000"
    page.goto(frontend_url)
    
    # Wait for page to load
    page.wait_for_selector("input[placeholder*='Type']", timeout=10000)
    
    # Get the current card's English term
    current_card_element = page.query_selector("div[style*='fontSize: 64px']")
    if current_card_element is None:
        # Try alternative selector
        current_card_element = page.query_selector("div[style*='font-size: 64px']")
    assert current_card_element is not None, "Card should be displayed"
    current_english_term = current_card_element.text_content()
    
    # Type something and click Check
    input_field = page.query_selector("input[placeholder*='Type']")
    input_field.fill("test answer")
    
    check_button = page.query_selector("button:has-text('Check')")
    check_button.click()
    
    # Wait for response
    time.sleep(1)
    
    # Click Continue
    continue_button = page.query_selector("button:has-text('Continue')")
    assert continue_button is not None, "Continue button should be present"
    continue_button.click()
    
    # Wait for new card to load
    time.sleep(2)
    
    # Verify a new card appears (should be different from the previous one)
    new_card_element = page.query_selector("div[style*='fontSize: 64px']")
    if new_card_element is None:
        # Try alternative selector
        new_card_element = page.query_selector("div[style*='font-size: 64px']")
    assert new_card_element is not None, "New card should be displayed"
    new_english_term = new_card_element.text_content()
    
    # The new card should be different (with 135 terms, this should almost always be true)
    assert new_english_term != current_english_term, f"New card should be different. Old: {current_english_term}, New: {new_english_term}"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
