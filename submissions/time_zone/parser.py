import csv
from dataclasses import dataclass
from datetime import time
from pathlib import Path
from typing import List


@dataclass
class Participant:
	name: str
	tz: str
	start_time: time
	end_time: time


def parse_time(time_str: str) -> time:
	hours, minutes = map(int, time_str.split(':'))
	return time(hour=hours, minute=minutes)


def parse_roster(file_path: Path) -> List[Participant]:
	if not file_path.exists():
		raise FileNotFoundError(f"Roster file not found: {file_path}")
	
	participants = []
	
	with open(file_path, 'r', newline='') as csvfile:
		reader = csv.reader(csvfile)
		
		for row in reader:
			if len(row) != 4:
				continue
			
			name, tz, start_time_str, end_time_str = row
			
			try:
				start_time = parse_time(start_time_str)
				end_time = parse_time(end_time_str)
				
				participants.append(Participant(
					name=name,
					tz=tz,
					start_time=start_time,
					end_time=end_time
				))
			except ValueError as e:
				print(f"Skipping invalid row: {row}. Error: {e}")
	
	if not participants:
		raise ValueError("No valid participants found in roster file")
	
	return participants