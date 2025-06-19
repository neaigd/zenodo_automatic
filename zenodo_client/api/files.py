import requests
from ..core.client import ZenodoClient
from ..config.settings import ZENODO_API_URL

# Keep the direct upload function for now, as it targets a specific bucket URL
def upload_file_to_bucket(bucket_url, file_path, token):
    """Uploads a file to the given Zenodo bucket URL."""
    print(f"Attempting to upload file {file_path} to {bucket_url}")
    with open(file_path, "rb") as f:
        filename = file_path.split("/")[-1]
        # Note: Bucket upload often uses access_token query param
        response = requests.put(
            f"{bucket_url}/{filename}?access_token={token}",
            data=f
        )
        # Note: Zenodo API returns 200 or 201 on success for uploads
        response.raise_for_status() # Raise an exception for bad status codes (>=400)
        print(f"File {filename} uploaded successfully. Status Code: {response.status_code}")
        # The response might contain details about the uploaded file
        return response.json()


class FilesAPI:
    def __init__(self):
        self.client = ZenodoClient()
        # Base URL for file operations related to a deposition
        # The full URL will be like f"{ZENODO_API_URL}/deposit/depositions/{deposition_id}/files"
        self.base_url_template = f"{ZENODO_API_URL}/deposit/depositions/{{}}/files"

    def list_files_of_deposition(self, deposition_id):
        """Lists files associated with a specific deposition ID."""
        url = self.base_url_template.format(deposition_id)
        print(f"Fetching files for deposition ID {deposition_id} from: {url}")
        # Use the ZenodoClient which handles authentication and retries
        response = self.client.request("GET", url)
        response.raise_for_status() # Raise an exception for bad status codes
        print(f"Files for deposition {deposition_id} fetched successfully.")
        return response.json()