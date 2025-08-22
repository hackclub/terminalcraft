import { Box, Text } from "ink";
import { useMemo } from "react";
import type { SummariesViewModel } from "../lib/wakatime/models";

export default function SummaryChart({ data }: { data: SummariesViewModel }) {
  const bestDay = useMemo(() => {
    return data.data.reduce((best, current) => {
      return current.grand_total.total_seconds > best.grand_total.total_seconds ? current : best;
    }, data.data[0]);
  }, [data]);

  return (
    <Box flexDirection="row" width="100%" flexWrap="nowrap">
      {data.data.map((day) => {
        return (
          <Box
            key={day.range.date}
            width={`${100 / data.data.length}%`}
            height={`${Math.round((day.grand_total.total_seconds / bestDay.grand_total.total_seconds) * 100)}%`}>
            <Text backgroundColor="blue" wrap="end">
              {" ".repeat(99)}
            </Text>
          </Box>
        );
      })}
    </Box>
  );
}
