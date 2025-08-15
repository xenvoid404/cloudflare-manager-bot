import logging
import json
import io
from datetime import datetime
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from constants import Messages, CallbackData, Emojis
from services.cloudflare_service import create_cloudflare_service, CloudflareAPIError
from utils.decorators import cloudflare_handler
from utils.helpers import format_timestamp, get_export_filename, get_user_display_name, send_response

logger = logging.getLogger(__name__)


@cloudflare_handler
async def get_records_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle get_records callback to fetch and display DNS records."""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    account = context.user_data['cf_account']  # Set by cloudflare_handler decorator
    
    # Show loading message
    await send_response(update, Messages.Common.LOADING)
    
    try:
        # Create Cloudflare service
        cf_service = create_cloudflare_service(
            account.get("email"),
            account.get("api_key")
        )
        
        # Fetch DNS records
        records = await cf_service.get_dns_records(account.get("zone_id"))
        
        if not records:
            await send_response(update, Messages.Records.NO_RECORDS)
            return
        
        # Format records data for export
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
                "exported_by": f"{get_user_display_name(user)} ({user.id})"
            }
        }
        
        # Create JSON file
        json_content = json.dumps(formatted_data, indent=2, ensure_ascii=False)
        json_bytes = io.BytesIO(json_content.encode('utf-8'))
        json_bytes.name = get_export_filename(account.get("zone_name", "unknown"))
        
        # Send summary message
        summary_text = Messages.Records.VIEW_SUMMARY.format(
            zone_name=account.get("zone_name", "N/A"),
            total_records=len(records),
            export_time=format_timestamp()
        )
        
        await send_response(update, summary_text)
        
        # Send the JSON file
        await context.bot.send_document(
            chat_id=user.id,
            document=json_bytes,
            caption=f"{Emojis.FILE} DNS Records untuk zone: {account.get('zone_name', 'Unknown')}",
            filename=json_bytes.name
        )
        
    except CloudflareAPIError as e:
        logger.error(f"Cloudflare API error for user {user.id}: {e}")
        await send_response(update, Messages.Records.FETCH_ERROR)


# Handler exports
get_records_handlers = [
    CallbackQueryHandler(get_records_callback, pattern=f"^{CallbackData.GET_RECORDS}$"),
]