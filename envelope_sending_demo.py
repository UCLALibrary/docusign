from docusign_esign import EnvelopesApi, EnvelopeDefinition, TemplateRole
from docusign_esign.client.api_exception import ApiException
from jwt_secrets import DOCUSIGN_CONFIG as ds_config
from jwt_utils import get_base_api_client


def create_envelope_definition() -> EnvelopeDefinition:
    # Hard-coded for now, as POC; normally, pass args
    template_id = "7d1ed421-aaae-49a0-b5f0-045d289c5fb1"
    envelope_definition = EnvelopeDefinition(
        status="sent",  # requests that the envelope be created and sent.
        template_id=template_id,
    )

    # Create template roles to connect signers to the template.
    employee = TemplateRole(
        email="zoetucker@library.ucla.edu",
        name="Zoe Tucker",
        role_name="Employee",
    )
    supervisor = TemplateRole(
        email="akohler@library.ucla.edu",
        name="Andy Kohler",
        role_name="Supervisor",
    )
    aul = TemplateRole(
        email="joshuagomez@library.ucla.edu",
        name="Joshua Gomez",
        role_name="AUL",
    )

    # Add the TemplateRole objects to the envelope object
    envelope_definition.template_roles = [employee, supervisor, aul]
    return envelope_definition


def main() -> None:
    scopes = ["signature", "impersonation"]
    api_client = get_base_api_client(scopes, ds_config)
    account_id = api_client.account_id

    try:
        # Hard-coded for now, for POC
        envelope_definition = create_envelope_definition()
        envelopes_api = EnvelopesApi(api_client)
        results = envelopes_api.create_envelope(
            account_id=account_id, envelope_definition=envelope_definition
        )
        envelope_id = results.envelope_id
        print(f"{envelope_id=}")

        # Test to Zoe, Andy, Josh 20241119
        # envelope_id = "6dc9501f-bf85-494f-ba1e-e5c5b8ad5115"

    except ApiException as err:
        print("")
        print(err)
        body = err.body.decode("utf8")
        print(body)


if __name__ == "__main__":
    main()
