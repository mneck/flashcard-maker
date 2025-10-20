import pytest
from playwright.sync_api import sync_playwright


def test_arabic_text_audit():
    """Simple audit to find any Arabic text that doesn't use arabic-font class."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        try:
            # Navigate to the frontend
            page.goto('http://localhost:3000')
            
            # Wait for the page to load
            page.wait_for_selector('input[placeholder*="Type"]', timeout=10000)
            
            # Get all elements on the page
            all_elements = page.query_selector_all('*')
            
            arabic_text_issues = []
            
            for element in all_elements:
                text = element.text_content()
                
                # Check if element contains Arabic characters
                if text and any('\u0600' <= char <= '\u06FF' for char in text):
                    # Get element info
                    tag = element.tag_name
                    class_attr = element.get_attribute('class') or ''
                    element_id = element.get_attribute('id') or ''
                    
                    # Check if it has arabic-font class
                    has_arabic_font_class = 'arabic-font' in class_attr
                    
                    if not has_arabic_font_class:
                        arabic_text_issues.append({
                            'tag': tag,
                            'id': element_id,
                            'class': class_attr,
                            'text': text[:100] + '...' if len(text) > 100 else text
                        })
            
            # Print results
            print(f"\nFound {len(arabic_text_issues)} Arabic text elements without 'arabic-font' class:")
            for i, issue in enumerate(arabic_text_issues, 1):
                print(f"{i}. <{issue['tag']}> (class='{issue['class']}', id='{issue['id']}')")
                print(f"   Text: {issue['text']}")
                print()
            
            # Assert no issues found
            assert len(arabic_text_issues) == 0, f"Found {len(arabic_text_issues)} Arabic text elements without arabic-font class"
            
        finally:
            browser.close()


if __name__ == '__main__':
    test_arabic_text_audit()
    print("✅ All Arabic text uses arabic-font class!")
