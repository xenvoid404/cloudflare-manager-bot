"""
Cloudflare API service untuk operasi manajemen DNS.
Mengumpulkan semua interaksi Cloudflare API dengan penanganan error yang tepat.
"""

import logging
import requests
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from constants import CloudflareAPI, Headers, Config
from utils.helpers import format_timestamp

logger = logging.getLogger(__name__)


class CloudflareAPIError(Exception):
    """Exception kustom untuk error Cloudflare API."""

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
    Service class untuk operasi Cloudflare API.
    """

    def __init__(self, email: str, api_key: str):
        """
        Inisialisasi service dengan kredensial.

        Args:
            email: Email akun Cloudflare
            api_key: Cloudflare Global API Key
        """
        self.email = email
        self.api_key = api_key
        self.headers = Headers.cloudflare_auth(email, api_key)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Buat HTTP request ke Cloudflare API dengan penanganan error.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            url: API endpoint URL
            **kwargs: Parameter request tambahan

        Returns:
            Objek Response

        Raises:
            CloudflareAPIError: Jika request gagal
        """
        try:
            kwargs.setdefault("headers", self.headers)
            kwargs.setdefault("timeout", Config.CLOUDFLARE_API_TIMEOUT)

            logger.debug(f"Melakukan {method} request ke {url}")

            response = requests.request(method, url, **kwargs)

            # Log detail response
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
            logger.error(f"Network error dalam Cloudflare API request: {e}")
            raise CloudflareAPIError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Error tidak terduga dalam Cloudflare API request: {e}")
            raise CloudflareAPIError(f"Error tidak terduga: {str(e)}")

    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parse dan validasi response Cloudflare API.

        Args:
            response: Objek HTTP response

        Returns:
            Data response yang diparsing

        Raises:
            CloudflareAPIError: Jika response tidak valid
        """
        try:
            data = response.json()
        except ValueError as e:
            raise CloudflareAPIError(f"JSON response tidak valid: {e}")

        if not data.get("success", False):
            errors = data.get("errors", ["Error tidak diketahui"])
            raise CloudflareAPIError(f"API mengembalikan error: {errors}", errors=errors)

        return data

    async def get_zones(self) -> List[Dict[str, Any]]:
        """
        Ambil semua zona dari akun Cloudflare.

        Returns:
            Daftar kamus zona dengan id, nama, dan status

        Raises:
            CloudflareAPIError: Jika request API gagal
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

            logger.info(f"Berhasil mengambil {len(zones)} zona")
            return zones

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error mengambil zona: {e}")
            raise CloudflareAPIError(f"Gagal mengambil zona: {str(e)}")

    async def get_dns_records(self, zone_id: str) -> List[Dict[str, Any]]:
        """
        Ambil semua rekaman DNS untuk zona tertentu.

        Args:
            zone_id: ID zona Cloudflare

        Returns:
            Daftar kamus rekaman DNS

        Raises:
            CloudflareAPIError: Jika request API gagal
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

                # Tambahkan prioritas untuk rekaman MX
                if record.get("type") == "MX" and "priority" in record:
                    formatted_record["priority"] = record["priority"]

                # Tambahkan data tambahan jika ada
                if "data" in record and record["data"]:
                    formatted_record["data"] = record["data"]

                records.append(formatted_record)

            logger.info(
                f"Berhasil mengambil {len(records)} rekaman DNS untuk zona {zone_id}"
            )
            return records

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error mengambil rekaman DNS untuk zona {zone_id}: {e}")
            raise CloudflareAPIError(f"Gagal mengambil rekaman DNS: {str(e)}")

    async def create_dns_record(
        self, zone_id: str, record_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Buat rekaman DNS baru.

        Args:
            zone_id: ID zona Cloudflare
            record_data: Data rekaman DNS (tipe, nama, konten, dll.)

        Returns:
            Data rekaman DNS yang dibuat

        Raises:
            CloudflareAPIError: Jika request API gagal
        """
        try:
            response = self._make_request(
                "POST", CloudflareAPI.dns_records_endpoint(zone_id), json=record_data
            )
            data = self._parse_response(response)

            record = data.get("result", {})
            logger.info(
                f"Berhasil membuat rekaman DNS {record.get('id')} di zona {zone_id}"
            )
            return record

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(f"Error membuat rekaman DNS di zona {zone_id}: {e}")
            raise CloudflareAPIError(f"Gagal membuat rekaman DNS: {str(e)}")

    async def update_dns_record(
        self, zone_id: str, record_id: str, record_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perbarui rekaman DNS yang ada.

        Args:
            zone_id: ID zona Cloudflare
            record_id: ID rekaman DNS untuk diperbarui
            record_data: Data rekaman DNS yang diperbarui

        Returns:
            Data rekaman DNS yang diperbarui

        Raises:
            CloudflareAPIError: Jika request API gagal
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
                f"Berhasil memperbarui rekaman DNS {record_id} di zona {zone_id}"
            )
            return record

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(
                f"Error memperbarui rekaman DNS {record_id} di zona {zone_id}: {e}"
            )
            raise CloudflareAPIError(f"Gagal memperbarui rekaman DNS: {str(e)}")

    async def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """
        Hapus rekaman DNS.

        Args:
            zone_id: ID zona Cloudflare
            record_id: ID rekaman DNS untuk dihapus

        Returns:
            True jika penghapusan berhasil

        Raises:
            CloudflareAPIError: Jika request API gagal
        """
        try:
            response = self._make_request(
                "DELETE", CloudflareAPI.dns_record_endpoint(zone_id, record_id)
            )
            data = self._parse_response(response)

            logger.info(
                f"Berhasil menghapus rekaman DNS {record_id} dari zona {zone_id}"
            )
            return True

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(
                f"Error menghapus rekaman DNS {record_id} dari zona {zone_id}: {e}"
            )
            raise CloudflareAPIError(f"Gagal menghapus rekaman DNS: {str(e)}")

    async def get_dns_record(self, zone_id: str, record_id: str) -> Dict[str, Any]:
        """
        Dapatkan detail rekaman DNS spesifik.

        Args:
            zone_id: ID zona Cloudflare
            record_id: ID rekaman DNS

        Returns:
            Data rekaman DNS

        Raises:
            CloudflareAPIError: Jika request API gagal
        """
        try:
            response = self._make_request(
                "GET", CloudflareAPI.dns_record_endpoint(zone_id, record_id)
            )
            data = self._parse_response(response)

            record = data.get("result", {})
            logger.info(
                f"Berhasil mengambil rekaman DNS {record_id} dari zona {zone_id}"
            )
            return record

        except CloudflareAPIError:
            raise
        except Exception as e:
            logger.error(
                f"Error mengambil rekaman DNS {record_id} dari zona {zone_id}: {e}"
            )
            raise CloudflareAPIError(f"Gagal mengambil rekaman DNS: {str(e)}")

    async def verify_credentials(self) -> Tuple[bool, str]:
        """
        Verifikasi apakah kredensial yang diberikan valid.

        Returns:
            Tuple dari (is_valid, pesan)
        """
        try:
            zones = await self.get_zones()
            return True, f"Kredensial diverifikasi. Ditemukan {len(zones)} zona."
        except CloudflareAPIError as e:
            return False, f"Kredensial tidak valid: {e.message}"
        except Exception as e:
            return False, f"Verifikasi gagal: {str(e)}"


def create_cloudflare_service(email: str, api_key: str) -> CloudflareService:
    """
    Fungsi pabrik untuk membuat instance CloudflareService.

    Args:
        email: Email akun Cloudflare
        api_key: Cloudflare Global API Key

    Returns:
        Instance CloudflareService
    """
    return CloudflareService(email, api_key)
