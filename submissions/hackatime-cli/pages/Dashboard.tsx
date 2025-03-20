import { useQuery } from "@tanstack/react-query";
import { Box, Text } from "ink";
import FunRunningAnimation from "../components/FunRunningAnimation";
import Loading from "../components/Loading";
import ProjectsCoded from "../components/ProjectsCoded";
import StatusBarWithText from "../components/StatusBarWithText";
import { EntryColors, Thresholds } from "../constants";
import { useAppContext } from "../contexts/AppContext";
import { timeAgo } from "../utils";

export default function Dashboard() {
  const { wakatimeConfig, wakatime, screenWidth } = useAppContext();

  if (!wakatimeConfig?.apiKey || !wakatimeConfig?.apiUrl || !wakatime) {
    return <Text>No API key or URL set. Please login first.</Text>;
  }

  const isMobile = screenWidth < 80;

  const user = useQuery({
    queryKey: ["userInfo", wakatimeConfig.apiUrl, wakatimeConfig.apiKey],
    queryFn: async () => (await wakatime.getUser()).data,
  });

  const allTimeSinceToday = useQuery({
    queryKey: ["allTime", wakatimeConfig.apiUrl, wakatimeConfig.apiKey],
    queryFn: async () => (await wakatime.getAllTimeSinceToday()).data,
  });

  const projects = useQuery({
    queryKey: ["projects", wakatimeConfig.apiUrl, wakatimeConfig.apiKey],
    queryFn: async () => (await wakatime.getProjects()).data,
  });

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

  const statusBar = useQuery({
    queryKey: ["summaries", "today", wakatimeConfig.apiUrl, wakatimeConfig.apiKey],
    queryFn: async () => (await wakatime.getSummaries("current", "today")).data,
  });

  const last30DaysSummaries = useQuery({
    queryKey: ["summaries", "last_30_days", wakatimeConfig.apiUrl, wakatimeConfig.apiKey],
    queryFn: () => wakatime.getSummaries("current", "last_30_days"),
  });

  if (user.isError) return <Text>Error: {String(user.error)}</Text>;
  if (allTimeSinceToday.isError) return <Text>Error: {String(allTimeSinceToday.error)}</Text>;
  if (projects.isError) return <Text>Error: {String(projects.error)}</Text>;
  if (todayStats.isError) return <Text>Error: {String(todayStats.error)}</Text>;
  if (weekStats.isError) return <Text>Error: {String(weekStats.error)}</Text>;
  if (monthStats.isError) return <Text>Error: {String(monthStats.error)}</Text>;
  if (statusBar.isError) return <Text>Error: {String(statusBar.error)}</Text>;
  if (last30DaysSummaries.isError) return <Text>Error: {String(last30DaysSummaries.error)}</Text>;

  if (!user.isFetched || !user.data) {
    return <Loading />;
  }

  const lastHeartbeat = new Date(user.data.last_heartbeat_at);
  const timeDelta = Date.now() - lastHeartbeat.getTime();

  return (
    <>
      <Box
        width="100%"
        display="flex"
        justifyContent="center"
        alignItems="center"
        flexDirection="column"
        height={isMobile ? 1 : 2}
        marginBottom={isMobile ? 1 : 0}>
        <Box display="flex" flexDirection="row" alignItems="center" flexWrap="wrap" marginBottom={1}>
          <Text color="cyan">{wakatimeConfig.apiUrl}</Text>
          <Text> </Text>
          <Text>Dashboard</Text>
        </Box>
        {!isMobile && <FunRunningAnimation maxDots={Math.round(screenWidth / 10)} speed={100} color="green" />}
      </Box>
      <Box display="flex" width="100%" flexDirection={isMobile ? "column" : "row"} justifyContent="space-between">
        <Box display="flex" flexDirection="column" width={isMobile ? "100%" : "55%"}>
          <Text>
            Welcome back, <Text color="blueBright">{user.data.email}</Text>
          </Text>

          {todayStats.data && (
            <Box flexDirection={isMobile ? "column" : "row"} flexWrap="wrap">
              <Text>You have coded for </Text>
              <Text>
                <Text color={Thresholds.getColor(todayStats.data.total_seconds, Thresholds.today) ?? "redBright"}>
                  {todayStats.data.human_readable_total}
                </Text>{" "}
                today{weekStats.data && ", "}
              </Text>
              {weekStats.data && (
                <Text>
                  <Text color={Thresholds.getColor(weekStats.data.total_seconds, Thresholds.week) ?? "redBright"}>
                    {weekStats.data.human_readable_total}
                  </Text>{" "}
                  this week{monthStats.data && ", "}
                </Text>
              )}
              {monthStats.data && (
                <Text>
                  <Text color={Thresholds.getColor(monthStats.data.total_seconds, Thresholds.month) ?? "redBright"}>
                    {monthStats.data.human_readable_total}
                  </Text>{" "}
                  this month
                </Text>
              )}
            </Box>
          )}
        </Box>
        <Box
          display="flex"
          marginTop={isMobile ? 1 : 0}
          flexDirection="column"
          width={isMobile ? "100%" : "40%"}
          alignItems={isMobile ? "flex-start" : "flex-end"}>
          <Box
            flexDirection="row"
            flexWrap="wrap"
            alignItems={isMobile ? "flex-start" : "flex-end"}
            width="100%"
            justifyContent={isMobile ? "flex-start" : "flex-end"}>
            <Text>
              Last heartbeat: <Text color={Thresholds.getColor(timeDelta, Thresholds.lastHeartbeat)}>{timeAgo(lastHeartbeat)}</Text>{" "}
            </Text>
            <Text>
              <Text color="gray">({lastHeartbeat.toLocaleString()})</Text>
            </Text>
          </Box>
          {allTimeSinceToday.data && (
            <Box
              flexDirection="row"
              flexWrap="wrap"
              alignItems={isMobile ? "flex-start" : "flex-end"}
              width="100%"
              justifyContent={isMobile ? "flex-start" : "flex-end"}>
              <Text>
                All time coded: <Text color="green">{allTimeSinceToday.data.text}</Text>{" "}
              </Text>
              <Text>
                <Text color="gray">({allTimeSinceToday.data.total_seconds.toLocaleString()} seconds)</Text>
              </Text>
            </Box>
          )}
          <Text>
            <Text color="gray">User ID: {user.data.id}</Text>
          </Text>
        </Box>
      </Box>

      <Box flexDirection={isMobile ? "column" : "row"} justifyContent="space-between" width="100%">
        <Box width={isMobile ? "100%" : "35%"}>
          <ProjectsCoded />
        </Box>

        <Box width={isMobile ? "96%" : "60%"} flexDirection="column">
          {statusBar.data && (
            <Box margin={1} width="100%" flexDirection="column">
              {statusBar.data[0].categories && (
                <StatusBarWithText text="Categories:" data={statusBar.data[0].categories} colorMapping={EntryColors.category} />
              )}
              {statusBar.data[0].branches && <StatusBarWithText text="Branches:" data={statusBar.data[0].branches} />}
              {statusBar.data[0].editors && <StatusBarWithText text="Editors:" data={statusBar.data[0].editors} colorMapping={EntryColors.editor} />}
              {statusBar.data[0].languages && (
                <StatusBarWithText text="Languages:" data={statusBar.data[0].languages} colorMapping={EntryColors.language} />
              )}
              {statusBar.data[0].operating_systems && (
                <StatusBarWithText text="Operating Systems:" data={statusBar.data[0].operating_systems} colorMapping={EntryColors.os} />
              )}
              {statusBar.data[0].machines && <StatusBarWithText text="Machines:" data={statusBar.data[0].machines} />}
              {statusBar.data[0].projects && <StatusBarWithText text="Projects:" data={statusBar.data[0].projects} />}
            </Box>
          )}
          {/* {last30DaysSummaries.data && <SummaryChart data={last30DaysSummaries.data} />} */}
        </Box>
      </Box>
    </>
  );
}
