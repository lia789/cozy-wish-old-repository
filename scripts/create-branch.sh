#!/bin/bash

# Script to create a new branch following the project's branching strategy

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Display help
function show_help {
    echo -e "${BLUE}CozyWish Branch Creation Script${NC}"
    echo "This script helps create branches following the project's branching strategy."
    echo
    echo "Usage: $0 [options] <branch-name>"
    echo
    echo "Options:"
    echo "  -t, --type TYPE    Branch type (feature, bugfix, release, hotfix)"
    echo "  -i, --issue NUMBER Issue number to include in branch name"
    echo "  -h, --help         Show this help message"
    echo
    echo "Examples:"
    echo "  $0 --type feature --issue 123 add-search-functionality"
    echo "  $0 -t bugfix -i 456 fix-login-error"
    echo "  $0 -t release v1.2.0"
    echo "  $0 -t hotfix critical-security-issue"
    echo
}

# Parse arguments
BRANCH_TYPE=""
ISSUE_NUMBER=""
BRANCH_NAME=""

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -t|--type)
            BRANCH_TYPE="$2"
            shift
            shift
            ;;
        -i|--issue)
            ISSUE_NUMBER="$2"
            shift
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            if [[ -z "$BRANCH_NAME" ]]; then
                BRANCH_NAME="$1"
            else
                BRANCH_NAME="$BRANCH_NAME-$1"
            fi
            shift
            ;;
    esac
done

# Validate branch type
if [[ -z "$BRANCH_TYPE" ]]; then
    echo -e "${RED}Error: Branch type is required.${NC}"
    echo "Use -t or --type to specify one of: feature, bugfix, release, hotfix"
    exit 1
fi

if [[ "$BRANCH_TYPE" != "feature" && "$BRANCH_TYPE" != "bugfix" && "$BRANCH_TYPE" != "release" && "$BRANCH_TYPE" != "hotfix" ]]; then
    echo -e "${RED}Error: Invalid branch type.${NC}"
    echo "Branch type must be one of: feature, bugfix, release, hotfix"
    exit 1
fi

# Validate branch name
if [[ -z "$BRANCH_NAME" ]]; then
    echo -e "${RED}Error: Branch name is required.${NC}"
    exit 1
fi

# Determine base branch
BASE_BRANCH="develop"
if [[ "$BRANCH_TYPE" == "hotfix" ]]; then
    BASE_BRANCH="main"
fi

# Construct full branch name
FULL_BRANCH_NAME="$BRANCH_TYPE/"
if [[ -n "$ISSUE_NUMBER" && "$BRANCH_TYPE" != "release" ]]; then
    FULL_BRANCH_NAME="${FULL_BRANCH_NAME}issue-${ISSUE_NUMBER}-"
fi
FULL_BRANCH_NAME="${FULL_BRANCH_NAME}${BRANCH_NAME}"

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository.${NC}"
    exit 1
fi

# Update base branch
echo -e "${BLUE}Updating $BASE_BRANCH branch...${NC}"
git checkout $BASE_BRANCH
git pull origin $BASE_BRANCH

# Create and checkout new branch
echo -e "${BLUE}Creating branch $FULL_BRANCH_NAME from $BASE_BRANCH...${NC}"
git checkout -b $FULL_BRANCH_NAME

echo -e "${GREEN}Successfully created branch: $FULL_BRANCH_NAME${NC}"
echo -e "${YELLOW}Don't forget to push your branch to GitHub:${NC}"
echo -e "  git push -u origin $FULL_BRANCH_NAME"
