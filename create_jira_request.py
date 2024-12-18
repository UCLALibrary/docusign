from argparse import ArgumentParser
from jwt_utils import get_config, get_jira_api_client


# This code is proof of concept only, not nearly ready for production use.
def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--config", help="Configuration file to use", required=True)
    args = parser.parse_args()
    config = get_config(args.config)

    jira_client = get_jira_api_client(config)

    # Obtained via jira_client.service_desks()
    # 22 LBS Library Business Services
    service_desk_id = 22

    jira_client.request_types(service_desk_id)
    # [<JIRA RequestType: name='Travel & Entertainment Request', id='164'>,
    # <JIRA RequestType: name='Emailed request', id='163'>]
    # No way to get request type by id?
    request_type = jira_client.request_type_by_name(
        service_desk_id, "Travel & Entertainment Request"
    )
    request_type_id = request_type.id

    # Bare bones minimal data package.
    # description field is not accepted if present, even though it's in the request type?
    # Haven't found API way to get accurate list of fields for a service desk request type.
    issue_data = {
        "serviceDeskId": service_desk_id,
        "requestTypeId": request_type_id,
        "requestFieldValues": {
            "summary": "Test request summary via API",
        },
    }

    # This raises the request... but raises an exception since this user can't view it,
    # via the API???
    jira_client.create_customer_request(fields=issue_data)

    # jira.exceptions.JIRAError: JiraError HTTP 404 url:
    # https://uclalibrary-sandbox-741.atlassian.net/rest/api/2/issue/LBS-34
    # text: Issue does not exist or you do not have permission to see it.

    # Request is available here (for LBS-34 created above)
    # https://uclalibrary-sandbox-741.atlassian.net/jira/servicedesk/projects/LBS/queues/custom/183/LBS-34


if __name__ == "__main__":
    main()
