import asyncio
import time
import random
import json
import aiohttp
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

from ntp_utils import TimeSynchronizer

class SugangBot:
    """Handles initial login via Selenium to get secure cookies."""
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.wait = None
        self.cookies = {}

    def initialize_driver(self):
        logger.info("Initializing Selenium WebDriver for login...")
        chrome_options = Options()
        if self.config.get("headless", False):
            chrome_options.add_argument("--headless")
        
        # Anti-detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self):
        try:
            logger.info("Navigating to login page...")
            self.driver.get("https://sugang.korea.ac.kr")
            
            # --- CRITICAL: USER MUST UPDATE THESE SELECTORS ---
            # Inspect the page and update these IDs
            USERNAME_FIELD_ID = "id"  
            PASSWORD_FIELD_ID = "pw"
            # --------------------------------------------------

            logger.info("Waiting for login fields...")
            try:
                username_input = self.wait.until(EC.presence_of_element_located((By.ID, USERNAME_FIELD_ID)))
                password_input = self.driver.find_element(By.ID, PASSWORD_FIELD_ID)
            except TimeoutException:
                logger.error("Could not find login fields. Please update USERNAME_FIELD_ID in bot.py")
                return False

            username_input.send_keys(self.config["username"])
            password_input.send_keys(self.config["password"])
            
            logger.info("Please complete the login manually in the browser window if needed (CAPTCHA, etc.).")
            logger.info("Waiting for redirect to main page...")
            
            # Wait until URL changes or a specific element appears indicating login success
            # Here we wait for a generic time or user confirmation for safety in this template
            # Ideally, wait for "Log out" button
            time.sleep(15) 
            
            # Extract cookies
            selenium_cookies = self.driver.get_cookies()
            for cookie in selenium_cookies:
                self.cookies[cookie['name']] = cookie['value']
            
            logger.success(f"Login successful! Captured {len(self.cookies)} cookies.")
            return True

        except Exception as e:
            logger.error(f"Selenium login failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

class AsyncSugangBot:
    """High-performance async bot using aiohttp."""
    def __init__(self, config, cookies):
        self.config = config
        self.cookies = cookies
        self.session = None
        self.ua = UserAgent()
        self.ntp = TimeSynchronizer()
        self.base_url = "https://sugang.korea.ac.kr" # Update if API is different
        
        # Concurrency settings
        self.conc_config = config.get("concurrency", {})
        self.net_config = config.get("network", {})
        
    async def init_session(self):
        """Initializes aiohttp session with connection pooling."""
        connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)
        self.session = aiohttp.ClientSession(
            cookies=self.cookies,
            connector=connector,
            headers={"User-Agent": self.ua.random}
        )
        # Pre-warm connection
        try:
            await self.session.get(self.base_url)
            logger.info("Connection pool warmed up.")
        except:
            pass

    async def close(self):
        if self.session:
            await self.session.close()

    def get_headers(self):
        """Generates dynamic headers to avoid detection."""
        return {
            "User-Agent": self.ua.random,
            "Referer": "https://sugang.korea.ac.kr/",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            # Add other static headers here
        }

    async def register_course(self, course, attempt_id):
        """
        Sends a single registration request.
        TODO: You MUST inspect the Network tab in DevTools to find:
        1. The exact Request URL for registration.
        2. The Request Method (POST/GET).
        3. The Form Data / JSON Payload.
        """
        
        # --- PLACEHOLDER URL & DATA ---
        # Example: https://sugang.korea.ac.kr/sugang/register.do
        url = f"{self.base_url}/core/service/sugang/register" 
        
        payload = {
            "course_code": course["course_code"],
            # "token": "...", # Some sites require a CSRF token
            # ... add other required fields from config or hardcoded
        }
        # ------------------------------

        start_time = time.time()
        
        # Jitter
        if self.net_config.get("jitter_min"):
            await asyncio.sleep(random.uniform(
                self.net_config["jitter_min"], 
                self.net_config["jitter_max"]
            ))

        try:
            async with self.session.post(url, data=payload, headers=self.get_headers()) as response:
                latency = (time.time() - start_time) * 1000
                status = response.status
                
                # Try to parse response
                try:
                    resp_text = await response.text()
                    # resp_json = await response.json() 
                except:
                    resp_text = "No Content"

                log_msg = f"| Attempt: {attempt_id} | Status: {status} | Latency: {latency:.2f}ms | Course: {course['course_code']}"
                
                if status == 200 and "success" in resp_text.lower(): # Adjust success condition
                    logger.success(f"SUCCESS! {log_msg}")
                    return True
                elif status == 503:
                    logger.warning(f"Server Overload {log_msg}")
                else:
                    logger.info(f"Failed {log_msg}")
                    
                return False

        except Exception as e:
            logger.error(f"Request Error: {e}")
            return False

    async def burst_attack(self):
        """Orchestrates the high-concurrency attack."""
        await self.init_session()
        
        # NTP Sync
        self.ntp.sync()
        
        # Wait for target time if configured
        target_str = self.conc_config.get("target_time")
        if target_str:
            target_ts = time.mktime(time.strptime(target_str, "%Y-%m-%d %H:%M:%S"))
            # Start slightly earlier (burst_start_ms)
            start_ts = target_ts - (self.conc_config.get("burst_start_ms", 0) / 1000.0)
            
            wait_seconds = start_ts - self.ntp.get_time()
            if wait_seconds > 0:
                logger.info(f"Waiting {wait_seconds:.2f}s for target time...")
                await asyncio.sleep(wait_seconds)
            else:
                logger.warning("Target time passed! Starting immediately.")

        logger.info("🚀 STARTING BURST MODE 🚀")
        
        tasks = []
        task_id = 0
        
        # Infinite loop or limited attempts
        # Here we demonstrate a continuous wave
        while True:
            for course in self.config["target_courses"]:
                # Batch creation
                batch_size = self.conc_config.get("max_tasks", 5)
                
                # Create a batch of concurrent tasks
                batch = []
                for _ in range(batch_size):
                    task_id += 1
                    batch.append(self.register_course(course, task_id))
                
                # Execute batch
                results = await asyncio.gather(*batch)
                
                if any(results):
                    logger.success("Course registered! Stopping bot.")
                    return
            
            # Small delay between batches to avoid total IP ban
            await asyncio.sleep(self.net_config.get("retry_delay_base", 0.1))

        await self.close()
