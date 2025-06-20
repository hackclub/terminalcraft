import type { WakatimeConfig } from "./config";
import type { AllTimeViewModel, ProjectsViewModel, ProjectViewModel, RangeInterval, StatsViewModel, SummariesViewModel, UserViewModel } from "./models";

function encodeApiKey(apiKey: string): string {
  return Buffer.from(apiKey).toString("base64");
}

export default class Wakatime {
  private config: WakatimeConfig<true>;

  constructor(config: WakatimeConfig<true>) {
    this.config = config;
  }

  private authHeaders(): Record<string, string> {
    return {
      authorization: `Basic ${encodeApiKey(this.config.apiKey)}`,
    };
  }

  async getHealth(): Promise<string> {
    const response = await fetch(new URL("/health", this.config.apiUrl));
    return response.text();
  }

  async getUser(userId: string = "current"): Promise<UserViewModel> {
    const response = await fetch(new URL(`/api/compat/wakatime/v1/users/${userId}`, this.config.apiUrl), {
      headers: {
        ...this.authHeaders(),
      },
    });

    return response.json();
  }

  async getAllTimeSinceToday(userId: string = "current"): Promise<AllTimeViewModel> {
    const response = await fetch(new URL(`/api/compat/wakatime/v1/users/${userId}/all_time_since_today`, this.config.apiUrl), {
      headers: {
        ...this.authHeaders(),
      },
    });

    return response.json();
  }

  async getProjects(userId: string = "current", q?: string): Promise<ProjectsViewModel> {
    const url = new URL(`/api/compat/wakatime/v1/users/${userId}/projects`, this.config.apiUrl);
    if (q) {
      url.searchParams.append("q", q);
    }

    const response = await fetch(url, {
      headers: {
        ...this.authHeaders(),
      },
    });

    return response.json();
  }

  async getProject(userId: string = "current", projectId: string): Promise<ProjectViewModel> {
    const response = await fetch(new URL(`/api/compat/wakatime/v1/users/${userId}/projects/${projectId}`, this.config.apiUrl), {
      headers: {
        ...this.authHeaders(),
      },
    });

    return response.json();
  }

  async getStatistics(
    userId: string = "current",
    range: RangeInterval,
    project?: string,
    language?: string,
    editor?: string,
    operatingSystem?: string,
    machine?: string,
    label?: string
  ): Promise<StatsViewModel> {
    const url = new URL(`/api/compat/wakatime/v1/users/${userId}/stats/${range}`, this.config.apiUrl);
    if (project) {
      url.searchParams.append("project", project);
    }
    if (language) {
      url.searchParams.append("language", language);
    }
    if (editor) {
      url.searchParams.append("editor", editor);
    }
    if (operatingSystem) {
      url.searchParams.append("operating_system", operatingSystem);
    }
    if (machine) {
      url.searchParams.append("machine", machine);
    }
    if (label) {
      url.searchParams.append("label", label);
    }

    const response = await fetch(url, {
      headers: {
        ...this.authHeaders(),
      },
    });

    return response.json();
  }

  async getSummaries(
    userId: string = "current",
    range?: RangeInterval,
    start?: string,
    end?: string,
    project?: string,
    language?: string,
    editor?: string,
    operatingSystem?: string,
    machine?: string,
    label?: string
  ): Promise<SummariesViewModel> {
    const url = new URL(`/api/compat/wakatime/v1/users/${userId}/summaries`, this.config.apiUrl);
    if (range) {
      url.searchParams.append("range", range);
    }
    if (start) {
      url.searchParams.append("start", start);
    }
    if (end) {
      url.searchParams.append("end", end);
    }
    if (project) {
      url.searchParams.append("project", project);
    }
    if (language) {
      url.searchParams.append("language", language);
    }
    if (editor) {
      url.searchParams.append("editor", editor);
    }
    if (operatingSystem) {
      url.searchParams.append("operating_system", operatingSystem);
    }
    if (machine) {
      url.searchParams.append("machine", machine);
    }
    if (label) {
      url.searchParams.append("label", label);
    }

    const response = await fetch(url, {
      headers: {
        ...this.authHeaders(),
      },
    });

    return response.json();
  }
  
}
