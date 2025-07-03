"""
Export functionality for Meet-Zone
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dataclasses import asdict

from meet_zone.parser import Participant
from meet_zone.scheduler import TimeSlot


class ExportManager:
    """Handles exporting data in various formats"""
    
    @staticmethod
    def export_participants_csv(participants: List[Participant], file_path: Path) -> bool:
        """Export participants to CSV file"""
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['name', 'timezone', 'start_time', 'end_time'])
                
                for participant in participants:
                    writer.writerow([
                        participant.name,
                        participant.tz,
                        participant.start_time.strftime('%H:%M'),
                        participant.end_time.strftime('%H:%M')
                    ])
            return True
        except Exception as e:
            print(f"Error exporting participants: {e}")
            return False
    
    @staticmethod
    def export_results_csv(slots: List[TimeSlot], file_path: Path) -> bool:
        """Export meeting results to CSV file"""
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'start_time_utc', 'end_time_utc', 'duration_minutes',
                    'participant_count', 'score', 'participants'
                ])
                
                for slot in slots:
                    writer.writerow([
                        slot.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        slot.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        slot.get_duration_minutes(),
                        slot.participant_count,
                        f"{slot.score:.3f}",
                        ', '.join(sorted(slot.participant_names))
                    ])
            return True
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False
    
    @staticmethod
    def export_results_json(slots: List[TimeSlot], participants: List[Participant], 
                           file_path: Path, metadata: Optional[dict] = None) -> bool:
        """Export complete results to JSON file"""
        try:
            data = {
                'metadata': {
                    'export_time': datetime.now().isoformat(),
                    'total_participants': len(participants),
                    'total_slots': len(slots),
                    **(metadata or {})
                },
                'participants': [
                    {
                        'name': p.name,
                        'timezone': p.tz,
                        'start_time': p.start_time.strftime('%H:%M'),
                        'end_time': p.end_time.strftime('%H:%M')
                    }
                    for p in participants
                ],
                'meeting_slots': [
                    {
                        'start_time_utc': slot.start_time.isoformat(),
                        'end_time_utc': slot.end_time.isoformat(),
                        'duration_minutes': slot.get_duration_minutes(),
                        'participant_count': slot.participant_count,
                        'score': slot.score,
                        'participants': list(slot.participant_names),
                        'day_offset': getattr(slot, 'day_offset', 0)
                    }
                    for slot in slots
                ]
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting JSON: {e}")
            return False
    
    @staticmethod
    def export_calendar_ics(slots: List[TimeSlot], file_path: Path, 
                           meeting_title: str = "Team Meeting") -> bool:
        """Export meeting slots to ICS calendar format"""
        try:
            ics_content = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//Meet-Zone//Meeting Scheduler//EN",
                "CALSCALE:GREGORIAN",
                "METHOD:PUBLISH"
            ]
            
            for i, slot in enumerate(slots):
                # Create unique UID
                uid = f"meetzone-{slot.start_time.strftime('%Y%m%d%H%M%S')}-{i}"
                
                # Format times for ICS
                start_time = slot.start_time.strftime('%Y%m%dT%H%M%SZ')
                end_time = slot.end_time.strftime('%Y%m%dT%H%M%SZ')
                
                # Create description
                description = f"Participants: {', '.join(sorted(slot.participant_names))}\\n"
                description += f"Duration: {slot.get_duration_minutes()} minutes\\n"
                description += f"Score: {slot.score:.1%}"
                
                ics_content.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTART:{start_time}",
                    f"DTEND:{end_time}",
                    f"SUMMARY:{meeting_title} (Option {i+1})",
                    f"DESCRIPTION:{description}",
                    f"STATUS:TENTATIVE",
                    "END:VEVENT"
                ])
            
            ics_content.append("END:VCALENDAR")
            
            with open(file_path, 'w') as f:
                f.write('\n'.join(ics_content))
            return True
        except Exception as e:
            print(f"Error exporting calendar: {e}")
            return False