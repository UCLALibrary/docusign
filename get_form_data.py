from argparse import ArgumentParser
from pprint import pprint  # for pretty output during development
from docusign_esign import (
    EnvelopesApi,
    EnvelopeFormData,
    FoldersApi,
    FolderItemV2,
    FormDataItem,
)
from docusign_esign.client.api_exception import ApiException
from jwt_utils import get_base_api_client, get_config, get_consent_url


def get_form_data_from_envelope(envelope_form_data: EnvelopeFormData) -> dict:
    """Returns form data from the given envelope."""
    # Ignore recipient_form_data (a list, each element including its own form_data)
    # for now.
    parsed_data = {}
    form_data_item: FormDataItem  # for type hints
    for form_data_item in envelope_form_data.form_data:
        parsed_data[form_data_item.name] = form_data_item.value
    return parsed_data


def main() -> None:
    # Proof of concept, with some info hard-coded for now.
    # TODO: Get folder / document info via CLI.
    parser = ArgumentParser()
    parser.add_argument("--config", help="Configuration file to use", required=True)
    args = parser.parse_args()
    config = get_config(args.config)

    try:
        scopes = ["signature", "impersonation"]
        api_client = get_base_api_client(scopes, config)
        account_id = api_client.account_id

        folders_api = FoldersApi(api_client)
        # folders = folders_api.list(account_id)
        # Could also limit this by date and sender, but not subject.
        # search() requires a search_folder_id value (which is really a status);
        # could also use list_items(account_id, folder_id) which requires all items
        # of interest to be in one specific folder.
        completed_docs = folders_api.search(account_id, search_folder_id="completed")
        docs = [
            doc for doc in completed_docs.folder_items if "Form 100-1A" in doc.subject
        ]

        envelopes_api = EnvelopesApi(api_client)
        # Collect information we want.
        parsed_form_data = []
        doc: FolderItemV2  # for type hints
        for doc in docs:
            print(f"{doc.subject} ({doc.status} {doc.last_modified_date_time})")
            form_data: EnvelopeFormData = envelopes_api.get_form_data(
                account_id, doc.envelope_id
            )
            parsed_form_data.append(get_form_data_from_envelope(form_data))
        # For now, just dump data for review.
        pprint(parsed_form_data, width=132)

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
