#!/usr/bin/env python3
"""
Quick test script for basic functionality
"""

import asyncio
import sys
from bot_advanced import YouTubeWatchTimeBotAdvanced

async def quick_test():
    bot = YouTubeWatchTimeBotAdvanced()
    result = await bot.run_advanced_session(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with your video
    )
    return result.get('success', False)

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)