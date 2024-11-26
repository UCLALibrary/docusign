from argparse import ArgumentParser
from docusign_esign import EnvelopesApi, FoldersApi, FolderItemV2
from docusign_esign.client.api_exception import ApiException
from jwt_utils import dump_form_data, get_base_api_client, get_config


def main() -> None:
    # Proof of concept, with some info hard-coded for now.
    # TODO: Get folder / document info via CLI.
    parser = ArgumentParser()
    parser.add_argument("--config", help="Configuration file to use", required=True)
    args = parser.parse_args()
    config = get_config(args.config)

    scopes = ["signature", "impersonation"]
    api_client = get_base_api_client(scopes, config)
    account_id = api_client.account_id

    try:
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
        doc: FolderItemV2  # for type hints
        for doc in docs:
            print(f"{doc.subject} ({doc.status} {doc.last_modified_date_time})")
            form_data = envelopes_api.get_form_data(account_id, doc.envelope_id)
            dump_form_data(form_data)

    except ApiException as err:
        # TODO: Proper handling, this is just QAD for now.
        print("")
        print(err)
        body = err.body.decode("utf8")
        print(body)


if __name__ == "__main__":
    main()
