import logging
import asyncio
import aiohttp
import os
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.synthesia_client import SynthesiaClient
from constants import AMA

logger = logging.getLogger(__name__)

async def handle_video_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle video creation request from AMA mode."""
    query = update.callback_query
    await query.answer()
    
    # Get the last AMA response
    last_response = context.user_data.get("last_ama_response")
    if not last_response:
        await query.edit_message_text(
            "❌ No recent response found to create video from. Please ask a question first.",
            reply_markup=None
        )
        return AMA
    
    # Check if video is too long
    if len(last_response) > 2000:
        await query.edit_message_text(
            "❌ Response is too long for video generation (max 2000 characters). Please ask for a shorter response.",
            reply_markup=None
        )
        return AMA
    
    try:
        # Show progress message
        await query.edit_message_text(
            "🎬 Creating your video...\n\n"
            "⏳ This may take 2-5 minutes. You can continue asking questions while I prepare your video.",
            reply_markup=None
        )
        
        # Initialize Synthesia client
        logger.info("Initializing Synthesia client...")
        synthesia = SynthesiaClient()
        logger.info(f"Creating video with script length: {len(last_response)}")
        
        # Create video
        video_result = await synthesia.create_video(
            script=last_response,
            title="NutriBot Advice Video"
        )
        
        if not video_result:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Failed to start video creation. Please try again later."
            )
            return AMA
        
        video_id = video_result.get('id')
        if not video_id:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Failed to get video ID. Please try again later."
            )
            return AMA
        
        # Store video ID for status checking
        context.user_data["pending_video_id"] = video_id
        
        # Start background task to check video status
        asyncio.create_task(check_video_status(context, update.effective_chat.id, video_id))
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ Video creation started! (ID: {video_id[:8]}...)\n\n"
                 "🔔 I'll notify you when your video is ready. You can continue asking questions in the meantime."
        )
        
    except Exception as e:
        logger.error(f"Video creation error: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error creating video. Please try again later."
        )
    
    return AMA

async def check_video_status(context: ContextTypes.DEFAULT_TYPE, chat_id: int, video_id: str):
    """Background task to check video status and send when ready."""
    synthesia = SynthesiaClient()
    max_attempts = 60  # Check for up to 10 minutes (60 * 10 seconds)
    attempt = 0
    
    try:
        while attempt < max_attempts:
            await asyncio.sleep(10)  # Wait 10 seconds between checks
            attempt += 1
            
            status = await synthesia.get_video_status(video_id)
            if not status:
                continue
                
            video_status = status.get('status')
            logger.info(f"Video {video_id} status: {video_status}")
            
            if video_status == 'complete':
                # Video is ready - download and send directly
                download_url = status.get('download')
                if download_url:
                    try:
                        # Download video data directly to memory
                        async with aiohttp.ClientSession() as session:
                            async with session.get(download_url) as video_response:
                                if video_response.status == 200:
                                    # Read entire video into memory
                                    video_data = await video_response.read()
                                    
                                    # Send video directly from memory using BytesIO
                                    video_buffer = io.BytesIO(video_data)
                                    video_buffer.name = f"nutribot_advice_{video_id[:8]}.mp4"
                                    
                                    await context.bot.send_video(
                                        chat_id=chat_id,
                                        video=video_buffer,
                                        caption="🎉 Your NutriBot advice video is ready!\n\n💡 This video contains your previous gardening/composting advice.",
                                        supports_streaming=True
                                    )
                                        
                                else:
                                    # Fallback message if download fails
                                    await context.bot.send_message(
                                        chat_id=chat_id,
                                        text="🎉 Your video is ready!\n\n📹 Video processing complete. "
                                    )
                    except Exception as e:
                        logger.error(f"Error downloading/sending video: {e}")
                        # Fallback message
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text="🎉 Your video is ready!\n\n📹 Video processing complete."
                        )
                else:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="✅ Your video is complete, but I couldn't get the download link. Please check your Synthesia dashboard."
                    )
                break
                
            elif video_status == 'failed':
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ Video creation failed. Please try again with a different response."
                )
                break
                
            elif video_status in ['in_progress', 'queued']:
                # Still processing, continue waiting
                if attempt % 6 == 0:  # Send update every minute
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"⏳ Your video is still being created... ({attempt//6} min elapsed)"
                    )
                continue
                
        if attempt >= max_attempts:
            await context.bot.send_message(
                chat_id=chat_id,
                text="⏰ Video creation is taking longer than expected. Please check your Synthesia dashboard later."
            )
            
    except Exception as e:
        logger.error(f"Error checking video status: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Error checking video status. Please check your Synthesia dashboard."
        )