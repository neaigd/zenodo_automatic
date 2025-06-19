from ..core.client import ZenodoClient
from ..config.settings import ZENODO_API_URL

class DepositionAPI:
    def __init__(self):
        self.client = ZenodoClient()
        # Using the sandbox URL for development
        self.base_url = f"{ZENODO_API_URL}/deposit/depositions"

    def list_depositions(self, params=None):
        """Lists depositions for the authenticated user."""
        # Zenodo API might use pagination. This is a basic implementation.
        print(f"Fetching depositions from: {self.base_url}")
        response = self.client.request("GET", self.base_url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        print("Depositions fetched successfully.")
        return response.json()

    def get_deposition(self, deposition_id):
        """Retrieves details for a specific deposition."""
        url = f"{self.base_url}/{deposition_id}"
        print(f"Fetching deposition with ID {deposition_id} from: {url}")
        response = self.client.request("GET", url)
        response.raise_for_status() # Raise an exception for bad status codes
        print(f"Deposition {deposition_id} fetched successfully.")
        return response.json()

    def create_draft(self):
        """Creates a new empty deposition draft."""
        print(f"Creating a new deposition draft at: {self.base_url}")
        # A POST request with an empty JSON body creates a new draft
        response = self.client.request("POST", self.base_url, json={})
        response.raise_for_status() # Raise an exception for bad status codes
        print("New deposition draft created successfully.")
        return response.json()

    def update_metadata(self, deposition_id, metadata):
        """Updates the metadata for a specific deposition."""
        url = f"{self.base_url}/{deposition_id}"
        data = {"metadata": metadata}
        print(f"Updating metadata for deposition ID {deposition_id} at: {url}")
        response = self.client.request("PUT", url, json=data)
        response.raise_for_status() # Raise an exception for bad status codes
        print(f"Metadata for deposition {deposition_id} updated successfully.")
        return response.json()