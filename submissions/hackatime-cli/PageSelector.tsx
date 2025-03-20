import { useInput } from "ink";
import { useAppContext } from "./contexts/AppContext";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";

export default function PageSelector() {
  const { page, noQuit } = useAppContext();

  useInput(
    (input, key) => {
      if (input === "q") {
        process.exit();
      }
    },
    { isActive: !noQuit }
  );

  return page === "login" ? <Login /> : <Dashboard />;
}
