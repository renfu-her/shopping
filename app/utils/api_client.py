"""
API client utilities for making API calls from backend/frontend controllers.
"""
import requests
from flask import session, request as flask_request
from typing import Optional, Dict, Any
import json

class APIClient:
    """
    Client for making API calls.
    Uses session cookies for authentication.
    """
    
    def __init__(self, base_url: str = 'http://localhost:5000/api/v1'):
        self.base_url = base_url
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with session cookies."""
        headers = {'Content-Type': 'application/json'}
        # Copy session cookies if available
        if hasattr(flask_request, 'cookies'):
            cookie_header = '; '.join([f'{k}={v}' for k, v in flask_request.cookies.items()])
            if cookie_header:
                headers['Cookie'] = cookie_header
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     files: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request data (for JSON requests)
            files: Files for multipart requests
            
        Returns:
            Response data dictionary
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        # Handle multipart/form-data
        if files:
            # Remove Content-Type for multipart requests
            headers.pop('Content-Type', None)
            response = requests.request(method, url, data=data, files=files, 
                                      headers=headers, cookies=flask_request.cookies)
        else:
            response = requests.request(method, url, json=data, headers=headers,
                                      cookies=flask_request.cookies)
        
        try:
            return response.json()
        except:
            return {'success': False, 'message': 'Invalid JSON response'}
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request."""
        url = f"{self.base_url}{endpoint}"
        if params:
            url += '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
        headers = self._get_headers()
        response = requests.get(url, headers=headers, cookies=flask_request.cookies)
        try:
            return response.json()
        except:
            return {'success': False, 'message': 'Invalid JSON response'}
    
    def post(self, endpoint: str, data: Optional[Dict] = None, 
             files: Optional[Dict] = None) -> Dict[str, Any]:
        """POST request."""
        return self._make_request('POST', endpoint, data, files)
    
    def put(self, endpoint: str, data: Optional[Dict] = None,
            files: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT request."""
        return self._make_request('PUT', endpoint, data, files)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE request."""
        return self._make_request('DELETE', endpoint)

# Global API client instance
api_client = APIClient()

