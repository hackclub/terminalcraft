import { Alert, Spinner } from "@inkjs/ui";
import gitRemoteOriginUrl from "git-remote-origin-url";
import { Box, Text } from "ink";
import BigText from "ink-big-text";
import { useEffect, useState } from "react";
import Markdown from "@inkkit/ink-markdown";
console.clear();
export const GithubIssue = ({ args }: { args: string[] }) => {
  if (!args[0])
    return <Alert variant="error">The Github issues id is needed</Alert>;
  const [issueComments, setIssueComments] = useState<{ [key: string]: any }[]>(
    []
  );
  const [issuesInfo, setIssuesInfo] = useState<{ [key: string]: any }>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const { owner, repo } = await ParseRepoUrl();
      if (!owner || !repo) {
        setError("Invalid repository url");
        setLoading(false);
        return;
      }
      const res = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/issues/${
          args[0]
        }/comments`
      );
      const issuesInfoRes = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/issues/${args[0]}`
      );

      if (res.ok) {
        const data = await res.json();
        setIssueComments(data);
      } else {
        setError(res.statusText);
      }
      if (issuesInfoRes.ok) {
        const data = await issuesInfoRes.json();
        setIssuesInfo(data);
      } else {
        setError(issuesInfoRes.statusText);
      }

      setLoading(false);
    })();
  }, []);

  return loading ? (
    <Spinner label="Loading"></Spinner>
  ) : error ? (
    <Alert variant="error">{error}</Alert>
  ) : (
    <>
      <BigText text={issuesInfo.title + "#" + issuesInfo.number} font="tiny" />
      <Box
        key={issuesInfo.node_id}
        borderStyle={"doubleSingle"}
        flexDirection="column"
      >
        <Box margin={1}>
          <Text>{issuesInfo.user.login}</Text>
          <Text> - </Text>
          <Text>
            {issuesInfo.created_at == issuesInfo.updated_at
              ? issuesInfo.created_at
              : issuesInfo.updated_at + " (updated)"}
          </Text>
        </Box>
        <Box margin={0.5}>
          <Text>Content: </Text>
        </Box>
        <Box margin={1} borderStyle={"bold"}>
          <Markdown>{issuesInfo.body}</Markdown>
        </Box>
      </Box>
      {issueComments.map((comment) => (
        <Box
          key={comment.node_id}
          borderStyle={"doubleSingle"}
          flexDirection="column"
        >
          <Box margin={1}>
            <Text>{comment.user.login}</Text>
            <Text> - </Text>
            <Text>
              {comment.created_at == comment.updated_at
                ? comment.created_at
                : comment.updated_at + " (updated)"}
            </Text>
          </Box>
          <Box margin={0.5}>
            <Text>Content: </Text>
          </Box>
          <Box margin={1} borderStyle={"bold"}>
            <Markdown>{comment.body}</Markdown>
          </Box>
        </Box>
      ))}
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
