import { Text } from "ink";
import { useEffect, useState } from "react";

export default function Loading() {
  const [dots, setDots] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prev) => (prev + 1) % 4);
    }, 200);

    return () => clearInterval(interval);
  }, []);

  return <Text>Loading{".".repeat(dots)}</Text>;
}
