from argparse import ArgumentParser
from jira.exceptions import JIRAError
from jwt_utils import get_config, get_jira_api_client


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--config", help="Configuration file to use", required=True)
    args = parser.parse_args()
    config = get_config(args.config)

    try:
        jira = get_jira_api_client(config)

        # This assumes auth server is in the Sandbox & hardcoded for now
        # TODO: Add all custom fields
        issue_fields = {
            "project": {"key": "LBS"},
            "summary": "Test issue using Jira API",
            "description": "This is a test issue created using Jira API.",
            "issuetype": {"name": "Travel & Entertainment"},
            "customfield_10468": "Wanda Barahona",
        }
        new_issue = jira.create_issue(fields=issue_fields)
        print(f"Created new issue: {new_issue}")

    except JIRAError as err:
        print(err)


if __name__ == "__main__":
    main()
