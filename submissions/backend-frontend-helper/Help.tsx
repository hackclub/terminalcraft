import { UnorderedList } from "@inkjs/ui";
import { Box, Text } from "ink";
import BigText from "ink-big-text";
export const HelpPage = () => {
  return (
    <>
      <Box
        borderStyle="classic"
        marginRight={2}
        alignItems="center"
        justifyContent="center"
      >
        <BigText text="helper"></BigText>
      </Box>
      <Text color={"cyan"}>Commands: </Text>
      <Box marginLeft={2}>
        <UnorderedList>
          <Text color={"green"}>Categories:</Text>

          <UnorderedList.Item>
            <Text color={"yellow"}>🔮 Components (components)</Text>

            <UnorderedList>
              <UnorderedList.Item>
                <Text color={"red"}>⭐ List (list)</Text>
                <Text>
                  List all available components in from the repository
                </Text>
                <Text color={"blackBright"} backgroundColor={"blue"}>
                  Usage: helper.exe components list
                </Text>
              </UnorderedList.Item>

              <UnorderedList.Item>
                <Text color={"red"}>⭐ Download (download)</Text>
                <Text>Download a component from the repository</Text>
                <Text color={"blackBright"} backgroundColor={"blue"}>
                  Usage: helper.exe components download [component meta url]
                </Text>
              </UnorderedList.Item>
              <UnorderedList.Item>
                <Text color={"red"}>⭐ Init (init)</Text>
                <Text>Init the config file for downloading components</Text>
                <Text color={"blackBright"} backgroundColor={"blue"}>
                  Usage: helper.exe components init
                </Text>
              </UnorderedList.Item>
            </UnorderedList>
          </UnorderedList.Item>
          <UnorderedList.Item>
            <Text color={"yellow"}>🔮 Github (github)</Text>
            <Text>Some util for github repository</Text>
            <UnorderedList>
              <UnorderedList.Item>
                <Text color={"red"}>⭐ issues (issues)</Text>
                <Text>
                  list 10 newest issues of this repository (repository url get
                  from local git config)
                </Text>
                <Text color={"blackBright"} backgroundColor={"blue"}>
                  Using: helper.exe github issues [number of issues]
                </Text>
              </UnorderedList.Item>
              <UnorderedList.Item>
                <Text color={"red"}>⭐ issue (issue)</Text>
                <Text>
                  open an issue of this repository (repository url get from
                  local git config)
                </Text>
                <Text color={"blackBright"} backgroundColor={"blue"}>
                  using: helper.exe github issue [number of issue]
                </Text>
              </UnorderedList.Item>
            </UnorderedList>
          </UnorderedList.Item>
        </UnorderedList>
      </Box>
    </>
  );
};
