import { Box, Text } from "ink";
import { EntryColors, type EntryColorMapping } from "../constants";
import type { SummariesEntry } from "../lib/wakatime/models";
import { darkOrLight, stringToColorHex } from "../utils";

export default function StatusBar({ data, colorMapping }: { data: SummariesEntry[]; colorMapping?: EntryColorMapping }) {
  return (
    <Box display="flex" flexDirection="row" width="100%">
      {data.map((entry: SummariesEntry) => {
        const color =
          (colorMapping ? EntryColors.getColor(entry.name.toLowerCase(), colorMapping) : stringToColorHex(entry.name)) ??
          stringToColorHex(entry.name);

        return (
          <Box key={entry.name} width={`${entry.percent}%`} margin={0}>
            <Text backgroundColor={color} color={darkOrLight(color) == "dark" ? "whiteBright" : "black"} wrap="truncate">
              {entry.name}
              {" ".repeat(Math.max(Math.ceil(entry.percent) + 1 - entry.name.length, 0))}
            </Text>
          </Box>
        );
      })}
    </Box>
  );
}
