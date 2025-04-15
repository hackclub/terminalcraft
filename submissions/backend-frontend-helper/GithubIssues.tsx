import { useEffect, useState } from "react";
import gitRemoteOriginUrl from "git-remote-origin-url";
import Table from "./components/Table";
import { Spinner, Alert } from "@inkjs/ui";
import terminalSize from "terminal-size";
import { useInput,Text } from "ink";
console.clear();
export const GithubIssues = ({ args }: { args: string[] }) => {
  const [issues, setIssues] = useState<{ [key: string]: any }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const itemsPerPage = (terminalSize().rows - 8) / 2;

  useEffect(() => {
    (async () => {
      const { owner, repo } = await ParseRepoUrl();
      if (!owner || !repo) {
        setError("Invalid repository url");
        setLoading(false);
        return;
      }
      const res = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/issues?per_page=${
          args[0] || 50
        }`
      );

      if (res.ok) {
        const data = await res.json();
        setIssues(data);
      } else {
        setError(res.statusText);
      }

      setLoading(false);
    })();
  }, []);

  const data = issues.map((issue) => ({
    number: issue.number,
    title: issue.title,
    state: issue.state,
    openAt: issue.created_at,
    createdBy: issue.user.login,
  }));

  useInput((input, key) => {
    if (key.upArrow) {
      setOffset((offset) => Math.max(offset - 1, 0));
    } else if (key.downArrow) {
      setOffset((offset) => Math.min(offset + 1, data.length - itemsPerPage));
    } else if (input === "q") {
      process.exit(0);
    }
  });

  return loading ? (
    <Spinner label="Loading"></Spinner>
  ) : error ? (
    <Alert variant="error">{error}</Alert>
  ) : (
    <>
      <Table data={data.slice(offset, offset + itemsPerPage)}></Table>
      <Text>
        current offset: {offset}, total items: {data.length},q for quit
      </Text>
    </>
  );
};

async function ParseRepoUrl() {
  const repoUrl = await gitRemoteOriginUrl();
  let owner: string = "";
  let repo: string = "";
  if (repoUrl.startsWith("https://github.com/")) {
    owner = repoUrl.split("https://github.com/")[1].split("/")[0];
    repo = repoUrl.split("https://github.com/")[1].split("/")[1];
  } else if (repoUrl.startsWith("git@github.com:")) {
    owner = repoUrl.split("git@github.com:")[1].split("/")[0];
    repo = repoUrl.split("git@github.com:")[1].split("/")[1].split(".git")[0];
  }

  return { owner, repo };
}
