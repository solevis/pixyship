#!/usr/bin/env bash

BUILD_ARG="build"

while getopts 'sh' opt; do
  case "$opt" in
    s)
      BUILD_ARG="build-staging"
      ;;

    ?|h)
      echo "Usage: $(basename $0) [-s]"
      exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"

npx browserslist@latest --update-db
npm run "${BUILD_ARG}"
