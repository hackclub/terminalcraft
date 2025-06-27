import argparse
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Add debug logging for executable troubleshooting
import os
import logging

def setup_debug_logging():
	"""Setup debug logging for executable troubleshooting"""
	try:
		# Create logs directory if running as executable
		if getattr(sys, 'frozen', False):
			log_dir = Path(sys.executable).parent / "logs"
			log_dir.mkdir(exist_ok=True)
			log_file = log_dir / "meet-zone-debug.log"
		else:
			log_file = "meet-zone-debug.log"
		
		logging.basicConfig(
			level=logging.DEBUG,
			format='%(asctime)s - %(levelname)s - %(message)s',
			handlers=[
				logging.FileHandler(log_file),
				logging.StreamHandler(sys.stdout)
			]
		)
		logging.info("Debug logging initialized")
		return True
	except Exception as e:
		print(f"Failed to setup logging: {e}")
		return False

def main() -> int:
	"""Main entry point with comprehensive error handling"""
	try:
		# Setup debug logging first
		setup_debug_logging()
		logging.info("Starting Meet-Zone application")
		
		# Log Python and system information
		logging.info(f"Python version: {sys.version}")
		logging.info(f"Platform: {sys.platform}")
		logging.info(f"Executable: {sys.executable}")
		logging.info(f"Frozen: {getattr(sys, 'frozen', False)}")
		logging.info(f"Current working directory: {os.getcwd()}")
		
		# Test critical imports first
		logging.info("Testing critical imports...")
		
		try:
			import textual
			logging.info(f"Textual version: {textual.__version__}")
		except ImportError as e:
			logging.error(f"Failed to import textual: {e}")
			raise
		
		try:
			from textual.app import App
			from textual.widgets import TabbedContent, TabPane
			logging.info("Textual widgets imported successfully")
		except ImportError as e:
			logging.error(f"Failed to import textual widgets: {e}")
			raise
		
		try:
			import pytz
			logging.info(f"PyTZ imported successfully")
		except ImportError as e:
			logging.error(f"Failed to import pytz: {e}")
			raise
		
		# Import application modules
		logging.info("Importing application modules...")
		try:
			from meet_zone.parser import parse_roster, Participant
			from meet_zone.scheduler import find_best_slots, TimeSlot
			from meet_zone.ui import display_results, MeetZoneApp
			logging.info("Application modules imported successfully")
		except ImportError as e:
			logging.error(f"Failed to import application modules: {e}")
			raise
		
		# Parse command line arguments
		logging.info("Parsing command line arguments...")
		args = parse_args()
		logging.info(f"Arguments parsed: {vars(args)}")
		
		participants: List[Participant] = []
		best_slots: Optional[List[TimeSlot]] = None
		
		# Determine prioritization strategy
		prioritize_participants = args.prioritize == 'participants'
		
		# If a roster file is provided, load participants and calculate initial slots
		if args.roster_file:
			logging.info(f"Loading roster file: {args.roster_file}")
			try:
				participants = parse_roster(args.roster_file)
				logging.info(f"Loaded {len(participants)} participants")
				
				best_slots = find_best_slots(
					participants=participants,
					min_duration=args.duration,
					show_week=args.week,
					top_k=args.top,
					start_date=args.date,
					prioritize_participants=prioritize_participants
				)
				logging.info(f"Found {len(best_slots) if best_slots else 0} meeting slots")
			except Exception as e:
				logging.error(f"Error processing roster file: {e}")
				# Continue without roster data
		
		# Launch the UI with or without initial data
		logging.info("Launching UI...")
		try:
			app = display_results(
				slots=best_slots,
				participants=participants,
				min_duration=args.duration,
				show_week=args.week,
				prioritize_participants=prioritize_participants,
				start_date=args.date
			)
			logging.info("UI created successfully")
			
			logging.info("Starting application...")
			app.run()
			logging.info("Application completed successfully")
			return 0
			
		except Exception as e:
			logging.error(f"Error launching UI: {e}")
			logging.error(f"Traceback: {traceback.format_exc()}")
			raise
		
	except KeyboardInterrupt:
		logging.info("Application interrupted by user")
		return 0
	except Exception as e:
		error_msg = f"Fatal error: {e}"
		logging.error(error_msg)
		logging.error(f"Full traceback: {traceback.format_exc()}")
		
		# Show error dialog if possible
		try:
			import tkinter as tk
			from tkinter import messagebox
			root = tk.Tk()
			root.withdraw()
			messagebox.showerror("Meet-Zone Error", f"{error_msg}\n\nCheck meet-zone-debug.log for details.")
		except:
			# Fallback to console output
			print(f"\n{error_msg}")
			print("Check meet-zone-debug.log for detailed error information.")
		
		return 1

def parse_args():
	parser = argparse.ArgumentParser(description="Find optimal meeting times across time zones")
	parser.add_argument("roster_file", type=Path, nargs='?', help="Path to CSV roster file (optional)")
	parser.add_argument("--duration", type=int, default=30, help="Minimum meeting duration in minutes")
	parser.add_argument("--top", type=int, default=3, help="Number of top slots to display")
	parser.add_argument("--week", action="store_true", help="Show full week instead of just today")
	parser.add_argument("--prioritize", choices=['participants', 'duration'], default='participants',
				   help="Whether to prioritize maximizing participants or meeting duration")
	parser.add_argument("--date", type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
				   help="Start date for search (format: YYYY-MM-DD, default: today)")
	return parser.parse_args()


if __name__ == "__main__":
	sys.exit(main())
