import { useEffect, useState } from "react";
import { readFile, mkdirSync, createWriteStream } from "fs";
import { Box, Newline, Text } from "ink";
import { ProgressBar, Alert } from "@inkjs/ui";
import childProcess from "child_process";
import path from "path";
import { default as nodeFetch } from "node-fetch";
import stripAnsi from "strip-ansi";

const totalSteps = 6;

export const DownloadPage = ({ args }: { args: string[] }) => {
  useEffect(() => {
    console.clear();
  }, []);
  if (!args[0]) {
    return <Alert variant="error">Please provide the meta file url</Alert>;
  }
  const [{ step, name }, setStep] = useState({
    step: 1,
    name: "reading config file",
  });
  const [{ componentDir: componentsDir, packageManager }, setConfig] =
    useState<{
      componentDir?: string;
      packageManager?: string;
    }>({});
  const [error, setError] = useState(null);
  const [metaFile, setMetaFile] = useState<{ [key: string]: any }>({});
  const [log, setLog] = useState<string[]>([]);

  if (error) return <Alert variant="error">{error}</Alert>;
  if (step === 1) {
    readFile("./component.config.json", (err, data) => {
      if (err) {
        console.error(err);
        process.exit(1);
      }
      const config = JSON.parse(data.toString());
      if (!config.componentDir) {
        console.error("componentDir is required in config file");
        process.exit(1);
      } else if (!config.packageManager) {
        console.error("packageManager is required in config file");
        process.exit(1);
      }
      setConfig(config);
      setStep({ step: 2, name: "downloading meta.json of component" });
    });
  } else if (step === 2) {
    const metaFileUrl = args[0];
    if (
      !(
        metaFileUrl.startsWith(
          "https://raw.githubusercontent.com/code-ga/helper-cli-tool-repository/refs/heads/"
        ) || metaFileUrl.startsWith("https://github.com/")
      )
    ) {
      return <Alert variant="error">Invalid meta file url</Alert>;
    }
    fetch(metaFileUrl)
      .then((response) => response.json())
      .then((data) => {
        setMetaFile(data);
        setStep({ step: 3, name: "installing dependencies" });
      })
      .catch((error) => {
        setError(error);
      });
  } else if (step === 3) {
    const packagesList = Object.keys(metaFile.dependence)
      .reduce((acc, key) => `${acc} ${key}@${metaFile.dependence[key]}`, "")
      .trim();
    setLog((logs) =>
      logs.concat(
        `Installing dependencies (${packagesList}) using ${packageManager}...`
      )
    );
    if (!packageManager) {
      return (
        <Alert variant="error">packageManager is required in config file</Alert>
      );
    }
    const process = childProcess.spawn(packageManager, [
      "install",
      packagesList,
    ]);
    process.stdout.on("data", (data) => {
      const lines = stripAnsi(data.toString("utf8")).split("\n");

      setLog((log) => [...log, ...lines]);
    });
    setStep({ step: 4, name: "creating component directory" });
  } else if (step === 4) {
    if (!componentsDir) {
      return (
        <Alert variant="error">componentDir is required in config file</Alert>
      );
    }
    const componentDir = path.join(componentsDir, metaFile.name);
    mkdirSync(componentDir, { recursive: true });
    setStep({ step: 5, name: "copying files" });
  } else if (step === 5) {
    if (!componentsDir) {
      return (
        <Alert variant="error">componentDir is required in config file</Alert>
      );
    }
    const componentDir = path.join(componentsDir, metaFile.name);
    for (const filename in metaFile.files) {
      const fileUrl = metaFile.files[filename];
      const filePath = path.join(componentDir, filename);
      const fileStream = createWriteStream(filePath);
      nodeFetch(fileUrl).then((response) => {
        response.body?.pipe(fileStream);
      });
    }
    setStep({ step: 6, name: "done" });
  }
  return (
    <>
      <Box>
        {log.slice(log.length - 5).map((line, key) => (
          <Box key={key}>
            <Text key={key}>{line}</Text>
            <Newline></Newline>
          </Box>
        ))}
      </Box>
      <Text>
        {step}/{totalSteps}: {name}
      </Text>
      <ProgressBar value={(step / totalSteps) * 100}></ProgressBar>
    </>
  );
};
