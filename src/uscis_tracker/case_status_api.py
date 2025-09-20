"""
Case Status API Module
Fetches USCIS case status from the official USCIS API using OAuth2 authentication
Supports I-140, I-485, I-765, I-131, I-129, and other USCIS case types
"""

import requests
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from . import config
import base64

logger = logging.getLogger(__name__)


class CaseStatusAPI:
    """API client for USCIS case status using the official USCIS API with OAuth2 authentication"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        
        # USCIS API OAuth2 Configuration from config
        self.client_id = config.USCIS_CLIENT_ID
        self.client_secret = config.USCIS_CLIENT_SECRET
        self.access_token_url = config.USCIS_ACCESS_TOKEN_URL
        self.api_base_url = config.USCIS_API_BASE_URL
        self.timeout = config.SCRAPER_TIMEOUT
        self.retries = config.SCRAPER_RETRIES
        self.access_token = None
    
    def get_case_status(self, case_number: str) -> Optional[Dict[str, Any]]:
        """Get USCIS case status from the official USCIS API"""
        try:
            logger.info(f"Fetching USCIS status for case {case_number}")
            if getattr(config, 'ENABLE_MOCK_DATA', False):
                logger.info("Mock data is enabled, using mock status")
                return self._get_mock_status(case_number)
            
            # Get access token if not already obtained
            if not self.access_token:
                self.access_token = self._get_access_token()
                if not self.access_token:
                    logger.error("Failed to obtain access token")
                    return None
            
            # Use the official USCIS API with authentication
            status = self._get_status_from_api(case_number)
            if status:
                return status
            
            # Fallback to web scraping if API fails
            logger.warning("API failed, trying web scraping fallback...")
            status = self._get_status_from_web_scraping(case_number)
            if status:
                return status
            
            logger.error("Failed to retrieve case status from both API and web scraping")
            return None
            
        except Exception as e:
            logger.error(f"Error getting USCIS status: {e}")
            return None
    
    def _get_access_token(self) -> Optional[str]:
        """Get OAuth2 access token from USCIS API"""
        try:
            logger.info("Obtaining OAuth2 access token from USCIS API")
            
            # Create Basic Auth header with Client ID and Client Secret
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            # OAuth2 token request data
            data = {
                'grant_type': 'client_credentials',
                'scope': 'case-status'
            }
            
            response = self.session.post(self.access_token_url, headers=headers, data=data, timeout=self.timeout)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                if access_token:
                    logger.info("Successfully obtained OAuth2 access token")
                    return access_token
                else:
                    logger.error("No access token in response")
                    return None
            else:
                logger.error(f"Failed to obtain access token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error obtaining access token: {e}")
            return None
    
    def _get_status_from_api(self, case_number: str) -> Optional[Dict[str, Any]]:
        """Get case status from official USCIS API with OAuth2 authentication"""
        import time
        import random
        
        for attempt in range(self.retries):
            try:
                logger.info(f"Using official USCIS API with OAuth2 authentication (attempt {attempt + 1}/{self.retries})")
                
                # Add Bearer token to headers
                headers = {
                    'Authorization': f'Bearer {self.access_token}',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
                
                # Construct API endpoint
                api_endpoint = f"{self.api_base_url}/{case_number}"
                
                logger.info(f"Calling USCIS API: {api_endpoint}")
                response = self.session.get(api_endpoint, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        logger.info("Successfully retrieved case status from USCIS API")
                        return self._parse_api_response(data, case_number)
                    except ValueError as e:
                        logger.error(f"Error parsing JSON response: {e}")
                        return self._parse_text_response(response.text, case_number)
                elif response.status_code == 401:
                    logger.warning("Access token expired, trying to refresh")
                    # Try to get a new access token
                    self.access_token = self._get_access_token()
                    if self.access_token:
                        return self._get_status_from_api(case_number)  # Retry with new token
                    else:
                        return self._create_unauthorized_response(case_number)
                elif response.status_code == 404:
                    logger.warning(f"Case not found: {case_number}")
                    return self._create_not_found_response(case_number)
                elif response.status_code == 503:
                    if attempt < self.retries - 1:
                        # Exponential backoff with jitter
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Service unavailable (503) - attempt {attempt + 1}/{self.retries}. Retrying in {wait_time:.1f} seconds...")
                        logger.info(f"Response headers: {dict(response.headers)}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Service unavailable after all retries")
                        logger.error(f"Final response: {response.status_code} - {response.text[:200]}")
                        return self._create_service_unavailable_response(case_number)
                else:
                    logger.warning(f"USCIS API call failed: {response.status_code}")
                    if attempt < self.retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.info(f"Retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                        continue
                    return None
                    
            except Exception as e:
                logger.error(f"Error calling USCIS API (attempt {attempt + 1}): {e}")
                if attempt < self.retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                return None
        
        return None
    
    def _get_status_from_web_scraping(self, case_number: str) -> Optional[Dict[str, Any]]:
        """Fallback method using web scraping when API fails"""
        try:
            logger.info("Attempting web scraping fallback...")
            
            # Use the USCIS case status website
            url = "https://egov.uscis.gov/casestatus/mycasestatus.do"
            
            # Prepare form data
            form_data = {
                'appReceiptNum': case_number,
                'initCaseSearch': 'CHECK STATUS'
            }
            
            # Make POST request
            response = self.session.post(url, data=form_data, timeout=self.timeout)
            
            if response.status_code == 200:
                # Parse the response using BeautifulSoup
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for status information
                status_div = soup.find('div', class_='rows text-center')
                if status_div:
                    status_text = status_div.get_text(strip=True)
                    if status_text and 'not found' not in status_text.lower():
                        form_type = self._extract_form_type(case_number)
                        case_type = self._determine_case_type(form_type)
                        
                        return {
                            'case_number': case_number,
                            'status': status_text,
                            'last_updated': datetime.now().strftime('%Y-%m-%d'),
                            'form_type': form_type,
                            'case_type': case_type,
                            'office': 'USCIS Service Center',
                            'details': 'Retrieved via web scraping fallback',
                            'data_source': 'uscis.gov',
                            'method': 'web_scraping_fallback'
                        }
            
            logger.warning("Web scraping fallback also failed")
            return None
            
        except Exception as e:
            logger.error(f"Error in web scraping fallback: {e}")
            return None
    
    def _parse_api_response(self, data: dict, case_number: str) -> Optional[Dict[str, Any]]:
        """Parse the USCIS API JSON response"""
        try:
            # Handle different possible response structures
            status = data.get('status') or data.get('caseStatus') or data.get('statusText', 'Unknown')
            last_updated = data.get('lastUpdated') or data.get('updatedDate') or data.get('lastModified', '')
            form_type = data.get('formType') or data.get('form') or self._extract_form_type(case_number)
            office = data.get('office') or data.get('serviceCenter') or 'USCIS Service Center'
            details = data.get('details') or data.get('description') or data.get('message', '')
            case_type = self._determine_case_type(form_type)
            
            return {
                'case_number': case_number,
                'status': status,
                'last_updated': last_updated,
                'form_type': form_type,
                'case_type': case_type,
                'office': office,
                'details': details,
                'data_source': 'uscis.gov',
                'api_response': data,
                'method': 'official_api_oauth2'
            }
        except Exception as e:
            logger.error(f"Error parsing USCIS API response: {e}")
            return None
    
    def _parse_text_response(self, text_content: str, case_number: str) -> Optional[Dict[str, Any]]:
        """Parse text response when JSON parsing fails"""
        try:
            # Try to extract status information from text
            lines = text_content.split('\n')
            status_text = "Status not found"
            
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in ['received', 'approved', 'denied', 'pending', 'processing']):
                    status_text = line
                    break
            
            form_type = self._extract_form_type(case_number)
            case_type = self._determine_case_type(form_type)
            
            return {
                'case_number': case_number,
                'status': status_text,
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'form_type': form_type,
                'case_type': case_type,
                'office': 'USCIS Service Center',
                'details': text_content[:200] + "..." if len(text_content) > 200 else text_content,
                'data_source': 'uscis.gov',
                'raw_response': text_content,
                'method': 'api_text'
            }
        except Exception as e:
            logger.error(f"Error parsing text response: {e}")
            return None
    
    def _create_not_found_response(self, case_number: str) -> Dict[str, Any]:
        """Create response for case not found"""
        form_type = self._extract_form_type(case_number)
        case_type = self._determine_case_type(form_type)
        
        return {
            'case_number': case_number,
            'status': 'Case Not Found',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'form_type': form_type,
            'case_type': case_type,
            'office': 'USCIS Service Center',
            'details': 'The case number was not found in the USCIS system.',
            'data_source': 'uscis.gov',
            'method': 'official_api_oauth2',
            'error': 'case_not_found'
        }
    
    def _create_unauthorized_response(self, case_number: str) -> Dict[str, Any]:
        """Create response for unauthorized access"""
        form_type = self._extract_form_type(case_number)
        case_type = self._determine_case_type(form_type)
        
        return {
            'case_number': case_number,
            'status': 'Access Denied',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'form_type': form_type,
            'case_type': case_type,
            'office': 'USCIS Service Center',
            'details': 'API access requires authentication.',
            'data_source': 'uscis.gov',
            'method': 'official_api_oauth2',
            'error': 'unauthorized'
        }
    
    def _create_service_unavailable_response(self, case_number: str) -> Dict[str, Any]:
        """Create response for service unavailable (503)"""
        form_type = self._extract_form_type(case_number)
        case_type = self._determine_case_type(form_type)
        
        return {
            'case_number': case_number,
            'status': 'Service Temporarily Unavailable',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'form_type': form_type,
            'case_type': case_type,
            'office': 'USCIS Service Center',
            'details': 'The USCIS API is temporarily unavailable. Please try again later.',
            'data_source': 'uscis.gov',
            'method': 'official_api_oauth2',
            'error': 'service_unavailable'
        }
    
    def _extract_form_type(self, case_number: str) -> str:
        """Extract form type from case number"""
        if len(case_number) >= 3:
            prefix = case_number[:3]
            # Common USCIS form prefixes
            form_mapping = {
                'YSC': 'I-140',  # Vermont Service Center
                'WAC': 'I-140',  # California Service Center
                'LIN': 'I-140',  # Nebraska Service Center
                'SRC': 'I-140',  # Texas Service Center
                'MSC': 'I-140',  # Missouri Service Center
                'IOE': 'I-140',  # Electronic filing
                'G-': 'I-140',   # General cases
            }
            return form_mapping.get(prefix, prefix)
        return "Unknown"
    
    def _determine_case_type(self, form_type: str) -> str:
        """Determine case type based on form type"""
        case_mapping = {
            'I-140': 'Immigrant Petition for Alien Worker',
            'I-485': 'Application to Register Permanent Residence',
            'I-765': 'Application for Employment Authorization',
            'I-131': 'Application for Travel Document',
            'I-129': 'Petition for Nonimmigrant Worker',
        }
        return case_mapping.get(form_type, 'Unknown Case Type')

    def _get_mock_status(self, case_number: str) -> Dict[str, Any]:
        """Generate mock status for testing purposes"""
        logger.info("Generating mock USCIS status for testing")
        import os
        mock_status = os.getenv("MOCK_USCIS_STATUS", "Case Was Received")
        form_type = self._extract_form_type(case_number)
        case_type = self._determine_case_type(form_type)
        
        return {
            'case_number': case_number,
            'status': mock_status,
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'form_type': form_type,
            'case_type': case_type,
            'office': 'California Service Center',
            'details': 'Your case was received and a receipt notice was sent.',
            'is_mock_data': True,
            'method': 'mock'
        }
