#!/bin/bash

# Source: https://gist.github.com/xkrishguptaa/3c633f4c75f2b319e18880f3b68b1d23#file-go-application-builder-bash

### Helper functions ###

function header() {
  printf "\033[1;34m$1\033[0m\n"
}

function info() {
  printf "\033[0;32m$1\033[0m\n"
}

function debug() {
  printf "\033[0;33m$1\033[0m\n"
}

function success() {
  printf "\033[0;32m$1\033[0m\n"
}

function error() {
  printf "\033[0;31m$1\033[0m\n"
}

# Header

header "Go Application Builder"
header "======================"

cwd=$(pwd)

info "Build Context: $cwd"

info "Removing old binaries"

rm -rf "${cwd:?}"/bin

success "Removed old binaries"

# Options

CrossBuild=true
AppVersion="0.1.0"
AppName="mnemo"
GoBuildTags=""
OutDir="$cwd/bin"

if [[ -n "$CROSS_BUILD" ]]; then
  CrossBuild=true
fi

if [ -n "$VERSION" ]; then
  AppVersion="$VERSION"
fi

if [[ -n "$APP_NAME" ]]; then
  AppName=$APP_NAME
fi

if [[ -n "$GO_BUILD_TAGS" ]]; then
  GoBuildTags=$GO_BUILD_TAGS
fi

if [[ -n "$OUT_DIR" ]]; then
  OutDir=$OUT_DIR
fi

debug "Cross Build: $CrossBuild"
debug "App Version: $AppVersion"
debug "App Name: $AppName"
debug "Go Build Tags: $GoBuildTags"
debug "Out Dir: $OutDir"

# Build

AppSuffix=""

if [[ "$AppVersion" != "" ]]; then
  AppSuffix="-v$AppVersion"
fi

mkdir -p $OutDir

if [[ "$CrossBuild" = true ]]; then
  platforms=("linux/amd64" "linux/arm64" "darwin/amd64" "darwin/arm64" "windows/amd64" "windows/arm64")

  debug "Platforms:" "${platforms[@]}"

  for platform in "${platforms[@]}"; do
    IFS='/' read -ra p <<<"$platform"

    GOOS=${p[0]}
    GOARCH=${p[1]}

    header "Building for $GOOS/$GOARCH"
    header "--------------------------"

    go build -tags "$GoBuildTags" -o $OutDir/$AppName-$GOOS-$GOARCH$AppSuffix $cwd

    success "Built for $GOOS/$GOARCH"
  done

else
  header "Building for current platform"
  header "-----------------------------"

  go build -tags "$GoBuildTags" -o $OutDir/$AppName$AppSuffix $cwd

  success "Built for current platform"
fi

cd "$cwd" || exit
