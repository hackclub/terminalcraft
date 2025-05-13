import { useEffect, useState } from "react";
import { Spinner, Alert, OrderedList } from "@inkjs/ui";
import { Box, Newline, Text } from "ink";

interface Component {
  name: string;
  description: string;
  version: string;
  meta: string;
  "storybook-url": string;
}

export const ComponentListPage = () => {
  const [loading, setLoading] = useState(true);
  const [components, setComponents] = useState<Record<string, Component>>({});
  const [error, setError] = useState(null);
  useEffect(() => {
    console.clear();
    fetch(
      "https://raw.githubusercontent.com/code-ga/helper-cli-tool-repository/refs/heads/main/meta.json"
    )
      .then((response) => response.json())
      .then((data) => {
        setComponents(data);
        setLoading(false);
      })
      .catch((error) => {
        setError(error);
        setLoading(false);
      });
  }, []);
  return loading ? (
    <Spinner label="Loading"></Spinner>
  ) : error ? (
    <Alert variant="error">{error}</Alert>
  ) : (
    <Box justifyContent="center" flexDirection="column">
      <OrderedList>
        {Object.values(components).map((component, key) => (
          <OrderedList.Item key={key}>
            <Text bold underline>
              {component.name}
            </Text>
            <Text>description: {component.description}</Text>
            <Text>version: {component.version}</Text>
            <Text>storybook url: {component["storybook-url"]}</Text>
            <Text>
              download command:{" "}
              <Text
                bold
              >{`helper.exe components download ${component.meta}`}</Text>
            </Text>
            <Newline></Newline>
          </OrderedList.Item>
        ))}
      </OrderedList>
      <Newline></Newline>
      <Text bold>
        feel free to share your component at{" "}
        <Text underline backgroundColor={"blue"}>
          https://github.com/code-ga/helper-cli-tool-repository
        </Text>
      </Text>
    </Box>
  );
};
