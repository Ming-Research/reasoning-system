#!/bin/sh
# Print the base a CI job passes to check.py's --base: the revision preceding
# the change it checks. A push to main compares with the tip before the push,
# a manual run on main with the first parent, and any other ref with its fork
# point from origin/main. It assumes the main line is the branch main on the
# remote origin. Stdout contains only the resolved commit.
set -eu

if [ "$#" -ne 3 ]; then
  echo 'usage: review-base.sh EVENT REF PUSH_BEFORE' >&2
  exit 1
fi
event=$1
ref=$2
before=$3
case "$event" in
  push|workflow_dispatch|pull_request) ;;
  *) echo "unsupported event for the reasoning check: $event" >&2; exit 1 ;;
esac

if [ "$ref" = refs/heads/main ]; then
  if [ "$event" = push ]; then
    candidate=$before
  else
    # A manual main run checks the last revision against its first parent.
    candidate=HEAD^
  fi
else
  # New main-side commits are not changes made by this branch; for a pull
  # request HEAD is its merge commit, whose base is main's tip.
  candidate=$(git merge-base origin/main HEAD)
fi

if ! base=$(git rev-parse --verify --end-of-options "${candidate}^{commit}"); then
  echo "cannot resolve the reasoning check's base: $candidate" >&2
  exit 1
fi
if [ "$ref" = refs/heads/main ] && [ "$base" = "$(git rev-parse HEAD)" ]; then
  echo 'the base on main equals HEAD; refusing an empty comparison' >&2
  exit 1
fi
printf '%s\n' "$base"
