# Mock Interview Preparer

## Description

mock_interview_preparor is a CLI tool designed to help users prepare for interviews in any field. It leverages Cohere's AI API to generate interview questions, provide feedback on your answers, and score your responses on a scale of 0 to 10.

## Features

Conduct mock interviews on any topic.

Receive AI-generated feedback and scoring for your answers.

Track your performance across multiple questions.

## Prerequisites

Node.js installed on your system.

## Installation

`npm i mock_interview_preparor`


## Usage

Run the CLI tool:
 `interview` or `npx interview`

Follow the prompts:

Enter the number of questions you want.

Specify the topic for the interview.

Answer the questions and receive feedback and a score.

Example Output:

```bash
How many questions would you like? 3
What topic would you like to be interviewed on? JavaScript

Question: What is the difference between var, let, and const in JavaScript?
Your Answer: var is function-scoped, let and const are block-scoped.

Feedback: Good answer! You could expand on const being immutable.

Question: Explain the event loop in JavaScript.
Your Answer: The event loop handles asynchronous tasks and callbacks.

Feedback: Clear answer! Consider explaining the call stack and microtasks in more detail.

Thank you for practicing! Your readiness score is: 85%
```

Version

1.0.2


