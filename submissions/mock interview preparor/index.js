#!/usr/bin/env node

const readline = require("readline");
const { CohereClientV2 } = require("cohere-ai");

// Initialize Cohere with your API key
const cohere = new CohereClientV2({ token: "7ciaxvObjwRoJu8wW2jzg9S0f9pCpuXksaZrMCrj" });

// Set up readline interface for CLI interaction
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

let savedMessages = [];
let feedbackScores = [];

// Function to interact with Cohere's Chat API
async function chatWithCohere(messages) {
  try {
    const response = await cohere.chat({
      model: "command-r-plus-08-2024",
      messages,
    });
    savedMessages.push({
      role: "user",
      content: messages.length > 0 ? messages[messages.length - 1].content : "",
    });
    savedMessages.push({
      role: "assistant",
      content: response.message.content[0].text,
    });
    return response.message.content[0].text;
  } catch (error) {
    console.error("Error communicating with Cohere:", error);
    return "Sorry, I encountered an error.";
  }
}

// Function to evaluate the user's answer
async function evaluateAnswer(answer, question, systemMessage) {
  const feedbackPrompt = {
    role: "user",
    content: `Please provide feedback on this answer: ${answer}`,
  };
  const scorePrompt = {
    role: "user",
    content: `On a scale from 0 to 10, how well does this answer respond to the question: ${question}? Answer with only the number. NO PERCENTAGES`,
  };

  const feedback = await chatWithCohere([
    systemMessage,
    { role: "assistant", content: question },
    { role: "user", content: answer },
    feedbackPrompt,
  ]);
  const scoreResponse = await chatWithCohere([
    systemMessage,
    { role: "assistant", content: question },
    { role: "user", content: answer },
    scorePrompt,
  ]);

  const score = parseInt(scoreResponse, 10);
  if (!isNaN(score) && score >= 0 && score <= 10) {
    feedbackScores.push(score);
    console.log(`\nFeedback: ${feedback}`);
    // console.log(`Score: ${score * 10}%\n`);
  }
}

// Function to start the mock interview
function startInterview() {
  rl.question("How many questions would you like? ", (numQuestions) => {
    const totalQuestions = parseInt(numQuestions, 10);
    if (isNaN(totalQuestions) || totalQuestions <= 0) {
      console.log("Please enter a valid number of questions.");
      return startInterview();
    }

    rl.question(
      "What topic would you like to be interviewed on? ",
      async (topic) => {
        const systemMessage = {
          role: "system",
          content: `You are a helpful assistant conducting a mock interview on ${topic}. Only ask interview questions, no extra comments and NO FOLLOW UP QUESTIONS! ONLY STATEMENTS. Provide feedback on answers and score them from 0 to 10. NO PERCENTAGES! NO OTHER QUESTIONS! JUST PROVIDE FEEDBACK!`,
        };

        let questionsAsked = 0;

        async function askQuestion() {
          if (questionsAsked >= totalQuestions) {
            const averageScore =
              feedbackScores.length > 0
                ? Math.round(
                    (feedbackScores.reduce((a, b) => a + b, 0) /
                      feedbackScores.length) *
                      10,
                  )
                : 0;

            console.log(
              `\nThank you for practicing! Your readiness score is: ${averageScore}%`,
            );
            rl.close();
            return;
          }

          const userMessage = {
            role: "user",
            content: `Please ask me a ${topic} interview question.`,
          };
          const question = await chatWithCohere([
            systemMessage,
            ...savedMessages,
            userMessage,
          ]);
          console.log(`\nQuestion: ${question}`);

          rl.question("Your Answer: ", async (answer) => {
            await evaluateAnswer(answer, question, systemMessage);
            questionsAsked++;
            askQuestion();
          });
        }

        askQuestion();
      },
    );
  });
}

// Start the interview process
startInterview();
