import loadWakatimeConfig from "./lib/wakatime/config";
const wakatimeConfig = loadWakatimeConfig();

import { render } from "ink";
import App from "./App";

render(<App wakatimeConfig={wakatimeConfig} />);
