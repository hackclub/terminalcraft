import React, { createContext, useContext, useEffect, useState } from "react";
import type Wakatime from "../lib/wakatime";
import type { WakatimeConfig } from "../lib/wakatime/config";

type Page = "login" | "dashboard";

interface AppContextInterface {
  page: "login" | "dashboard";

  setPage: (page: Page) => void;

  wakatimeConfig?: WakatimeConfig;

  setWakatimeConfig: (wakatimeConfig: WakatimeConfig) => void;

  wakatime?: Wakatime;

  setWakatime: (wakatime: Wakatime) => void;

  noQuit: boolean;
  setNoQuit: (noQuit: boolean) => void;

  screenWidth: number;

  setScreenWidth: (screenWidth: number) => void;
}

const AppContext = createContext<AppContextInterface | undefined>(undefined);

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useAppContext must be used within a AppProvider");
  }
  return context;
};

export default AppContext;

export function AppProvider({ children, initWakatimeConfig }: React.PropsWithChildren<{ initWakatimeConfig?: WakatimeConfig }>) {
  const [page, setPage] = useState<Page>("login");
  const [wakatimeConfig, setWakatimeConfig] = useState(initWakatimeConfig);
  const [wakatime, setWakatime] = useState<Wakatime>();

  const [noQuit, setNoQuit] = useState(false);

  const [screenWidth, setScreenWidth] = useState(process.stdout.columns);

  useEffect(() => {
    process.stdout.on("resize", () => {
      setScreenWidth(process.stdout.columns);
    });
  }, []);

  return (
    <AppContext.Provider
      value={{ page, setPage, wakatimeConfig, setWakatimeConfig, wakatime, setWakatime, noQuit, setNoQuit, screenWidth, setScreenWidth }}>
      {children}
    </AppContext.Provider>
  );
}
