"""
Cloudflare API service for DNS management operations.
Centralizes all Cloudflare API interactions with proper error handling.
"""

import logging
import requests
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from constants import CloudflareAPI, Headers, Config
from utils.helpers import format_timestamp

logger = logging.getLogger(__name__)


class CloudflareAPIError(Exception):
    """Custom exception for Cloudflare API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        errors: Optional[List] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(self.message)


class CloudflareService:
    """
    Service class for Cloudflare API operations.
    """

    def __init__(self, email: str, api_key: str):
        """
        Initialize the service with credentials.

        Args:
            email: Cloudflare account email
            api_key: Cloudflare Global API Key
        """
        self.email = email
        self.api_key = api_key
        self.headers = Headers.cloudflare_auth(email, api_key)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request to Cloudflare API with error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: API endpoint URL
            **kwargs: Additional request parameters

        Returns:
            Response object

        Raises:
            CloudflareAPIError: If request fails
        """
        try:
            kwargs.setdefault("headers", self.headers)
            kwargs.setdefault("timeout", Config.CLOUDFLARE_API_TIMEOUT)

            logger.debug(f"Making {method} request to {url}")

            response = requests.request(method, url, **kwargs)

            # Log response details
            logger.debug(f"Response status: {response.status_code}")

            if not response.ok:
                error_msg = f"Cloudflare API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "errors" in error_data:
                        error_msg += f" - {error_data['errors']}"
                except:
                    error_msg += f" - {response.text}"

                raise CloudflareAPIError(error_msg, status_code=response.status_code)

            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in Cloudflare API request: {e}")
            raise CloudflareAPIError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Cloudflare API request: {e}")
            raise CloudflareAPIError(f"Unexpected error: {str(e)}")

    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parse and validate Cloudflare API response.

        Args:
            response: HTTP response object

        Returns:
            Parsed response data

        Raises:
            CloudflareAPIError: If response is invalid
        """
        try:
            data = response.json()
        except ValueError as e:
            raise CloudflareAPIError(f"Invalid JSON response: {e}")

        if not data.get("success", False):
            errors = data.get("errors", ["Unknown error"])
            raise CloudflareAPIError(f"API returned error: {errors}", errors=errors)

        return data

    async def get_zones(self) -> List[Dict[str, Any]]:
        """
        Fetch all zones from Cloudflare account.

        Returns:
            List of zone dictionaries with id, name, and status

        Raises:
            CloudflareAPIError: If API request fails
        """
        try:
            response = self._make_request("GET", CloudflareAPI.zones_endpoint())
            data = self._parse_response(response)

            zones = []
            for zone in data.get("result", []):
                zones.append(
                    {
                        "id": zone["id"],
                        "name": zone["name"],
                        "status": zone["status"],
                        "created_on": zone.get("created_on"),
                        "modified_on": zone.get("modified_on"),
                    }
                )

            logger.info(f"Successfully fetched {len(zones)} zones")
            return zones

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error fetching zones: {e}")
            raise CloudflareAPIError(f"Failed to fetch zones: {str(e)}")

    async def get_dns_records(self, zone_id: str) -> List[Dict[str, Any]]:
        """
        Fetch all DNS records for a specific zone.

        Args:
            zone_id: Cloudflare zone ID

        Returns:
            List of DNS record dictionaries

        Raises:
            CloudflareAPIError: If API request fails
        """
        try:
            response = self._make_request(
                "GET", CloudflareAPI.dns_records_endpoint(zone_id)
            )
            data = self._parse_response(response)

            records = []
            for record in data.get("result", []):
                formatted_record = {
                    "id": record.get("id"),
                    "type": record.get("type"),
                    "name": record.get("name"),
                    "content": record.get("content"),
                    "ttl": record.get("ttl"),
                    "proxied": record.get("proxied", False),
                    "locked": record.get("locked", False),
                    "created_on": record.get("created_on"),
                    "modified_on": record.get("modified_on"),
                    "zone_id": record.get("zone_id"),
                    "zone_name": record.get("zone_name"),
                }

                # Add priority for MX records
                if record.get("type") == "MX" and "priority" in record:
                    formatted_record["priority"] = record["priority"]

                # Add additional data if present
                if "data" in record and record["data"]:
                    formatted_record["data"] = record["data"]

                records.append(formatted_record)

            logger.info(
                f"Successfully fetched {len(records)} DNS records for zone {zone_id}"
            )
            return records

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error fetching DNS records for zone {zone_id}: {e}")
            raise CloudflareAPIError(f"Failed to fetch DNS records: {str(e)}")

    async def create_dns_record(
        self, zone_id: str, record_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new DNS record.

        Args:
            zone_id: Cloudflare zone ID
            record_data: DNS record data (type, name, content, etc.)

        Returns:
            Created DNS record data

        Raises:
            CloudflareAPIError: If API request fails
        """
        try:
            response = self._make_request(
                "POST", CloudflareAPI.dns_records_endpoint(zone_id), json=record_data
            )
            data = self._parse_response(response)

            record = data.get("result", {})
            logger.info(
                f"Successfully created DNS record {record.get('id')} in zone {zone_id}"
            )
            return record

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error creating DNS record in zone {zone_id}: {e}")
            raise CloudflareAPIError(f"Failed to create DNS record: {str(e)}")

    async def update_dns_record(
        self, zone_id: str, record_id: str, record_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing DNS record.

        Args:
            zone_id: Cloudflare zone ID
            record_id: DNS record ID to update
            record_data: Updated DNS record data

        Returns:
            Updated DNS record data

        Raises:
            CloudflareAPIError: If API request fails
        """
        try:
            response = self._make_request(
                "PUT",
                CloudflareAPI.dns_record_endpoint(zone_id, record_id),
                json=record_data,
            )
            data = self._parse_response(response)

            record = data.get("result", {})
            logger.info(
                f"Successfully updated DNS record {record_id} in zone {zone_id}"
            )
            return record

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(
                f"Error updating DNS record {record_id} in zone {zone_id}: {e}"
            )
            raise CloudflareAPIError(f"Failed to update DNS record: {str(e)}")

    async def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """
        Delete a DNS record.

        Args:
            zone_id: Cloudflare zone ID
            record_id: DNS record ID to delete

        Returns:
            True if deletion was successful

        Raises:
            CloudflareAPIError: If API request fails
        """
        try:
            response = self._make_request(
                "DELETE", CloudflareAPI.dns_record_endpoint(zone_id, record_id)
            )
            data = self._parse_response(response)

            logger.info(
                f"Successfully deleted DNS record {record_id} from zone {zone_id}"
            )
            return True

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(
                f"Error deleting DNS record {record_id} from zone {zone_id}: {e}"
            )
            raise CloudflareAPIError(f"Failed to delete DNS record: {str(e)}")

    async def get_dns_record(self, zone_id: str, record_id: str) -> Dict[str, Any]:
        """
        Get details of a specific DNS record.

        Args:
            zone_id: Cloudflare zone ID
            record_id: DNS record ID

        Returns:
            DNS record data

        Raises:
            CloudflareAPIError: If API request fails
        """
        try:
            response = self._make_request(
                "GET", CloudflareAPI.dns_record_endpoint(zone_id, record_id)
            )
            data = self._parse_response(response)

            record = data.get("result", {})
            logger.info(
                f"Successfully fetched DNS record {record_id} from zone {zone_id}"
            )
            return record

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(
                f"Error fetching DNS record {record_id} from zone {zone_id}: {e}"
            )
            raise CloudflareAPIError(f"Failed to fetch DNS record: {str(e)}")

    async def verify_credentials(self) -> Tuple[bool, str]:
        """
        Verify if the provided credentials are valid.

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            zones = await self.get_zones()
            return True, f"Credentials verified. Found {len(zones)} zones."
        except CloudflareAPIError as e:
            return False, f"Invalid credentials: {e.message}"
        except Exception as e:
            return False, f"Verification failed: {str(e)}"


def create_cloudflare_service(email: str, api_key: str) -> CloudflareService:
    """
    Factory function to create CloudflareService instance.

    Args:
        email: Cloudflare account email
        api_key: Cloudflare Global API Key

    Returns:
        CloudflareService instance
    """
    return CloudflareService(email, api_key)
