import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "./contexts/AppContext";
import type { WakatimeConfig } from "./lib/wakatime/config";
import PageSelector from "./PageSelector";

type Page = "login" | "dashboard";

const queryClient = new QueryClient();

export default function App({ wakatimeConfig }: { wakatimeConfig?: WakatimeConfig }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AppProvider initWakatimeConfig={wakatimeConfig}>
        <PageSelector />
      </AppProvider>
    </QueryClientProvider>
  );
}
