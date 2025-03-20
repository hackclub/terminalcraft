#!/usr/bin/env fish

set cmd $argv[1]
switch $cmd
    case ls list ''
        echo "listing all patterns..."
        for line in "$(curl https://conwaylife.com/patterns/ | grep .cells)"
            echo $line | string split '"' -f 2
        end
        exit 0

    case --help -h help
        echo "Usage: pattern.fish [opts] <PATTERN>"
        echo ""
        echo "opts:"
        echo "         -d, --download: download <PATTERN> to /tmp/<PATTERN>"
        echo "         -h, --help    : show this msg"
        echo ""
        echo "pattern:"
        echo "         ls, list, [default]: list all the patterns known by conwaylife.com"
        echo "         <pattern>          : display it inside cgol-tui"
        exit 0
end

set pattern "$(string replace '.cells' '' $cmd)"
echo "pattern: '$pattern'"
set url "https://conwaylife.com/patterns/$pattern.cells"
echo "url: '$url'"

set p "/tmp/$pattern.cells"
if test -e $p
    echo "already saved to '$p'"
else
    echo "saving to '$p'"
    curl $url -o $p
end
if test "$argv[2]" = --download; or test "$argv[2]" = -d
else
    cargo r -r -- $p
end
