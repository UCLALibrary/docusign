import tomllib
from docusign_esign import (
    Account,
    ApiClient,
    EnvelopeTemplate,
    OAuthToken,
)
from docusign_esign.client.auth.oauth import OAuthUserInfo


def get_config(config_file_name: str) -> dict:
    with open(config_file_name, "rb") as f:
        config = tomllib.load(f)
    return config


def get_base_api_client(scopes: list[str], config: dict) -> ApiClient:
    """Returns a generic Docusign API client, ready for basic use."""
    api_client = ApiClient()
    api_client.set_base_path(config["authorization_server"])
    api_client.set_oauth_host_name(config["authorization_server"])
    private_key = config["private_key"]
    oauth_token: OAuthToken = api_client.request_jwt_user_token(
        client_id=config["client_id"],
        user_id=config["impersonated_user_id"],
        oauth_host_name=config["authorization_server"],
        private_key_bytes=private_key,
        expires_in=3600,  # seconds
        scopes=scopes,
    )

    access_token = oauth_token.access_token
    # api_client.set_base_token exists, but apparently not used?
    api_client.set_default_header(
        header_name="Authorization", header_value=f"Bearer {access_token}"
    )

    user_info: OAuthUserInfo = api_client.get_user_info(access_token)
    accounts: list[Account] = user_info.get_accounts()

    # ApiClient does not have/use account_id directly;
    # add it for caller's convenience.
    api_client.account_id = accounts[0].account_id

    # This base_path is different from api_client.base_path,
    # which we don't set explicitly.
    base_path = accounts[0].base_uri + "/restapi"

    # host is required for API authorization.
    api_client.host = base_path

    return api_client


def dump_template_info(
    api_client: ApiClient, account_id: str, template: EnvelopeTemplate
) -> None:
    """QAD method to print selected data from a template during development."""
    template_id = template.template_id
    print(f"{template.name} ({template_id})")
    recipients = api_client.list_recipients(account_id, template_id)
    for signer in recipients.signers:
        print(f"\t{signer.role_name}")
        tabs = api_client.list_tabs(account_id, signer.recipient_id, template_id)
        # Tabs objects have lots of attributes, many of which are None
        for tab_field in tabs.attribute_map:
            tab_values = getattr(tabs, tab_field)
            if tab_values:
                print(f"\t\t{tab_field}")
                # tab_values is a list
                # print(f"\t\t\t{tab_values}")
                for tab_data in tab_values:
                    print(f"\t\t\t\t{tab_data.name=}")
                    print(f"\t\t\t\t{tab_data.tab_label=}")
                    print(f"\t\t\t\t{tab_data.tooltip=}")
                    print("")
