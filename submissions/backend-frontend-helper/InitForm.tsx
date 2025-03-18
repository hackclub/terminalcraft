import React, { useState } from "react";
import { Text } from "ink";
import { writeFileSync } from "fs";
import { TextInput, Select } from "@inkjs/ui";

function InitForm() {
  const [componentDir, setComponentDir] = useState("");
  const [packageManager, setPackageManager] = useState("");
  const [step, setStep] = useState(0);

  if (step === 0) {
    return (
      <>
        <Text>Please enter the component directory:</Text>
        <TextInput
          placeholder="Enter component directory..."
          onSubmit={(value) => {
            setComponentDir(value.trim());
            setStep(1);
          }}
        />
      </>
    );
  } else if (step === 1) {
    return (
      <>
        <Text>
          Please choose the package manager{" "}
          <Text bold>
            (choose the package manager installed in your pc, i cannot guess
            what error will have
          </Text>
          {"=>>"}):
        </Text>
        <Select
          options={[
            { label: "Bun", value: "bun" },
            { label: "NPM", value: "npm" },
          ]}
          onChange={(value) => {
            setPackageManager(value);
            console.log("Component directory:", componentDir);
            console.log("Package manager:", packageManager);
            setStep(2);
          }}
        />
      </>
    );
  } else {
    const config = JSON.stringify({ componentDir, packageManager }, null, 2);
    const filename = "component.config.json";
    writeFileSync(filename, config);
    return <Text>Configuration saved to {filename}</Text>;
  }
}

export default InitForm;
