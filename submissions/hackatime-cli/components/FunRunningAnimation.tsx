import { Text, useInput } from "ink";
import { useEffect, useRef, useState } from "react";

export default function FunRunningAnimation({
  maxDots,
  speed,
  color,
}: {
  maxDots?: number;
  speed?: number;
  color?: Parameters<typeof Text>[0]["color"];
}) {
  if (!maxDots || maxDots < 0) {
    maxDots = 10;
  }

  const [dots, setDots] = useState(0);

  const pause = useRef(false);

  useInput((input, key) => {
    if (input !== " " && input !== "k") return;
    pause.current = !pause.current;
  });

  useEffect(() => {
    setDots(0);

    const interval = setInterval(() => {
      if (pause.current) return;

      setDots((dots) => {
        dots = dots + 1;
        if (dots > maxDots) {
          dots = -maxDots;
        }

        return dots;
      });
    }, speed ?? 100);

    return () => clearInterval(interval);
  }, [maxDots, speed]);

  let dotsRender = "";
  let spaceRender = "";

  try {
    dotsRender = "-".repeat(Math.abs(dots));
    spaceRender = dots < 0 ? " ".repeat(dots + maxDots) : "";
  } catch (error) {}

  return (
    <Text color={color}>
      {dotsRender}
      {spaceRender}
      {spaceRender}
      {dotsRender}
    </Text>
  );
}
