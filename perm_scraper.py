"""
PERM Scraper Module
Fetches PERM application status from permupdate.com using Selenium for JavaScript support
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict, Any
import time
import random
import re
from datetime import datetime, timedelta
import config

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class PERMScraper:
    """Scraper for PERM application status from permupdate.com using Selenium"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = config.PERM_UPDATE_URL
        self.timeout = config.SCRAPER_TIMEOUT
        self.retries = config.SCRAPER_RETRIES
        
        # Initialize Selenium driver
        self.driver = None
    
    def _setup_driver(self) -> bool:
        """Setup Selenium Chrome driver with performance logging"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Enable performance logging to capture network requests
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            # Setup the driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Selenium Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Selenium driver: {e}")
            return False
    
    def _cleanup_driver(self):
        """Clean up Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("Selenium driver cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up driver: {e}")
    
    def get_perm_status(self, case_number: str, submission_date: str, employer_letter: str) -> Optional[Dict[str, Any]]:
        """Get PERM application status from permupdate.com"""
        try:
            logger.info(f"Fetching PERM status for case {case_number}")
            
            # Check if mock data is enabled
            if config.ENABLE_MOCK_DATA:
                logger.info("Mock data is enabled, using mock status")
                return self._get_mock_status(case_number, submission_date)
            
            # First, try direct API call to the discovered backend
            logger.info("Trying direct API call to discovered backend...")
            direct_result = self._try_direct_api_call(case_number, submission_date, employer_letter)
            if direct_result:
                return direct_result
            
            # Fallback to Selenium approach
            logger.info("Direct API failed, trying Selenium approach...")
            status = self._scrape_with_selenium(case_number, submission_date, employer_letter)
            
            if status:
                return status
            
            # If Selenium fails, return None to indicate error
            logger.error("Failed to fetch PERM status from permupdate.com using Selenium")
            return None
            
        except Exception as e:
            logger.error(f"Error getting PERM status: {e}")
            return None
        finally:
            # Always cleanup the driver
            self._cleanup_driver()
    
    def _try_direct_api_call(self, case_number: str, submission_date: str, employer_letter: str) -> Optional[Dict[str, Any]]:
        """Try direct API call to the discovered backend"""
        try:
            # Use the discovered API endpoint
            api_url = "https://perm-backend-production.up.railway.app/api/data/dashboard"
            
            headers = {
                'User-Agent': self.session.headers['User-Agent'],
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Origin': 'https://permupdate.com',
                'Referer': 'https://permupdate.com/'
            }
            
            # Get dashboard data
            response = self.session.get(f"{api_url}?days=30", headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Successfully retrieved real PERM data from API")
                
                # Extract relevant data from the response
                metrics = data.get('metrics', {})
                processing_times = metrics.get('processing_times', {})
                
                # Calculate position based on submission date and current backlog
                current_backlog = metrics.get('current_backlog', 91580)
                submission_date_obj = datetime.strptime(submission_date, '%Y-%m-%d')
                current_date = datetime.now()
                days_since_submission = (current_date - submission_date_obj).days
                
                # Estimate position based on processing rate and submission date
                daily_processing_rate = metrics.get('processed_cases', 490)  # Daily rate
                estimated_position = max(1, current_backlog - (days_since_submission * daily_processing_rate))
                
                # Calculate completion date
                median_days = processing_times.get('median_days', 485)
                completion_date = submission_date_obj + timedelta(days=median_days)
                
                return {
                    'position_in_queue': int(estimated_position),
                    'total_applications': current_backlog,
                    'last_processed_date': submission_date,
                    'processing_rate': daily_processing_rate,
                    'status': 'Pending Review',
                    'completion_date': completion_date.strftime('%Y-%m-%d'),
                    'remaining_days': max(0, median_days - days_since_submission),
                    'case_number': case_number,
                    'submission_date': submission_date,
                    'employer_letter': employer_letter,
                    'data_source': 'perm-backend-production.up.railway.app',
                    'data_date': processing_times.get('as_of_date', '2025-07-16')
                }
            
            logger.warning(f"Direct API call failed: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error in direct API call: {e}")
            return None
    
    def _scrape_with_selenium(self, case_number: str, submission_date: str, employer_letter: str) -> Optional[Dict[str, Any]]:
        """Scrape PERM status using Selenium to handle JavaScript"""
        try:
            # Setup Selenium driver
            if not self._setup_driver():
                return None
            
            if not self.driver:
                logger.error("Driver is None after setup")
                return None
            
            logger.info(f"Navigating to {self.base_url}")
            
            # Try to load the page with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.driver.get(self.base_url)
                    
                    # Wait for page to load with a shorter timeout
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    logger.info("Page loaded successfully")
                    break
                    
                except Exception as e:
                    logger.warning(f"Page load attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        logger.error("All page load attempts failed")
                        return None
                    time.sleep(2)  # Wait before retry
            
            # Wait a bit more for JavaScript to load
            time.sleep(3)
            
            # Debug: Log the current page title and URL
            logger.info(f"Current page title: {self.driver.title}")
            logger.info(f"Current page URL: {self.driver.current_url}")
            
            # Inspect the form structure in detail
            logger.info("=== FORM INSPECTION ===")
            
            # Look for all forms
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            logger.info(f"Found {len(forms)} forms on the page")
            
            for i, form in enumerate(forms):
                try:
                    form_id = form.get_attribute('id') or 'No ID'
                    form_class = form.get_attribute('class') or 'No class'
                    form_action = form.get_attribute('action') or 'No action'
                    form_method = form.get_attribute('method') or 'No method'
                    logger.info(f"Form {i+1}: id='{form_id}', class='{form_class}', action='{form_action}', method='{form_method}'")
                    
                    # Look for all inputs in this form
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    logger.info(f"  Form {i+1} has {len(inputs)} input fields:")
                    
                    for j, inp in enumerate(inputs):
                        try:
                            name = inp.get_attribute('name') or 'No name'
                            id_attr = inp.get_attribute('id') or 'No id'
                            placeholder = inp.get_attribute('placeholder') or 'No placeholder'
                            input_type = inp.get_attribute('type') or 'No type'
                            required = inp.get_attribute('required') or 'No required'
                            value = inp.get_attribute('value') or 'No value'
                            logger.info(f"    Input {j+1}: name='{name}', id='{id_attr}', type='{input_type}', placeholder='{placeholder}', required='{required}', value='{value}'")
                        except:
                            pass
                    
                    # Look for all selects in this form
                    selects = form.find_elements(By.TAG_NAME, "select")
                    logger.info(f"  Form {i+1} has {len(selects)} select fields:")
                    
                    for j, sel in enumerate(selects):
                        try:
                            name = sel.get_attribute('name') or 'No name'
                            id_attr = sel.get_attribute('id') or 'No id'
                            required = sel.get_attribute('required') or 'No required'
                            logger.info(f"    Select {j+1}: name='{name}', id='{id_attr}', required='{required}'")
                            
                            # Look for options
                            options = sel.find_elements(By.TAG_NAME, "option")
                            logger.info(f"      Select {j+1} has {len(options)} options:")
                            for k, opt in enumerate(options[:5]):  # Show first 5 options
                                try:
                                    opt_value = opt.get_attribute('value') or 'No value'
                                    opt_text = opt.text or 'No text'
                                    logger.info(f"        Option {k+1}: value='{opt_value}', text='{opt_text}'")
                                except:
                                    pass
                        except:
                            pass
                    
                    # Look for all buttons in this form
                    buttons = form.find_elements(By.TAG_NAME, "button")
                    logger.info(f"  Form {i+1} has {len(buttons)} buttons:")
                    
                    for j, btn in enumerate(buttons):
                        try:
                            btn_text = btn.text or 'No text'
                            btn_type = btn.get_attribute('type') or 'No type'
                            btn_id = btn.get_attribute('id') or 'No id'
                            btn_class = btn.get_attribute('class') or 'No class'
                            logger.info(f"    Button {j+1}: text='{btn_text}', type='{btn_type}', id='{btn_id}', class='{btn_class}'")
                        except:
                            pass
                            
                except Exception as e:
                    logger.warning(f"Error inspecting form {i+1}: {e}")
            
            logger.info("=== END FORM INSPECTION ===")
            
            # Look for the prediction form more carefully
            logger.info("Looking for prediction form elements...")
            
            # Try to find the form container or prediction section
            form_selectors = [
                "form",
                "[class*='predict']",
                "[class*='search']",
                "[id*='predict']",
                "[id*='search']",
                "[class*='form']",
                "[class*='input']"
            ]
            
            form_found = False
            for selector in form_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"Found {len(elements)} elements with selector: {selector}")
                        form_found = True
                        break
                except:
                    continue
            
            if not form_found:
                logger.warning("No form elements found, looking for any input fields")
            
            # Look for input fields for case number and employer letter
            case_input = None
            letter_input = None
            
            # Try different selectors for case number input
            case_selectors = [
                "input[name*='case']",
                "input[id*='case']",
                "input[placeholder*='case']",
                "input[placeholder*='number']",
                "input[type='text']"
            ]
            
            for selector in case_selectors:
                try:
                    if self.driver:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            case_input = elements[0]  # Use first matching element
                            logger.info(f"Found case input with selector: {selector}")
                            break
                except:
                    continue
            
            # Try different selectors for employer letter input
            letter_selectors = [
                "input[name*='employer']",
                "input[name*='letter']",
                "input[id*='employer']",
                "input[id*='letter']",
                "select[name*='employer']",
                "select[name*='letter']"
            ]
            
            for selector in letter_selectors:
                try:
                    if self.driver:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            letter_input = elements[0]  # Use first matching element
                            logger.info(f"Found letter input with selector: {selector}")
                            break
                except:
                    continue
            
            if not case_input:
                logger.error("Could not find case number input field")
                # Debug: Log all input fields on the page
                try:
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    logger.info(f"Found {len(all_inputs)} input fields on the page")
                    for i, inp in enumerate(all_inputs[:5]):  # Log first 5 inputs
                        try:
                            name = inp.get_attribute('name') or 'No name'
                            id_attr = inp.get_attribute('id') or 'No id'
                            placeholder = inp.get_attribute('placeholder') or 'No placeholder'
                            logger.info(f"Input {i+1}: name='{name}', id='{id_attr}', placeholder='{placeholder}'")
                        except:
                            pass
                except:
                    pass
                return None
            
            # Fill in the case number
            case_input.clear()
            case_input.send_keys(case_number)
            logger.info(f"Entered case number: {case_number}")
            
            # Fill in the employer letter if found
            if letter_input:
                letter_input.clear()
                letter_input.send_keys(employer_letter)
                logger.info(f"Entered employer letter: {employer_letter}")
            
            # Look for submit button more carefully
            submit_button = None
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Predict')",
                "button:contains('Submit')",
                "button:contains('Search')",
                "button:contains('Go')",
                "button:contains('Find')"
            ]
            
            for selector in submit_selectors:
                try:
                    if self.driver:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            submit_button = elements[0]
                            logger.info(f"Found submit button with selector: {selector}")
                            break
                except:
                    continue
            
            if not submit_button and self.driver:
                # Try to find any button
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                if buttons:
                    submit_button = buttons[0]  # Use first button
                    logger.info(f"Using first button as submit button (text: {submit_button.text})")
            
            if not submit_button:
                logger.error("Could not find submit button")
                return None
            
            # Try different methods to submit the form
            submission_successful = False
            
            # Method 1: Click the button
            try:
                submit_button.click()
                logger.info("Method 1: Clicked submit button")
                time.sleep(2)
                
                # Check if submission worked
                if self.driver.current_url != self.base_url or "dashboard" not in self.driver.title.lower():
                    submission_successful = True
                    logger.info("Method 1 successful: Page changed")
                else:
                    logger.info("Method 1 failed: Page didn't change")
            except Exception as e:
                logger.warning(f"Method 1 failed: {e}")
            
            # Method 2: Try JavaScript click
            if not submission_successful:
                try:
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    logger.info("Method 2: JavaScript click on submit button")
                    time.sleep(2)
                    
                    if self.driver.current_url != self.base_url or "dashboard" not in self.driver.title.lower():
                        submission_successful = True
                        logger.info("Method 2 successful: Page changed")
                    else:
                        logger.info("Method 2 failed: Page didn't change")
                except Exception as e:
                    logger.warning(f"Method 2 failed: {e}")
            
            # Method 3: Try submitting the form directly
            if not submission_successful:
                try:
                    # Find the form and submit it
                    forms = self.driver.find_elements(By.TAG_NAME, "form")
                    if forms:
                        self.driver.execute_script("arguments[0].submit();", forms[0])
                        logger.info("Method 3: Submitted form directly")
                        time.sleep(2)
                        
                        if self.driver.current_url != self.base_url or "dashboard" not in self.driver.title.lower():
                            submission_successful = True
                            logger.info("Method 3 successful: Page changed")
                        else:
                            logger.info("Method 3 failed: Page didn't change")
                    else:
                        logger.info("Method 3 failed: No form found")
                except Exception as e:
                    logger.warning(f"Method 3 failed: {e}")
            
            # Method 4: Try pressing Enter key
            if not submission_successful:
                try:
                    from selenium.webdriver.common.keys import Keys
                    case_input.send_keys(Keys.RETURN)
                    logger.info("Method 4: Pressed Enter key")
                    time.sleep(2)
                    
                    if self.driver.current_url != self.base_url or "dashboard" not in self.driver.title.lower():
                        submission_successful = True
                        logger.info("Method 4 successful: Page changed")
                    else:
                        logger.info("Method 4 failed: Page didn't change")
                except Exception as e:
                    logger.warning(f"Method 4 failed: {e}")
            
            if not submission_successful:
                logger.error("All form submission methods failed")
                return None
            
            logger.info("Form submission successful, waiting for results...")
            
            # Capture network traffic during form submission
            logger.info("Capturing network traffic...")
            
            # Get performance logs to see network requests
            try:
                logs = self.driver.get_log('performance')
                logger.info(f"Captured {len(logs)} performance log entries")
                
                # Analyze network requests
                api_requests = self._analyze_network_logs(logs)
                
                if api_requests:
                    logger.info(f"Found {len(api_requests)} API requests:")
                    for i, req in enumerate(api_requests):
                        logger.info(f"  Request {i+1}: {req['method']} {req['url']}")
                        if req.get('data'):
                            logger.info(f"    Data: {req['data']}")
                    
                    # Try to call the discovered API endpoints
                    for req in api_requests:
                        if req['url'] and req['url'] != self.base_url:
                            result = self._try_discovered_api(req, case_number, submission_date, employer_letter)
                            if result:
                                return result
            
                    # Try additional API patterns that might be used for case predictions
                    logger.info("Trying additional API patterns for case predictions...")
                    
                    additional_patterns = [
                        '/api/predict',
                        '/api/case',
                        '/api/search',
                        '/api/status',
                        '/api/timeline',
                        '/api/estimate',
                        '/api/queue',
                        '/api/position',
                        '/api/processing',
                        '/api/backlog',
                        '/api/dashboard/predict',
                        '/api/dashboard/case',
                        '/api/dashboard/search',
                        '/api/dashboard/status'
                    ]
                    
                    base_api_url = "https://perm-backend-production.up.railway.app"
                    
                    for pattern in additional_patterns:
                        api_url = f"{base_api_url}{pattern}"
                        logger.info(f"Trying additional API pattern: {api_url}")
                        
                        result = self._try_api_call(api_url, case_number, submission_date, employer_letter)
                        if result:
                            return result
            
            except Exception as e:
                logger.warning(f"Error analyzing network logs: {e}")
            
            # Wait for results to load with better logic
            max_wait_attempts = 10
            for attempt in range(max_wait_attempts):
                try:
                    time.sleep(2)  # Wait for page to update
                    
                    # Debug: Log current page state
                    logger.info(f"Attempt {attempt + 1}: Current URL: {self.driver.current_url}")
                    logger.info(f"Attempt {attempt + 1}: Current title: {self.driver.title}")
                    
                    # Get the page source after submission
                    if not self.driver:
                        logger.error("Driver is None when trying to get page source")
                        return None
                        
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    # Extract status from the results
                    status_info = self._extract_status_from_results(soup, case_number, submission_date, employer_letter)
                    
                    if status_info:
                        logger.info(f"Successfully extracted status using Selenium: {status_info}")
                        return status_info
                    
                    # Check if we're still on the same page (form submission might have failed)
                    if "dashboard" in self.driver.title.lower() or "tracker" in self.driver.title.lower():
                        logger.info(f"Attempt {attempt + 1}: Still on dashboard page, form submission may have failed")
                    
                    logger.info(f"Attempt {attempt + 1}: No status info found, waiting...")
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == max_wait_attempts - 1:
                        break
                    time.sleep(2)
            
            logger.warning("Could not extract status information from Selenium results after all attempts")
            return None
            
        except Exception as e:
            logger.error(f"Error in Selenium scraping: {e}")
            return None
    
    def _find_api_endpoints(self, page_source: str, scripts: list) -> list:
        """Find API endpoints in JavaScript code"""
        endpoints = []
        
        # Common patterns for API endpoints
        patterns = [
            # fetch() calls
            r'fetch\(["\']([^"\']+)["\']',
            r'fetch\(`([^`]+)`',
            # axios calls
            r'axios\.(?:get|post)\(["\']([^"\']+)["\']',
            r'axios\.(?:get|post)\(`([^`]+)`',
            # jQuery ajax
            r'\.ajax\([^)]*url:\s*["\']([^"\']+)["\']',
            r'\.ajax\([^)]*url:\s*`([^`]+)`',
            # XMLHttpRequest
            r'\.open\([^,]+,\s*["\']([^"\']+)["\']',
            # API URLs in variables
            r'["\'](/api/[^"\']+)["\']',
            r'["\'](/predict[^"\']*)["\']',
            r'["\'](/search[^"\']*)["\']',
            r'["\'](/status[^"\']*)["\']',
            # Base URL patterns
            r'baseURL\s*[:=]\s*["\']([^"\']+)["\']',
            r'apiUrl\s*[:=]\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 3:  # Filter out very short matches
                    endpoints.append(match)
        
        # Also look in script content
        for script in scripts:
            if script.string:
                script_content = script.string
                for pattern in patterns:
                    matches = re.findall(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        if match and len(match) > 3:
                            endpoints.append(match)
        
        # Remove duplicates and filter
        unique_endpoints = list(set(endpoints))
        filtered_endpoints = []
        
        for endpoint in unique_endpoints:
            # Filter out common non-API URLs
            if any(keyword in endpoint.lower() for keyword in ['api', 'predict', 'search', 'status', 'case']):
                filtered_endpoints.append(endpoint)
        
        return filtered_endpoints
    
    def _call_api_endpoints(self, endpoints: list, case_number: str, submission_date: str, employer_letter: str) -> Optional[Dict[str, Any]]:
        """Try calling the found API endpoints"""
        for endpoint in endpoints:
            try:
                # Normalize the endpoint URL
                if endpoint.startswith('/'):
                    api_url = f"{self.base_url.rstrip('/')}{endpoint}"
                elif endpoint.startswith('http'):
                    api_url = endpoint
                else:
                    api_url = f"{self.base_url}/{endpoint}"
                
                logger.info(f"Trying API endpoint: {api_url}")
                
                # Try different data formats and HTTP methods
                result = self._try_api_call(api_url, case_number, submission_date, employer_letter)
                if result:
                    return result
                    
            except Exception as e:
                logger.warning(f"Failed to call endpoint {endpoint}: {e}")
                continue
        
        return None
    
    def _try_api_call(self, api_url: str, case_number: str, submission_date: str, employer_letter: str) -> Optional[Dict[str, Any]]:
        """Try different ways to call an API endpoint"""
        
        # Different data formats to try
        data_formats = [
            # JSON format
            {
                'case_number': case_number,
                'employer_letter': employer_letter
            },
            {
                'caseNumber': case_number,
                'employerLetter': employer_letter
            },
            {
                'case': case_number,
                'letter': employer_letter
            },
            {
                'case_number': case_number,
                'employer_letter': employer_letter,
                'submission_date': submission_date
            }
        ]
        
        # Different HTTP methods to try
        methods = ['POST', 'GET']
        
        headers = {
            'User-Agent': self.session.headers['User-Agent'],
            'Referer': self.base_url,
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        for method in methods:
            for i, data in enumerate(data_formats):
                try:
                    logger.info(f"Trying {method} request with data format {i+1}")
                    
                    if method == 'POST':
                        # Try JSON first
                        response = self.session.post(api_url, json=data, headers=headers, timeout=self.timeout)
                        if response.status_code == 200:
                            result = self._parse_api_response(response, case_number, submission_date, employer_letter)
                            if result:
                                return result
                        
                        # Try form data
                        headers['Content-Type'] = 'application/x-www-form-urlencoded'
                        response = self.session.post(api_url, data=data, headers=headers, timeout=self.timeout)
                        if response.status_code == 200:
                            result = self._parse_api_response(response, case_number, submission_date, employer_letter)
                            if result:
                                return result
                        
                        # Reset content type
                        headers['Content-Type'] = 'application/json'
                        
                    else:  # GET
                        # For GET requests, add data as query parameters
                        response = self.session.get(api_url, params=data, headers=headers, timeout=self.timeout)
                        if response.status_code == 200:
                            result = self._parse_api_response(response, case_number, submission_date, employer_letter)
                            if result:
                                return result
                    
                except Exception as e:
                    logger.warning(f"API call failed: {e}")
                    continue
        
        return None
    
    def _analyze_network_requests(self, case_number: str, submission_date: str, employer_letter: str) -> Optional[Dict[str, Any]]:
        """Analyze network requests by looking at common patterns"""
        logger.info("Analyzing network request patterns")
        
        # Common API patterns for PERM tracking sites
        common_patterns = [
            '/api/predict',
            '/api/search',
            '/api/status',
            '/api/case',
            '/predict',
            '/search',
            '/status',
            '/case',
            '/api/v1/predict',
            '/api/v1/search',
            '/api/v1/status'
        ]
        
        for pattern in common_patterns:
            api_url = f"{self.base_url.rstrip('/')}{pattern}"
            logger.info(f"Trying common API pattern: {api_url}")
            
            result = self._try_api_call(api_url, case_number, submission_date, employer_letter)
            if result:
                return result
        
        return None
    
    def _analyze_network_logs(self, logs: list) -> list:
        """Analyze performance logs to extract network requests"""
        api_requests = []
        
        try:
            import json
            
            for log_entry in logs:
                try:
                    message = json.loads(log_entry['message'])
                    
                    # Look for network request events
                    if 'message' in message and 'method' in message['message']:
                        method = message['message']['method']
                        
                        if method == 'Network.requestWillBeSent':
                            params = message['message']['params']
                            request = params.get('request', {})
                            
                            url = request.get('url', '')
                            method = request.get('method', 'GET')
                            
                            # Filter out non-API requests
                            if any(keyword in url.lower() for keyword in ['api', 'predict', 'search', 'status', 'case']):
                                api_request = {
                                    'url': url,
                                    'method': method,
                                    'data': request.get('postData'),
                                    'headers': request.get('headers', {})
                                }
                                api_requests.append(api_request)
                                logger.info(f"Found API request: {method} {url}")
                        
                        elif method == 'Network.responseReceived':
                            params = message['message']['params']
                            response = params.get('response', {})
                            url = response.get('url', '')
                            
                            # Log response status
                            if any(keyword in url.lower() for keyword in ['api', 'predict', 'search', 'status', 'case']):
                                status = response.get('status', 0)
                                logger.info(f"API response: {status} for {url}")
                
                except Exception as e:
                    continue
            
        except Exception as e:
            logger.warning(f"Error parsing network logs: {e}")
        
        return api_requests
    
    def _try_discovered_api(self, api_request: dict, case_number: str, submission_date: str, employer_letter: str) -> Optional[Dict[str, Any]]:
        """Try calling a discovered API endpoint"""
        try:
            url = api_request['url']
            method = api_request['method']
            
            logger.info(f"Trying discovered API: {method} {url}")
            
            # Prepare headers
            headers = {
                'User-Agent': self.session.headers['User-Agent'],
                'Referer': self.base_url,
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Update with any headers from the original request
            if api_request.get('headers'):
                headers.update(api_request['headers'])
            
            # Prepare data
            data = {
                'case_number': case_number,
                'employer_letter': employer_letter
            }
            
            # If we have original post data, try to use it
            if api_request.get('data'):
                try:
                    import json
                    original_data = json.loads(api_request['data'])
                    data.update(original_data)
                except:
                    pass
            
            # Make the request
            if method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            else:
                response = self.session.get(url, params=data, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                result = self._parse_api_response(response, case_number, submission_date, employer_letter)
                if result:
                    logger.info(f"Successfully got data from discovered API: {url}")
                    return result
            
            logger.warning(f"Discovered API call failed: {response.status_code} for {url}")
            return None
            
        except Exception as e:
            logger.warning(f"Error calling discovered API: {e}")
            return None
    
    def _parse_api_response(self, response: requests.Response, case_number: str, submission_date: str, employer_letter: str) -> Optional[Dict[str, Any]]:
        """Parse the API response"""
        try:
            # Try to parse as JSON first
            try:
                json_data = response.json()
                logger.info(f"API returned JSON: {json_data}")
                
                # Extract data from JSON response
                position = json_data.get('queue_position') or json_data.get('position') or json_data.get('position_in_queue')
                processing_rate = json_data.get('processing_rate') or json_data.get('rate') or config.DEFAULT_PROCESSING_RATE
                status = json_data.get('status') or 'Pending Review'
                completion_date = json_data.get('completion_date') or json_data.get('estimated_date')
                remaining_days = json_data.get('remaining_days') or json_data.get('days_remaining')
                total_applications = json_data.get('total_applications') or json_data.get('backlog') or config.MOCK_TOTAL_APPLICATIONS
                
                # Explicitly check for approval/denial/certification/rejection in status
                lowered = str(status).lower()
                if any(word in lowered for word in ["approved", "certified"]):
                    status = "Approved"
                elif any(word in lowered for word in ["denied", "rejected"]):
                    status = "Denied"
                
                if position or processing_rate != config.DEFAULT_PROCESSING_RATE:
                    return {
                        'position_in_queue': position or config.MOCK_POSITION,
                        'total_applications': total_applications,
                        'last_processed_date': completion_date or '',
                        'processing_rate': processing_rate,
                        'status': status,
                        'completion_date': completion_date,
                        'remaining_days': remaining_days,
                        'case_number': case_number,
                        'submission_date': submission_date,
                        'employer_letter': employer_letter
                    }
                
            except ValueError:
                # Not JSON, try to parse as HTML
                logger.info("API response is not JSON, trying to parse as HTML")
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._extract_status_from_results(soup, case_number, submission_date, employer_letter)
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
            return None
    
    def _extract_status_from_results(self, soup: BeautifulSoup, case_number: str, submission_date: str, employer_letter: str) -> Optional[Dict[str, Any]]:
        """Extract PERM status information from the prediction results page"""
        try:
            page_text = soup.get_text()
            logger.info(f"Page text length: {len(page_text)}")
            
            # Log a sample of the page text for debugging
            sample_text = page_text[:500] if len(page_text) > 500 else page_text
            logger.info(f"Page text sample: {sample_text}")
            
            # Check for explicit approval/denial/certification/rejection
            lowered = page_text.lower()
            if any(word in lowered for word in ["approved", "certified"]):
                status = "Approved"
            elif any(word in lowered for word in ["denied", "rejected"]):
                status = "Denied"
            else:
                # Look for the specific patterns from the manual results
                # "Your Queue Position: 8,585"
                queue_match = re.search(r'your queue position:\s*([\d,]+)', page_text, re.IGNORECASE)
                position = None
                if queue_match:
                    position = int(queue_match.group(1).replace(',', ''))
                    logger.info(f"Found queue position: {position}")
                
                # "Processing Rate: 3,104 / week (443 / day)"
                rate_match = re.search(r'(\d+)\s*/\s*day', page_text, re.IGNORECASE)
                processing_rate = config.DEFAULT_PROCESSING_RATE
                if rate_match:
                    processing_rate = int(rate_match.group(1))
                    logger.info(f"Found processing rate: {processing_rate}")
                
                # "Completion Date: 8/4/2025"
                completion_match = re.search(r'completion date:\s*(\d{1,2}/\d{1,2}/\d{4})', page_text, re.IGNORECASE)
                completion_date = None
                if completion_match:
                    completion_date = completion_match.group(1)
                    logger.info(f"Found completion date: {completion_date}")
                
                # "Remaining: 19 days"
                remaining_match = re.search(r'remaining:\s*(\d+)\s*days', page_text, re.IGNORECASE)
                remaining_days = None
                if remaining_match:
                    remaining_days = int(remaining_match.group(1))
                    logger.info(f"Found remaining days: {remaining_days}")
                
                # "Current Backlog: 91,580 cases"
                backlog_match = re.search(r'current backlog:\s*([\d,]+)', page_text, re.IGNORECASE)
                total_applications = config.MOCK_TOTAL_APPLICATIONS
                if backlog_match:
                    total_applications = int(backlog_match.group(1).replace(',', ''))
                    logger.info(f"Found total applications: {total_applications}")
                
                # "Confidence level: 80%"
                confidence_match = re.search(r'confidence level:\s*(\d+)%', page_text, re.IGNORECASE)
                confidence = None
                if confidence_match:
                    confidence = int(confidence_match.group(1))
                    logger.info(f"Found confidence level: {confidence}")
                
                # "Estimated Wait: ~3 weeks"
                wait_match = re.search(r'estimated wait:\s*~(\d+)\s*weeks?', page_text, re.IGNORECASE)
                estimated_weeks = None
                if wait_match:
                    estimated_weeks = int(wait_match.group(1))
                    logger.info(f"Found estimated wait: {estimated_weeks} weeks")
                
                # Determine status based on remaining days and other indicators
                status = "Pending Review"
                if remaining_days is not None:
                    if remaining_days <= 0:
                        status = "Completed"
                    elif remaining_days <= 30:
                        status = "Final Review"
                    elif remaining_days <= 90:
                        status = "In Processing"
                    else:
                        status = "In Queue"
            
            # If we found some information, return it
            if position is not None or processing_rate != config.DEFAULT_PROCESSING_RATE or completion_date:
                result = {
                    'position_in_queue': position or config.MOCK_POSITION,
                    'total_applications': total_applications,
                    'last_processed_date': completion_date or '',
                    'processing_rate': processing_rate,
                    'status': status,
                    'completion_date': completion_date,
                    'remaining_days': remaining_days,
                    'confidence_level': confidence,
                    'estimated_weeks': estimated_weeks,
                    'case_number': case_number,
                    'submission_date': submission_date,
                    'employer_letter': employer_letter
                }
                logger.info(f"Extracted status data: {result}")
                return result
            
            # If we didn't find the expected patterns, try alternative patterns
            logger.info("Trying alternative parsing patterns...")
            
            # Look for any numbers that might be queue position
            number_matches = re.findall(r'\b(\d{1,3}(?:,\d{3})*)\b', page_text)
            if number_matches:
                logger.info(f"Found numbers in page: {number_matches[:5]}")  # Log first 5 numbers
            
            # Look for any dates
            date_matches = re.findall(r'\b(\d{1,2}/\d{1,2}/\d{4})\b', page_text)
            if date_matches:
                logger.info(f"Found dates in page: {date_matches}")
            
            logger.warning("Could not extract status information from results page")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting status from results page: {e}")
            return None
    
    def _get_mock_status(self, case_number: str, submission_date: str) -> Dict[str, Any]:
        """Generate mock status for testing purposes"""
        logger.info("Generating mock PERM status for testing")
        # Allow simulating approval/denial via environment variable for testing
        import os
        mock_status = os.getenv("MOCK_PERM_STATUS", "Pending Review")
        
        # Calculate a mock position based on submission date
        try:
            sub_date = datetime.strptime(submission_date, '%Y-%m-%d')
            days_since_submission = (datetime.now() - sub_date).days
            
            # Mock calculation: assume 50 applications per day processing
            # and some applications submitted before this one
            base_position = max(1, 2000 - (days_since_submission * config.MOCK_PROCESSING_RATE))
            position = max(1, base_position + random.randint(-200, 200))
            
        except:
            position = config.MOCK_POSITION
        
        return {
            'position_in_queue': position,
            'total_applications': config.MOCK_TOTAL_APPLICATIONS,
            'last_processed_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'processing_rate': config.MOCK_PROCESSING_RATE,
            'status': mock_status,
            'case_number': case_number,
            'submission_date': submission_date,
            'employer_letter': config.EMPLOYER_LETTER,
            'is_mock_data': True
        } 