export type RangeInterval =
  | "today"
  | "yesterday"
  | "week"
  | "month"
  | "year"
  | "7_days"
  | "30_days"
  | "6_months"
  | "12_months"
  | "last_7_days"
  | "last_30_days"
  | "last_6_months"
  | "last_12_months"
  | "last_year"
  | "any"
  | "all_time";

/**
  Example:
  {
    "id": "U07D59XCG4U",
    "display_name": "U07D59XCG4U",
    "full_name": "",
    "email": "toby@vsus.app",
    "is_email_public": false,
    "is_email_confirmed": false,
    "timezone": "America/Vancouver",
    "last_heartbeat_at": "2025-03-18T23:19:01.042Z",
    "last_project": "hackatime-cli",
    "last_plugin_name": "Vscode",
    "username": "U07D59XCG4U",
    "website": "",
    "created_at": "2024-11-02T17:22:27.027Z",
    "modified_at": "2024-11-02T17:22:27.027Z",
    "photo": "https://cachet.dunkirk.sh/users/U07D59XCG4U/r"
  }
 */

export interface User {
  created_at: string;
  display_name: string;
  email: string;
  full_name: string;
  id: string;
  is_email_confirmed: boolean;
  is_email_public: boolean;
  last_heartbeat_at: string;
  last_plugin_name: string;
  last_project: string;
  modified_at: string;
  photo: string;
  timezone: string;
  username: string;
  website: string;
}

export interface UserViewModel {
  data: User;
}

/**
  Example:
  {
    "end": "2025-03-18T23:56:46Z",
    "end_date": "2025-03-18",
    "start": "2024-11-08T21:14:55Z",
    "start_date": "2024-11-08",
    "timezone": "UTC"
  }
 */

export interface AllTimeRange {
  end: string;
  end_date: string;
  start: string;
  start_date: string;
  timezone: string;
}

/**
  Example: 
  {
    "total_seconds": 378483,
    "text": "105 hrs 8 mins",
    "is_up_to_date": true,
    "range": <AllTimeRange>
  }
 */

export interface AllTimeData {
  total_seconds: number;
  text: string;
  is_up_to_date: boolean;
  range: AllTimeRange;
}

export interface AllTimeViewModel {
  data: AllTimeData;
}

/**
  Example:
  {
    "id": "hackatime-cli",
    "name": "hackatime-cli",
    "last_heartbeat_at": "2025-03-18T23:59:35.215Z",
    "human_readable_last_heartbeat_at": "Tue, 18 Mar 2025 23:59",
    "urlencoded_name": "hackatime-cli",
    "created_at": "2025-03-18T19:59:52.145Z"
  }
 */

export interface Project {
  created_at: string;
  human_readable_last_heartbeat_at: string;
  id: string;
  last_heartbeat_at: string;
  name: string;
  urlencoded_name: string;
}

export interface ProjectViewModel {
  data: Project;
}

export interface ProjectsViewModel {
  data: Project[];
}

/**
  Example:
  {
    "digital": "3:39:10",
    "hours": 3,
    "minutes": 39,
    "name": "Vscode",
    "percent": 100,
    "seconds": 10,
    "text": "3 hrs 39 mins",
    "total_seconds": 13150
  }
 */

export interface SummariesEntry {
  digital: string;
  hours: number;
  minutes: number;
  name: string;
  percent: number;
  seconds: number;
  text: string;
  total_seconds: number;
}

/**
  Example:
  {
    "username": "U07D59XCG4U",
    "user_id": "U07D59XCG4U",
    "start": "2025-03-18T19:59:52.145Z",
    "end": "2025-03-19T02:09:44.768Z",
    "status": "ok",
    "total_seconds": 13150,
    "daily_average": 0,
    "days_including_holidays": 0,
    "range": "today",
    "human_readable_range": "Today",
    "human_readable_total": "3 hrs 39 mins",
    "human_readable_daily_average": "",
    "is_coding_activity_visible": true,
    "is_other_usage_visible": true,
    "editors": <SummariesEntry[]>,
    "languages": <SummariesEntry[]>,
    "machines": <SummariesEntry[]>,
    "projects": <SummariesEntry[]>,
    "operating_systems": <SummariesEntry[]>,
    "categories": <SummariesEntry[]>
  }
 */

export interface StatsData {
  branches: SummariesEntry[];
  categories: SummariesEntry[];
  daily_average: number;
  days_including_holidays: number;
  editors: SummariesEntry[];
  end: string;
  human_readable_daily_average: string;
  human_readable_range: string;
  human_readable_total: string;
  is_coding_activity_visible: boolean;
  is_other_usage_visible: boolean;
  languages: SummariesEntry[];
  machines: SummariesEntry[];
  operating_systems: SummariesEntry[];
  projects: SummariesEntry[];
  range: string;
  start: string;
  status: string;
  total_seconds: number;
  user_id: string;
  username: string;
}

export interface StatsViewModel {
  data: StatsData;
}

/**
  Example:
  {
    "decimal": "4.16",
    "digital": "4:9",
    "seconds": 14978,
    "text": "4 hrs 10 mins"
  }
 */

export interface SummariesCumulativeTotal {
  decimal: string;
  digital: string;
  seconds: number;
  text: string;
}

/**
  Example:
  {
    "days_including_holidays": 1,
    "days_minus_holidays": 1,
    "holidays": 0,
    "seconds": 14976,
    "seconds_including_other_language": 14978,
    "text": "4 hrs 10 mins",
    "text_including_other_language": "4 hrs 10 mins"
  }
 */

export interface SummariesDailyAverage {
  days_including_holidays: number;
  days_minus_holidays: number;
  holidays: number;
  seconds: number;
  seconds_including_other_language: number;
  text: string;
  text_including_other_language: string;
}

/**
  Example:
  {
    "digital": "4:9",
    "hours": 4,
    "minutes": 9,
    "text": "4 hrs 10 mins",
    "total_seconds": 14978
  }
 */

export interface SummariesGrandTotal {
  digital: string;
  hours: number;
  minutes: number;
  text: string;
  total_seconds: number;
}

/**
  Example:
  {
    "date": "2025-03-19T03:09:40Z",
    "end": "2025-03-18T23:59:58.999999999-07:00",
    "start": "2025-03-18T00:00:00-07:00",
    "text": "",
    "timezone": "UTC"
  }
 */

export interface SummariesRange {
  date: string;
  end: string;
  start: string;
  text: string;
  timezone: string;
}

/**
  Example:
  {
    "categories": <SummariesEntry[]>,
    "dependencies": <SummariesEntry[]>,
    "editors": <SummariesEntry[]>,
    "languages": <SummariesEntry[]>,
    "machines": <SummariesEntry[]>,
    "operating_systems": <SummariesEntry[]>,
    "projects": <SummariesEntry[]>,
    "grand_total": <SummariesGrandTotal>,
    "range": <SummariesRange>
  }
 */

export interface SummariesData {
  branches: SummariesEntry[];
  categories: SummariesEntry[];
  dependencies: SummariesEntry[];
  editors: SummariesEntry[];
  entities: SummariesEntry[];
  grand_total: SummariesGrandTotal;
  languages: SummariesEntry[];
  machines: SummariesEntry[];
  operating_systems: SummariesEntry[];
  projects: SummariesEntry[];
  range: SummariesRange;
}

/**
  Example:
  {
    "cumulative_total": <SummariesCumulativeTotal>,
    "daily_average": <SummariesDailyAverage>,
    "data": <SummariesData[]>,
    "end": "2025-03-18T23:59:58.999999999-07:00",
    "start": "2025-03-18T00:00:00-07:00"
  }
 */

export interface SummariesViewModel {
  cumulative_total: SummariesCumulativeTotal;
  daily_average: SummariesDailyAverage;
  data: SummariesData[];
  end: string;
  start: string;
}

/**
  Example:
  {
    "cached_at": "2025-03-19T03:20:22.062526831Z",
    "data": <SummariesData>
  }
 */

export interface StatusBarViewModel {
  cached_at: string;
  data: SummariesData;
}
