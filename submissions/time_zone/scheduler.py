import datetime
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Set
from zoneinfo import ZoneInfo

from meet_zone.parser import Participant

@dataclass
class TimeSlot:
    start_time: datetime
    end_time: datetime
    participant_count: int
    participant_names: Set[str]
    score: float = 0.0
    day_offset: int = 0

    def get_duration_minutes(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() / 60)

    def overlaps_with(self, other: 'TimeSlot') -> bool:
        return self.start_time < other.end_time and self.end_time > other.start_time

def convert_to_utc(local_time: time, tz_name: str, date: datetime.date) -> datetime:
    local_dt = datetime.combine(date, local_time)
    local_dt = local_dt.replace(tzinfo=ZoneInfo(tz_name))
    return local_dt.astimezone(ZoneInfo("UTC"))

def get_availability_grid(participants: List[Participant], date: datetime.date, interval_minutes: int = 15) -> Dict[datetime, Set[str]]:
    grid: Dict[datetime, Set[str]] = {}
    day_start = datetime.combine(date, time(0, 0)).replace(tzinfo=ZoneInfo("UTC"))
    time_slots = [day_start + timedelta(minutes=i * interval_minutes) for i in range(24 * 60 // interval_minutes)]
    for slot in time_slots:
        grid[slot] = set()
    for participant in participants:
        start_utc = convert_to_utc(participant.start_time, participant.tz, date)
        end_utc = convert_to_utc(participant.end_time, participant.tz, date)
        if end_utc < start_utc:
            end_utc += timedelta(days=1)
        current = start_utc.replace(
            minute=(start_utc.minute // interval_minutes) * interval_minutes,
            second=0,
            microsecond=0
        )
        while current < end_utc:
            if current in grid:
                grid[current].add(participant.name)
            current += timedelta(minutes=interval_minutes)
    return {k: v for k, v in grid.items() if v}

def find_continuous_slots(grid: Dict[datetime, Set[str]], min_duration_minutes: int, interval_minutes: int = 15) -> List[TimeSlot]:
    slots: List[TimeSlot] = []
    sorted_times = sorted(grid.keys())
    if not sorted_times:
        return slots
    min_intervals = min_duration_minutes // interval_minutes
    for i in range(len(sorted_times)):
        start_time = sorted_times[i]
        current_participants = grid[start_time].copy()
        if not current_participants:
            continue
        for j in range(i, len(sorted_times)):
            end_time = sorted_times[j]
            current_participants &= grid[end_time]
            if not current_participants:
                break
            if (j - i + 1) >= min_intervals:
                slot_end_time = end_time + timedelta(minutes=interval_minutes)
                slots.append(TimeSlot(
                    start_time=start_time,
                    end_time=slot_end_time,
                    participant_count=len(current_participants),
                    participant_names=current_participants.copy()
                ))
    slots.sort(key=lambda x: (x.end_time - x.start_time).total_seconds(), reverse=True)
    return slots

def find_best_slots(
    participants: List[Participant],
    min_duration: int,
    show_week: bool = False,
    top_k: int = 3,
    start_date: Optional[datetime.date] = None,
    prioritize_participants: bool = True
) -> List[TimeSlot]:
    if not participants:
        return []
    today = start_date or datetime.now().date()
    all_slots = []
    interval_minutes = 15
    if show_week:
        for i in range(7):
            date = today + timedelta(days=i)
            grid = get_availability_grid(participants, date, interval_minutes)
            slots = find_continuous_slots(grid, min_duration, interval_minutes)
            for slot in slots:
                slot.day_offset = i
            all_slots.extend(slots)
    else:
        grid = get_availability_grid(participants, today, interval_minutes)
        all_slots = find_continuous_slots(grid, min_duration, interval_minutes)
        for slot in all_slots:
            slot.day_offset = 0
    max_participants = len(participants)
    for slot in all_slots:
        participant_score = slot.participant_count / max_participants
        duration_hours = (slot.end_time - slot.start_time).total_seconds() / 3600
        duration_score = min(duration_hours / 4.0, 1.0)
        day_score = 1.0 - (getattr(slot, 'day_offset', 0) / 7.0)
        if prioritize_participants:
            slot.score = (participant_score * 0.6) + (duration_score * 0.3) + (day_score * 0.1)
        else:
            slot.score = (duration_score * 0.6) + (participant_score * 0.3) + (day_score * 0.1)
    all_slots.sort(key=lambda x: x.score, reverse=True)
    unique_slots = []
    for slot in all_slots:
        if any(
            slot.start_time <= u.end_time and
            slot.end_time >= u.start_time and
            slot.participant_names.issubset(u.participant_names)
            for u in unique_slots
        ):
            continue
        unique_slots.append(slot)
        if 0 < top_k <= len(unique_slots):
            break
    return unique_slots if top_k <= 0 else unique_slots[:top_k]
