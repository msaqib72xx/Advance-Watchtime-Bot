#!/usr/bin/env python3
"""
YouTube HumanWatch Pro - Advanced Watch Time Simulation System
Educational Project - For Research Purposes Only
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime

# Import our modules
from bot_advanced import YouTubeWatchTimeBotAdvanced
from session_orchestrator import SessionOrchestrator
from stealth_manager import StealthManager

def print_banner():
    """Print professional banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║   🎬 YOUTUBE HUMANWATCH PRO v3.0                                 ║
    ║   Advanced Behavioral Simulation Engine                         ║
    ║   Educational & Research Project                                ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_disclaimer():
    """Print ethical disclaimer"""
    disclaimer = """
    ⚠️  ETHICAL & LEGAL DISCLAIMER:
    ====================================================================
    THIS SOFTWARE IS DEVELOPED STRICTLY FOR:
    - Educational purposes (University projects, research)
    - Learning web automation and anti-detection techniques
    - Understanding browser fingerprinting and behavior analysis
    
    STRICTLY PROHIBITED:
    - Artificially inflating YouTube watch time or views
    - Use on real YouTube accounts or monetized videos
    - Any activity violating YouTube's Terms of Service
    
    WARNING:
    - Violation may result in account termination
    - Legal consequences may apply
    - Use at your own risk for educational purposes only
    ====================================================================
    """
    print(disclaimer)

async def run_single_session(config_file: str, video_url: str):
    """Run a single advanced session"""
    print(f"\n🎯 Starting single session for: {video_url}")
    
    bot = YouTubeWatchTimeBotAdvanced(config_file)
    result = await bot.run_advanced_session(video_url)
    
    return result

async def run_campaign(config_file: str, video_url: str, sessions: int):
    """Run a coordinated campaign"""
    print(f"\n🎬 Starting campaign: {sessions} sessions")
    
    orchestrator = SessionOrchestrator(config_file)
    results = await orchestrator.run_campaign(video_url, sessions)
    
    return results

def show_statistics():
    """Display session statistics"""
    try:
        import sqlite3
        import pandas as pd
        from tabulate import tabulate
        
        conn = sqlite3.connect('database/sessions.db')
        
        # Get today's stats
        today = datetime.now().strftime('%Y-%m-%d')
        query = """
        SELECT 
            COUNT(*) as total_sessions,
            SUM(duration_seconds) as total_watch_time,
            AVG(duration_seconds) as avg_duration,
            (SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
        FROM sessions 
        WHERE DATE(start_time) = ?
        """
        
        df = pd.read_sql_query(query, conn, params=(today,))
        
        if not df.empty and df['total_sessions'].iloc[0] > 0:
            print("\n📊 TODAY'S STATISTICS")
            print("=" * 60)
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        
        # Recent sessions
        recent_query = """
        SELECT 
            session_id,
            video_url,
            start_time,
            duration_seconds,
            viewer_type,
            success,
            drop_detected
        FROM sessions 
        ORDER BY start_time DESC 
        LIMIT 10
        """
        
        recent_df = pd.read_sql_query(recent_query, conn)
        
        if not recent_df.empty:
            print(f"\n📋 RECENT SESSIONS (Last 10)")
            print("=" * 60)
            print(tabulate(recent_df, headers='keys', tablefmt='grid', showindex=False))
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️  Could not load statistics: {e}")

def export_data(format_type: str = 'csv'):
    """Export session data"""
    try:
        import sqlite3
        import pandas as pd
        import json as json_lib
        
        conn = sqlite3.connect('database/sessions.db')
        df = pd.read_sql_query("SELECT * FROM sessions", conn)
        conn.close()
        
        if format_type == 'csv':
            filename = f"session_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Data exported to CSV: {filename}")
            
        elif format_type == 'json':
            filename = f"session_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            df.to_json(filename, orient='records', indent=2)
            print(f"✅ Data exported to JSON: {filename}")
            
        elif format_type == 'excel':
            filename = f"session_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            print(f"✅ Data exported to Excel: {filename}")
            
        return filename
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return None

def main():
    """Main function"""
    
    # Print banner and disclaimer
    print_banner()
    print_disclaimer()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='YouTube HumanWatch Pro - Advanced Watch Time Simulation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url https://youtube.com/watch?v=VIDEO_ID
  %(prog)s --url https://youtube.com/watch?v=VIDEO_ID --sessions 3
  %(prog)s --gui
  %(prog)s --stats
  %(prog)s --export csv
        """
    )
    
    parser.add_argument('--url', type=str, help='YouTube video URL')
    parser.add_argument('--sessions', type=int, default=1, help='Number of sessions (default: 1)')
    parser.add_argument('--config', type=str, default='config_advanced.json', help='Configuration file')
    parser.add_argument('--gui', action='store_true', help='Launch GUI interface')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--export', type=str, choices=['csv', 'json', 'excel'], help='Export data')
    parser.add_argument('--quick', action='store_true', help='Run quick test')
    parser.add_argument('--demo', action='store_true', help='Run presentation demo')
    
    args = parser.parse_args()
    
    # GUI Mode
    if args.gui:
        try:
            from gui_pro import YouTubeWatchTimeGUI
            import tkinter as tk
            
            root = tk.Tk()
            app = YouTubeWatchTimeGUI(root)
            root.mainloop()
            return
        except ImportError as e:
            print(f"❌ GUI not available: {e}")
            print("Try: pip install tkinter")
            return
    
    # Statistics mode
    if args.stats:
        show_statistics()
        return
    
    # Export mode
    if args.export:
        export_data(args.export)
        return
    
    # Quick test mode
    if args.quick:
        try:
            from run_quick import quick_test
            success = asyncio.run(quick_test())
            sys.exit(0 if success else 1)
        except ImportError:
            print("❌ Quick test module not found")
            return
    
    # Presentation demo
    if args.demo:
        try:
            from presentation_demo import run_presentation_demo
            asyncio.run(run_presentation_demo())
            return
        except ImportError:
            print("❌ Presentation demo not found")
            return
    
    # Normal execution with URL
    if args.url:
        try:
            if args.sessions == 1:
                result = asyncio.run(run_single_session(args.config, args.url))
                if result.get('success'):
                    print(f"\n✅ Session completed successfully!")
                    print(f"   Watch Time: {result.get('watch_time', 0)} seconds")
                    print(f"   Session ID: {result.get('session_id', 'N/A')}")
                else:
                    print(f"\n❌ Session failed: {result.get('error', 'Unknown error')}")
            else:
                results = asyncio.run(run_campaign(args.config, args.url, args.sessions))
                print(f"\n📊 Campaign Results:")
                print(f"   Successful: {results.get('successful', 0)}/{args.sessions}")
                print(f"   Failed: {results.get('failed', 0)}/{args.sessions}")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Operation interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    else:
        # Interactive mode
        print("\n🔧 INTERACTIVE MODE")
        print("=" * 50)
        print("1. Run single session")
        print("2. Run campaign (multiple sessions)")
        print("3. Show statistics")
        print("4. Export data")
        print("5. Launch GUI")
        print("6. Run presentation demo")
        print("7. Exit")
        
        try:
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                url = input("Enter YouTube URL: ").strip()
                if not url:
                    print("❌ URL is required!")
                    return
                asyncio.run(run_single_session('config_advanced.json', url))
                
            elif choice == "2":
                url = input("Enter YouTube URL: ").strip()
                if not url:
                    print("❌ URL is required!")
                    return
                try:
                    sessions = int(input("Number of sessions (1-10): "))
                    sessions = max(1, min(10, sessions))
                except ValueError:
                    print("⚠️  Invalid number, using 3 sessions")
                    sessions = 3
                asyncio.run(run_campaign('config_advanced.json', url, sessions))
                
            elif choice == "3":
                show_statistics()
                
            elif choice == "4":
                print("Export formats: csv, json, excel")
                fmt = input("Format (default: csv): ").strip().lower()
                if fmt not in ['csv', 'json', 'excel']:
                    fmt = 'csv'
                export_data(fmt)
                
            elif choice == "5":
                try:
                    from gui_pro import YouTubeWatchTimeGUI
                    import tkinter as tk
                    
                    root = tk.Tk()
                    app = YouTubeWatchTimeGUI(root)
                    root.mainloop()
                except ImportError as e:
                    print(f"❌ GUI not available: {e}")
                    
            elif choice == "6":
                try:
                    from presentation_demo import run_presentation_demo
                    asyncio.run(run_presentation_demo())
                except ImportError:
                    print("❌ Presentation demo not found")
                    
            elif choice == "7":
                print("👋 Goodbye!")
                sys.exit(0)
                
            else:
                print("❌ Invalid choice!")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Operation interrupted by user")
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Program terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)