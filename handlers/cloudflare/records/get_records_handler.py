import logging
import json
import io
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any
from telegram import Update, Document
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from database.models.cf_accounts_model import get_cloudflare_account

logger = logging.getLogger(__name__)


async def get_records_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle get_records callback to fetch and display DNS records."""
    try:
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        
        # Get Cloudflare account data
        account = await get_cloudflare_account(user.id)
        
        if not account:
            await query.edit_message_text(
                "❌ Akun Cloudflare tidak ditemukan\\.\n\n"
                "Silakan tambahkan akun Cloudflare terlebih dahulu\\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
        
        # Show loading message
        await query.edit_message_text(
            "🔄 Mengambil daftar DNS records\\.\\.\\.\n"
            "Mohon tunggu sebentar\\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        # Fetch DNS records
        records = await _fetch_dns_records(account)
        
        if records is None:
            await query.edit_message_text(
                "❌ Gagal mengambil DNS records\\.\n\n"
                "Kemungkinan penyebab:\n"
                "• API Key tidak valid\n"
                "• Zone tidak ditemukan\n"
                "• Masalah koneksi internet\n\n"
                "Gunakan /menu untuk mencoba lagi\\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
        
        if not records:
            await query.edit_message_text(
                "📋 *DNS Records*\n\n"
                "Tidak ada DNS records ditemukan di zone ini\\.\n\n"
                "Gunakan /menu untuk kembali ke menu utama\\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
        
        # Format records data
        formatted_data = {
            "zone_info": {
                "zone_name": account.get("zone_name"),
                "zone_id": account.get("zone_id"),
                "email": account.get("email"),
                "total_records": len(records)
            },
            "records": records,
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "exported_by": f"{user.first_name or 'Unknown'} ({user.id})"
            }
        }
        
        # Create JSON file
        json_content = json.dumps(formatted_data, indent=2, ensure_ascii=False)
        json_bytes = io.BytesIO(json_content.encode('utf-8'))
        json_bytes.name = f"dns_records_{account.get('zone_name', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Send file with summary
        summary_text = (
            f"📋 *DNS Records Export*\n\n"
            f"🌐 *Zone:* `{account.get('zone_name', 'N/A')}`\n"
            f"📊 *Total Records:* `{len(records)}`\n"
            f"📅 *Exported:* `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
            f"File JSON berisi semua DNS records dengan format yang rapi\\."
        )
        
        await query.edit_message_text(
            summary_text,
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        # Send the JSON file
        await context.bot.send_document(
            chat_id=user.id,
            document=json_bytes,
            caption=f"📁 DNS Records untuk zone: {account.get('zone_name', 'Unknown')}",
            filename=json_bytes.name
        )
        
        logger.info(f"DNS records exported for user {user.id}, zone: {account.get('zone_name')}")
        
    except Exception as e:
        logger.error(f"Error getting DNS records for user {update.effective_user.id}: {e}")
        try:
            await update.callback_query.edit_message_text(
                "⚠️ Terjadi kesalahan saat mengambil DNS records\\. "
                "Gunakan /menu untuk mencoba lagi\\.",
                parse_mode=ParseMode.MARKDOWN_V2
            )
        except:
            await update.effective_chat.send_message(
                "⚠️ Terjadi kesalahan saat mengambil DNS records. "
                "Gunakan /menu untuk mencoba lagi."
            )


async def _fetch_dns_records(account: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """Fetch DNS records from Cloudflare API."""
    try:
        email = account.get("email")
        api_key = account.get("api_key")
        zone_id = account.get("zone_id")
        
        if not email or not api_key or not zone_id:
            logger.error("Missing required account information")
            return None
        
        # Fetch DNS records
        response = requests.get(
            f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
            headers={
                "X-Auth-Email": email,
                "X-Auth-Key": api_key,
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        
        if not response.ok:
            logger.error(f"Cloudflare API error: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        
        if not data.get("success", False):
            logger.error(f"Cloudflare API returned error: {data.get('errors', [])}")
            return None
        
        records_result = data.get("result", [])
        
        # Format records data
        formatted_records = []
        for record in records_result:
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
                "zone_name": record.get("zone_name")
            }
            
            # Add priority for MX records
            if record.get("type") == "MX" and "priority" in record:
                formatted_record["priority"] = record["priority"]
            
            # Add additional data if present
            if "data" in record and record["data"]:
                formatted_record["data"] = record["data"]
            
            formatted_records.append(formatted_record)
        
        logger.info(f"Successfully fetched {len(formatted_records)} DNS records")
        return formatted_records
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching DNS records: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching DNS records: {e}")
        return None


# Handler exports
get_records_handlers = [
    CallbackQueryHandler(get_records_callback, pattern="^get_records$"),
]