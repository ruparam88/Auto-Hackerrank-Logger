import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def random_delay(min_seconds=0.5, max_seconds=2.0):
    time.sleep(random.uniform(min_seconds, max_seconds))

def setup_driver():
    try:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=100vw,100vh")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        
        logger.info("Initializing Chrome driver...")
        driver = uc.Chrome(
            options=options,
            driver_executable_path=None,  # Let it auto-detect
            browser_executable_path=None,  # Let it auto-detect
            suppress_welcome=True,
            use_subprocess=True
        )
        logger.info("Chrome driver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to set up Chrome driver: {str(e)}")
        logger.error("Please make sure you have Chrome browser installed and up to date")
        raise

def move_to_element_with_offset(driver, element):
    """Move to element with random offset to simulate human behavior"""
    action = ActionChains(driver)
    size = element.size
    x_offset = random.randint(-size['width']//4, size['width']//4)
    y_offset = random.randint(-size['height']//4, size['height']//4)
    action.move_to_element_with_offset(element, x_offset, y_offset).perform()
    random_delay(0.1, 0.3)

def type_like_human(element, text):
    """Type text with random delays between keystrokes"""
    for char in text:
        element.send_keys(char)
        random_delay(0.05, 0.2)

def login_to_hackerrank(driver, username, password):
    try:
        logger.info("Navigating to HackerRank login page...")
        driver.get('https://www.hackerrank.com/auth/login')
        wait = WebDriverWait(driver, 5)
        
        logger.info("Waiting for login form...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        random_delay()
        
        # Try different selectors for username field
        selectors = [
            (By.ID, "input-1"),
            (By.NAME, "username"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[data-analytics='LoginUsername']")
        ]
        
        username_field = None
        for by, selector in selectors:
            try:
                username_field = wait.until(EC.presence_of_element_located((by, selector)))
                if username_field.is_displayed():
                    break
            except:
                continue
        
        if not username_field:
            raise Exception("Could not find username field")
            
        logger.info("Found username field, filling it...")
        move_to_element_with_offset(driver, username_field)
        username_field.click()
        type_like_human(username_field, username)
        
        # Try different selectors for password field
        password_selectors = [
            (By.ID, "input-2"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[data-analytics='LoginPassword']")
        ]
        
        password_field = None
        for by, selector in password_selectors:
            try:
                password_field = wait.until(EC.presence_of_element_located((by, selector)))
                if password_field.is_displayed():
                    break
            except:
                continue
                
        if not password_field:
            raise Exception("Could not find password field")
            
        logger.info("Found password field, filling it...")
        move_to_element_with_offset(driver, password_field)
        password_field.click()
        random_delay()
        type_like_human(password_field, password)
        random_delay()
        
        # Try different selectors for login button
        button_selectors = [
            (By.CSS_SELECTOR, "button[data-analytics='LoginPassword']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Log In')]"),
            (By.XPATH, "//button[contains(@class, 'login')]")
        ]
        
        login_button = None
        for by, selector in button_selectors:
            try:
                login_button = wait.until(EC.element_to_be_clickable((by, selector)))
                if login_button.is_displayed():
                    break
            except:
                continue
                
        if not login_button:
            raise Exception("Could not find login button")
            
        logger.info("Found login button, clicking it...")
        move_to_element_with_offset(driver, login_button)
        random_delay()
        login_button.click()
        
        logger.info("Waiting for login to complete...")
        # Try different selectors for successful login
        success_selectors = [
            (By.CLASS_NAME, "profile-nav-item-link"),
            (By.CSS_SELECTOR, "[data-analytics='NavBarProfileDropDown']"),
            (By.XPATH, "//div[contains(@class, 'profile')]")
        ]
        
        for by, selector in success_selectors:
            try:
                wait.until(EC.presence_of_element_located((by, selector)))
                logger.info("Successfully logged in!")
                return
            except:
                continue
                
        raise Exception("Login might have failed - could not detect success condition")
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise

def fetch_unsolved_problems(driver):
    try:
        logger.info("Navigating to algorithms page...")
        driver.get('https://www.hackerrank.com/domains/algorithms')
        random_delay(3, 5)
        
        # Wait for the challenges to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.challenge-list')))
        
        unsolved_problems = []
        page = 1
        
        while True:
            logger.info(f"Parsing page {page}...")
            
            # Wait for challenge cards to be visible
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.challenge-card')))
            random_delay(1, 2)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find all challenge cards
            problem_items = soup.find_all('div', class_='challenge-card')
            if not problem_items:
                logger.info("No more problems found")
                break
                
            for problem in problem_items:
                try:
                    # Get problem title and link
                    title_element = problem.find('h4', class_='challengecard-title')
                    if not title_element:
                        continue
                        
                    problem_name = title_element.text.strip()
                    problem_link = problem.find('a')
                    
                    if not problem_link:
                        continue
                        
                    problem_url = 'https://www.hackerrank.com' + problem_link.get('href', '')
                    
                    # Check if problem is solved
                    solved_badge = problem.find('div', class_='solved-badge')
                    if not solved_badge:
                        unsolved_problems.append((problem_name, problem_url))
                        logger.info(f"Found unsolved problem: {problem_name}")
                        
                except Exception as e:
                    logger.error(f"Error processing problem: {e}")
                    continue
            
            # Try to go to next page
            try:
                next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-attr1="Right"]')))
                if not next_button.is_enabled():
                    break
                    
                logger.info(f"Moving to page {page + 1}")
                next_button.click()
                random_delay(2, 4)
                page += 1
                
            except Exception as e:
                logger.info("No more pages to process")
                break
                
        logger.info(f"Found {len(unsolved_problems)} unsolved problems")
        return unsolved_problems
        
    except Exception as e:
        logger.error(f"Error fetching problems: {e}")
        raise

def main():
    username = 'USERNAME'
    password = 'PASSCODE'
    driver = None
    
    try:
        logger.info("Setting up Chrome driver...")
        driver = setup_driver()
        
        login_to_hackerrank(driver, username, password)
        unsolved_problems = fetch_unsolved_problems(driver)
        
        print("\nUnsolved Problems:")
        for name, url in unsolved_problems:
            print(f"{name}: {url}")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    main()