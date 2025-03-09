import { Input } from "https://deno.land/x/cliffy@v1.0.0-rc.3/prompt/mod.ts";
import { bold, blue } from "./colors.ts";

const chatLogs: string[] = [];
console.log(bold(blue("Welcome to the Fancy Chat!")));

while (true) {
  const message = await Input.prompt({
    message: "Enter your message",
    validate: (value) => value.trim() !== "" || "Message cannot be empty",
  });

  if (message.toLowerCase() === "exit") {
    console.log(bold("Chat ended."));
    break;
  }

  chatLogs.push(message);
  console.log(`You: ${message}`);
}
