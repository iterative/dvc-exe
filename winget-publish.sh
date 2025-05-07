#!/bin/sh

if [ -z "$1" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

komac sync-fork
komac update Iterative.DVC --version "$1" --submit --urls https://dvc.org/download/win/"$1" --release-notes-url https://github.com/iterative/dvc/releases/tag/"$1" --submit
komac cleanup --only-merged
