import { Text } from "ink";
import type { ColorMapping } from "../constants";
import { Thresholds } from "../constants";
import type { SummariesEntry } from "../lib/wakatime/models";

export default function SummariesEntryComponent({ project, colorMapping }: { project: SummariesEntry; colorMapping?: ColorMapping }) {
  colorMapping = colorMapping ?? Thresholds.todayProject;

  const color = Thresholds.getColor(project.total_seconds, colorMapping) ?? "greenBright";

  return (
    <Text>
      <Text color={color}>{project.name}</Text>: {project.text}
    </Text>
  );
}
