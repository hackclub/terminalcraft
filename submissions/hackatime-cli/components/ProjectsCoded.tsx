import { useQuery } from "@tanstack/react-query";
import { Box, Newline, Text } from "ink";
import { Thresholds } from "../constants";
import { useAppContext } from "../contexts/AppContext";
import Loading from "./Loading";
import SummariesEntryComponent from "./Project";

export default function ProjectsCoded() {
  const { wakatimeConfig, wakatime } = useAppContext();

  if (!wakatimeConfig?.apiKey || !wakatimeConfig?.apiUrl || !wakatime) {
    return <Text>No API key or URL set. Please login first.</Text>;
  }

  const todayStats = useQuery({
    queryKey: ["stats", "today", wakatimeConfig.apiUrl, wakatimeConfig.apiKey],
    queryFn: async () => (await wakatime.getStatistics("current", "today")).data,
  });

  const weekStats = useQuery({
    queryKey: ["stats", "week", wakatimeConfig.apiUrl, wakatimeConfig.apiKey],
    queryFn: async () => (await wakatime.getStatistics("current", "week")).data,
  });

  const monthStats = useQuery({
    queryKey: ["stats", "month", wakatimeConfig.apiUrl, wakatimeConfig.apiKey],
    queryFn: async () => (await wakatime.getStatistics("current", "month")).data,
  });

  if (todayStats.isError) return <Text>Error: {String(todayStats.error)}</Text>;
  if (weekStats.isError) return <Text>Error: {String(weekStats.error)}</Text>;
  if (monthStats.isError) return <Text>Error: {String(monthStats.error)}</Text>;

  return (
    <Box flexDirection="column">
      <Box marginTop={1} flexDirection="column">
        <Text>
          Projects coded <Text color="greenBright">last 24 hours</Text>:
          <Newline />
        </Text>

        {!todayStats.data ? (
          <Loading />
        ) : (
          todayStats.data.projects.map((project) => (
            <SummariesEntryComponent key={project.name} project={project} colorMapping={Thresholds.todayProject} />
          ))
        )}
      </Box>

      <Box marginTop={1} flexDirection="column">
        <Text>
          Projects coded <Text color="greenBright">this week</Text>:
          <Newline />
        </Text>

        {!weekStats.data ? (
          <Loading />
        ) : (
          weekStats.data.projects.map((project) => (
            <SummariesEntryComponent key={project.name} project={project} colorMapping={Thresholds.weekProject} />
          ))
        )}
      </Box>

      <Box marginTop={1} flexDirection="column">
        <Text>
          Projects coded <Text color="greenBright">this month</Text>:
          <Newline />
        </Text>

        {!monthStats.data ? (
          <Loading />
        ) : (
          monthStats.data.projects.map((project) => (
            <SummariesEntryComponent key={project.name} project={project} colorMapping={Thresholds.monthProject} />
          ))
        )}
      </Box>
    </Box>
  );
}
