from argparse import ArgumentParser
from docusign_esign import EnvelopesApi, EnvelopeDefinition, TemplateRole
from docusign_esign.client.api_exception import ApiException
from jwt_utils import get_base_api_client, get_config, get_consent_url


def create_envelope_definition() -> EnvelopeDefinition:
    # Hard-coded for now, as POC; normally, pass args
    template_id = "7d1ed421-aaae-49a0-b5f0-045d289c5fb1"
    envelope_definition = EnvelopeDefinition(
        status="sent",  # requests that the envelope be created and sent.
        template_id=template_id,
    )

    # Create template roles to connect signers to the template.
    # TODO: Proper input of values, this is just hard-coded for demo.
    employee = TemplateRole(
        email="akohler@library.ucla.edu",
        name="Andy Kohler (Employee)",
        role_name="Employee",
    )
    supervisor = TemplateRole(
        email="akohler@library.ucla.edu",
        name="Andy Kohler (Supervisor)",
        role_name="Supervisor",
    )
    aul = TemplateRole(
        email="akohler@library.ucla.edu",
        name="Andy Kohler (AUL)",
        role_name="AUL",
    )

    # Add the TemplateRole objects to the envelope object
    envelope_definition.template_roles = [employee, supervisor, aul]
    return envelope_definition


def main() -> None:
    # Proof of concept, with some info hard-coded for now.
    parser = ArgumentParser()
    parser.add_argument("--config", help="Configuration file to use", required=True)
    args = parser.parse_args()
    config = get_config(args.config)

    scopes = ["signature", "impersonation"]
    api_client = get_base_api_client(scopes, config)
    account_id = api_client.account_id

    try:
        # Hard-coded for now, for proof of concept.
        envelope_definition = create_envelope_definition()
        envelopes_api = EnvelopesApi(api_client)
        results = envelopes_api.create_envelope(
            account_id=account_id, envelope_definition=envelope_definition
        )
        envelope_id = results.envelope_id
        print(f"{envelope_id=}")

    except ApiException as err:
        # TODO: Proper handling, this is just QAD for now.
        print("")
        print(err)
        body = err.body.decode("utf8")
        print(body)
        print("")
        print("Checking for consent....")
        # Each application needs to get "consent" from the impersonated user.
        # This appears to be needed only one, on the first run.
        # TODO: This, better...
        if "consent_required" in body:
            consent_url = get_consent_url(scopes, config)
            print(
                "Open the following URL in your browser to grant consent to the application:"
            )
            print(consent_url)


if __name__ == "__main__":
    main()
