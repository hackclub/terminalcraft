import { useState } from "react";
import Table from "./components/Table";
import { Text, useInput } from "ink";
import terminalSize from "terminal-size";

console.clear();

export function Test() {
  const [offset, setOffset] = useState(0);
  const itemsPerPage = (terminalSize().rows - 8) / 2;

  const data = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    name: `Name ${i}`,
    email: `Email ${i}`,
  }));

  useInput((input, key) => {
    if (key.upArrow) {
      setOffset((offset) => Math.max(offset - 1, 0));
    }else if (key.downArrow) {
      setOffset((offset) => Math.min(offset + 1, data.length - itemsPerPage));
    }else if (input === "q") {
      process.exit(0);
    }
  })
  return (
    <>
      <Table data={data.slice(offset, offset + itemsPerPage)}></Table>
      <Text>
        current offset: {offset}, total items: {data.length},q for quit
      </Text>

      <Text>p/s:you find the place code-ga dev component</Text>
    </>
  );
}
