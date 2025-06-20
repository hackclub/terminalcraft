import { readFileSync } from "fs";
import { parse } from "ini";

export interface WakatimeConfig<Filled extends boolean = false> {
  apiKey: Filled extends true ? string : string | undefined;
  apiUrl: Filled extends true ? string : string | undefined;
}

export default function loadWakatimeConfig(configPath: string = `${process.env.HOME}/.wakatime.cfg`): WakatimeConfig {
  const config = parse(readFileSync(configPath, "utf-8"));
  return {
    apiKey: config.settings.api_key,
    apiUrl: config.settings.api_url,
  };
}
