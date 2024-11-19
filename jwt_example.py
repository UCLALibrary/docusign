from docusign_esign import ApiClient, TemplatesApi, EnvelopeTemplate
from docusign_esign.client.api_exception import ApiException
from jwt_secrets import DOCUSIGN_CONFIG as ds_config

# from pprint import pprint

# Reimplementation of code from:
# * jwt_console.py
# * app/jwt_config.py
# * app/jwt_helpers/jwt_helper.py


def get_private_key(private_key_path: str) -> str:
    """Returns contents of the private key file
    at private_key_path.
    """
    with open(private_key_path) as f:
        private_key = f.read()
    # Original code, re-encode as utf-8...
    # return private_key.encode("ascii").decode("utf-8")
    # But... the file is already base64, which is ASCII...
    return private_key


# Original code, adapted to remove inputs
def get_args(account_id, access_token, base_path):
    signer_email = "akohler@library.ucla.edu"
    signer_name = "Andy Kohler WORK"
    cc_email = "akohler726@gmail.com"
    cc_name = "Andy Kohler HOME"

    envelope_args = {
        "signer_email": signer_email,
        "signer_name": signer_name,
        "cc_email": cc_email,
        "cc_name": cc_name,
        "status": "sent",
    }
    args = {
        "account_id": account_id,
        "base_path": base_path,
        "access_token": access_token,
        "envelope_args": envelope_args,
    }

    return args


def dump_template_info(
    api_client: ApiClient, account_id: str, template: EnvelopeTemplate
) -> None:
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


def main() -> None:
    scopes = ["signature", "impersonation"]
    private_key = get_private_key(ds_config["private_key_file"])
    api_client = ApiClient()
    api_client.set_base_path(ds_config["authorization_server"])
    api_client.set_oauth_host_name(ds_config["authorization_server"])
    oauth_token = api_client.request_jwt_user_token(
        client_id=ds_config["client_id"],
        user_id=ds_config["impersonated_user_id"],
        oauth_host_name=ds_config["authorization_server"],
        private_key_bytes=private_key,
        expires_in=3600,  # seconds
        scopes=scopes,
    )

    # oauth_token looks like a dictionary but is docusign_esign.client.auth.oauth.OAuthToken
    # print(type(oauth_token))
    # print(oauth_token)

    access_token = oauth_token.access_token
    # set_access_token requires a token object... not the actual value...
    # Also, this fails with
    # {"errorCode":"AUTHORIZATION_INVALID_TOKEN",
    # "message":"The access token provided is expired, revoked or malformed."}
    # api_client.set_access_token(oauth_token)
    api_client.set_default_header(
        header_name="Authorization", header_value=f"Bearer {access_token}"
    )

    user_info = api_client.get_user_info(access_token)
    # user_info looks like dict but is docusign_esign.client.auth.oauth.OAuthUserInfo
    # print("")
    # print(type(user_info))
    # print(user_info)

    accounts = user_info.get_accounts()
    # accounts is list of <docusign_esign.client.auth.oauth.Account
    # print("")
    # print(type(accounts))
    # print(accounts)

    account_id = accounts[0].account_id
    # print("")
    # print(f"{account_id=}")

    base_path = accounts[0].base_uri + "/restapi"
    # print("")
    # print(f"{base_path=}")

    # Several layers down, demo code sets host from base_path (via creation of a new client...)
    api_client.host = base_path

    try:
        # This works, with tweak to consts.py for document path.
        # args = get_args(account_id, access_token, base_path)
        # doc_docx = "World_Wide_Corp_Battle_Plan_Trafalgar.docx"
        # doc_pdf = "World_Wide_Corp_lorem.pdf"
        # envelope_id = Eg002SigningViaEmailController.worker(args, doc_docx, doc_pdf)
        # print("Your envelope has been sent.")
        # print(envelope_id)

        # This works, now that host is being set correctly
        # pprint(vars(api_client))

        templates_api = TemplatesApi(api_client)
        # Doesn't actually list anything, just gets the data
        template_list = templates_api.list_templates(account_id)
        # print(template_list)
        print("Templates:")
        template: EnvelopeTemplate  # type hint for dev
        for template in template_list.envelope_templates:
            # There's currently only one template available.
            dump_template_info(templates_api, account_id, template)

        # template_id = template.template_id
    except ApiException as err:
        print("")
        print(err)
        body = err.body.decode("utf8")
        print(body)


if __name__ == "__main__":
    main()
