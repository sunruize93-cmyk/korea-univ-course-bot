import time
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class KupidBot:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.driver = None
        self.wait = None
        self.is_logged_in = False

    def initialize_driver(self):
        """Initialize the Chrome WebDriver with options."""
        self.logger.info("Initializing WebDriver...")
        chrome_options = Options()
        
        if self.config.get("headless", False):
            chrome_options.add_argument("--headless")
        
        # Anti-detection measures
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            # Execute CDP commands to prevent detection
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })
            self.logger.info("WebDriver initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def login(self):
        """Handle login process."""
        try:
            self.logger.info("Navigating to login page...")
            self.driver.get("https://kupid.korea.ac.kr") # Redirects to portal login
            
            # TODO: UPDATE THESE SELECTORS BASED ON ACTUAL PAGE SOURCE
            # Note: These are placeholder IDs. You must inspect the KUPID login page 
            # and update 'id' and 'pw' with the actual HTML element IDs.
            USERNAME_FIELD_ID = "id"  
            PASSWORD_FIELD_ID = "pw"
            LOGIN_BUTTON_ID = "btn_login" # or equivalent xpath

            self.logger.info("Waiting for login fields...")
            username_input = self.wait.until(EC.presence_of_element_located((By.ID, USERNAME_FIELD_ID)))
            password_input = self.driver.find_element(By.ID, PASSWORD_FIELD_ID)
            
            # Human-like typing
            for char in self.config["username"]:
                username_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
            
            time.sleep(random.uniform(0.3, 0.7))
            
            for char in self.config["password"]:
                password_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))
            
            self.logger.info("Credentials entered. Attempting login...")
            
            # Check for CAPTCHA
            # If there is a captcha image, we might need to pause and let user solve it
            # or use an OCR service. For this version, we'll pause if we detect it.
            try:
                # Placeholder for captcha element
                captcha_img = self.driver.find_element(By.ID, "captcha_image_id") 
                if captcha_img.is_displayed():
                    self.logger.warning("CAPTCHA detected! Please solve it manually in the browser window.")
                    self.logger.info("Waiting 30 seconds for manual CAPTCHA solution...")
                    time.sleep(30)
            except NoSuchElementException:
                pass

            # Click login
            login_btn = self.driver.find_element(By.ID, LOGIN_BUTTON_ID) # Or By.XPATH, etc.
            login_btn.click()
            
            # Wait for successful login indicator (e.g., logout button or main menu)
            # Adjust selector for successful login check
            self.wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Log out")))
            self.is_logged_in = True
            self.logger.info("Login successful!")
            
        except TimeoutException:
            self.logger.error("Login timed out. Please check your network or selectors.")
            # Allow manual login if automation fails
            self.logger.info("Waiting 60s for manual login intervention...")
            time.sleep(60)
            if self.driver.current_url != "https://kupid.korea.ac.kr": # basic check
                 self.is_logged_in = True
        except Exception as e:
            self.logger.error(f"Login failed: {e}")

    def navigate_to_registration(self):
        """Navigate to the course registration page."""
        # This logic highly depends on the menu structure of KUPID (usually frames or iframes)
        self.logger.info("Navigating to course registration menu...")
        # Example: Click 'Registration' -> 'Course Registration'
        # You might need to switch_to.frame if the site uses frames
        pass 

    def search_course(self, course_code):
        """Search for a specific course."""
        self.logger.info(f"Searching for course: {course_code}")
        
        # Placeholder selectors - UPDATE THESE
        SEARCH_INPUT_ID = "course_code_input"
        SEARCH_BTN_ID = "search_button"
        
        try:
            search_input = self.driver.find_element(By.ID, SEARCH_INPUT_ID)
            search_input.clear()
            search_input.send_keys(course_code)
            
            self.driver.find_element(By.ID, SEARCH_BTN_ID).click()
            time.sleep(random.uniform(1, 2)) # Wait for AJAX
            
            return True
        except Exception as e:
            self.logger.error(f"Error searching course {course_code}: {e}")
            return False

    def check_availability_and_register(self, course_info):
        """Check if slots are available and register."""
        course_code = course_info["course_code"]
        
        # Find the row corresponding to the course
        # This usually involves finding a table row <tr> that contains the course code
        # and checking a specific column for 'Capacity' vs 'Enrolled'
        
        try:
            # Example logic: Find row by text
            # xpath = f"//tr[contains(., '{course_code}')]"
            # row = self.driver.find_element(By.XPATH, xpath)
            
            # Check availability column (e.g., 5th column)
            # available_text = row.find_element(By.XPATH, "./td[5]").text
            # current, total = map(int, available_text.split('/'))
            
            # MOCK implementation for demonstration
            is_available = False # Change logic to parse real HTML
            
            if is_available:
                self.logger.info(f"Slot found for {course_code}! Attempting to register...")
                # Click register button in that row
                # register_btn = row.find_element(By.XPATH, ".//button[contains(text(), 'Register')]")
                # register_btn.click()
                
                # Handle popup confirmation
                # try:
                #     alert = self.driver.switch_to.alert
                #     alert.accept()
                # except:
                #     pass
                    
                self.logger.info(f"Registration command sent for {course_code}. Verifying...")
                # Add verification logic here
                return True
            else:
                self.logger.debug(f"No slots for {course_code}.")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking/registering {course_code}: {e}")
            return False

    def run(self):
        """Main loop."""
        try:
            self.initialize_driver()
            self.login()
            
            if not self.is_logged_in:
                self.logger.error("Login failed. Exiting.")
                return

            self.navigate_to_registration()
            
            while True:
                for course in self.config["target_courses"]:
                    self.search_course(course["course_code"])
                    if self.check_availability_and_register(course):
                        self.logger.info(f"Successfully registered for {course['course_name']}! Removing from list.")
                        self.config["target_courses"].remove(course)
                        if not self.config["target_courses"]:
                            self.logger.info("All courses registered! Exiting.")
                            return
                    
                    # Random delay between courses
                    time.sleep(random.uniform(0.5, 1.5))
                
                # Wait before next cycle
                wait_time = self.config["refresh_interval"] + random.uniform(0, 2)
                self.logger.info(f"Waiting {wait_time:.2f}s before next scan...")
                time.sleep(wait_time)
                
                # Refresh page periodically to keep session alive or reset state
                # self.driver.refresh()
                
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user.")
        except Exception as e:
            self.logger.critical(f"Unexpected error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
