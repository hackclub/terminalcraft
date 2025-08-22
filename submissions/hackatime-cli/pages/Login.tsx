import { Newline, Text, useInput } from "ink";
import { useState } from "react";
import { bigBanner, hackatimeApiUrl, smallBanner, smallerBanner, smallestBanner } from "../constants";
import { useAppContext } from "../contexts/AppContext";
import Wakatime from "../lib/wakatime";

function getInput({
  initValue,
  setFinalValue,
  setNoQuit,
}: {
  initValue?: string;
  setFinalValue: (value: string) => void;
  setNoQuit?: (noQuit: boolean) => void;
}) {
  const [waiting, setWaiting] = useState(false);
  const [value, setValue] = useState(initValue ?? "");

  const handler: Parameters<typeof useInput>[0] = (input, key) => {
    if (key.return) {
      setWaiting(false);
      setFinalValue(value);
      setNoQuit?.(false);
      return;
    }

    if (key.escape) {
      setWaiting(false);
      setNoQuit?.(false);
      return;
    }

    if (key.backspace || key.delete) {
      setValue((prev) => prev.slice(0, -1));
      return;
    }

    setValue((prev) => prev + input);
  };

  return { waiting, setWaiting, value, handler };
}

export default function Login() {
  // reached Login, no apiKey

  const { setPage, wakatimeConfig, setWakatimeConfig, setWakatime, setNoQuit, screenWidth } = useAppContext();

  const apiUrlInput = getInput({
    initValue: wakatimeConfig?.apiUrl,
    setNoQuit,
    setFinalValue(value) {
      setWakatimeConfig({ apiUrl: value, apiKey: wakatimeConfig?.apiKey });
    },
  });

  const apiKeyInput = getInput({
    initValue: wakatimeConfig?.apiKey,
    setNoQuit,
    setFinalValue(value) {
      setWakatimeConfig({ apiKey: value, apiUrl: wakatimeConfig?.apiUrl });
    },
  });

  useInput(
    (input, key) => {
      if (input === "1") {
        setNoQuit(true);
        apiUrlInput.setWaiting(true);
      }
      if (input === "2") {
        setNoQuit(true);
        apiKeyInput.setWaiting(true);
      }
      if (wakatimeConfig?.apiUrl && wakatimeConfig.apiKey && key.return) {
        setWakatime(new Wakatime({ apiUrl: wakatimeConfig.apiUrl, apiKey: wakatimeConfig.apiKey }));
        setPage("dashboard");
      }
    },
    { isActive: !(apiUrlInput.waiting || apiKeyInput.waiting) }
  );

  useInput(apiUrlInput.handler, { isActive: apiUrlInput.waiting });
  useInput(apiKeyInput.handler, { isActive: apiKeyInput.waiting });

  if (apiUrlInput.waiting) return <Text>Enter your Wakatime API url: {apiUrlInput.value}</Text>;
  if (apiKeyInput.waiting) return <Text>Enter your Wakatime API key: {"●".repeat(apiKeyInput.value.length)}</Text>;

  return (
    <>
      {screenWidth > 136 ? (
        <Text>{bigBanner}</Text>
      ) : screenWidth > 76 ? (
        <Text>{smallBanner}</Text>
      ) : screenWidth > 60 ? (
        <Text>{smallerBanner}</Text>
      ) : screenWidth > 56 ? (
        <Text>{smallestBanner}</Text>
      ) : (
        <Text>Hackatime-CLI</Text>
      )}

      <Newline />

      <Text>
        Press <Text color="magentaBright">q</Text> anywhere to quit
        <Newline />
      </Text>

      <Text>Login into {wakatimeConfig?.apiUrl ?? hackatimeApiUrl}</Text>
      <Text>
        Press <Text color="magentaBright">1</Text>. Change API Url
      </Text>
      <Text>
        Press <Text color="magentaBright">2</Text>.{" "}
        {wakatimeConfig?.apiKey ? (
          <>
            API Key: <Text color="gray">{"●".repeat(wakatimeConfig.apiKey.length)}</Text>
          </>
        ) : (
          "Enter API Key"
        )}
      </Text>
      {wakatimeConfig?.apiUrl && wakatimeConfig.apiKey && (
        <Text>
          Press <Text color="magentaBright">Enter</Text> to login
        </Text>
      )}
    </>
  );
}
