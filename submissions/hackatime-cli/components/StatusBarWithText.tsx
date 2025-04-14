import { Box, Text } from "ink";
import { type EntryColorMapping } from "../constants";
import type { SummariesEntry } from "../lib/wakatime/models";
import StatusBar from "./StatusBar";

export default function StatusBarWithText({ data, text, colorMapping }: { text: string; data: SummariesEntry[]; colorMapping?: EntryColorMapping }) {
  return (
    <Box flexDirection="column" marginTop={1}>
      <Text>{text}</Text>
      <StatusBar data={data} colorMapping={colorMapping} />
    </Box>
  );
}
