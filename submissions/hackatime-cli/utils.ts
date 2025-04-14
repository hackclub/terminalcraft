export function timeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);

  const formatter = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

  if (diffSec < 60) return formatter.format(-diffSec, "seconds");
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return formatter.format(-diffMin, "minutes");
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return formatter.format(-diffHours, "hours");
  const diffDays = Math.floor(diffHours / 24);
  return formatter.format(-diffDays, "days");
}

export function stringToColorHex(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 31 + str.charCodeAt(i)) >>> 0; // Simple hash function
  }
  const r = (hash >> 16) & 0xff;
  const g = (hash >> 8) & 0xff;
  const b = hash & 0xff;
  return `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
}

export function hexToRgb(hex: string) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex.replaceAll("#", ""));
  if (!result) return null;
  return {
    r: parseInt(result[1], 16) / 255,
    g: parseInt(result[2], 16) / 255,
    b: parseInt(result[3], 16) / 255,
  };
}

export function darkOrLight(hex: string): "light" | "dark" {
  const rgb = hexToRgb(hex);
  if (!rgb) return "dark";

  return rgb.r * 0.299 + rgb.g * 0.587 + rgb.b * 0.114 > 0.5 ? "light" : "dark"; // copilot
}
