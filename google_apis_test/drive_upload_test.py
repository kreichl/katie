import os
import json
import time
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from googleapiclient.errors import HttpError

# Scopes needed for Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

dir = r"C:\Users\reich\Documents\GIT\katie\google_apis_test"

class DriveUploadTester:
    def __init__(self, credentials_file=os.path.join(dir,'credentials.json')):
        self.credentials_file = credentials_file
        self.service = None
        self.setup_drive_service()
    
    def setup_drive_service(self):
        """Set up Google Drive API service"""
        creds = None
        
        # Token file stores the user's access and refresh tokens
        if os.path.exists(os.path.join(dir,'token.json')):
            creds = Credentials.from_authorized_user_file(os.path.join(dir,'token.json'), SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(os.path.join(dir,'token.json'), 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
    
    def create_test_document(self, folder_id=None, file_prefix="Test Document"):
        """Create a Google Doc similar to what Make.com does"""
        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        file_name = f"{file_prefix} {timestamp}"
        
        # HTML content similar to what Make.com might upload
        html_content = """
        <html>
        <body>
        <h1>Test Document</h1>
        <p>This is a test document created via API</p>
        <p>Created at: {}</p>
        </body>
        </html>
        """.format(timestamp)
        
        # File metadata
        file_metadata = {
            'name': file_name,
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        # Add parent folder if specified
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        # Create media upload object
        media = MediaInMemoryUpload(
            html_content.encode('utf-8'),
            mimetype='text/html'
        )
        
        try:
            # This mimics Make.com's upload process
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink',
                supportsAllDrives=True
            ).execute()
            
            return {
                'success': True,
                'file_id': file.get('id'),
                'file_name': file.get('name'),
                'link': file.get('webViewLink'),
                'error': None
            }
            
        except HttpError as error:
            return {
                'success': False,
                'file_id': None,
                'file_name': file_name,
                'link': None,
                'error': f"HTTP {error.resp.status}: {error.error_details}"
            }
        except Exception as error:
            return {
                'success': False,
                'file_id': None,
                'file_name': file_name,
                'link': None,
                'error': str(error)
            }
    
    def run_test_batch(self, num_tests=20, delay_between_tests=1, folder_id=None):
        """Run multiple upload tests to replicate the issue"""
        results = []
        success_count = 0
        error_403_count = 0
        other_error_count = 0
        
        print(f"Starting {num_tests} upload tests...")
        print(f"Target: {'My Drive' if not folder_id else f'Folder ID: {folder_id}'}")
        print("-" * 50)
        
        for i in range(num_tests):
            print(f"Test {i+1}/{num_tests}: ", end="")
            
            result = self.create_test_document(folder_id=folder_id, file_prefix=f"Test-{i+1}")
            results.append(result)
            
            if result['success']:
                success_count += 1
                print("✅ SUCCESS")
            else:
                if "403" in str(result['error']):
                    error_403_count += 1
                    print("❌ 403 ERROR")
                else:
                    other_error_count += 1
                    print(f"❌ ERROR: {result['error']}")
            
            # Wait between tests
            if i < num_tests - 1:  # Don't wait after the last test
                time.sleep(delay_between_tests)
        
        # Summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {num_tests}")
        print(f"Successful: {success_count} ({success_count/num_tests*100:.1f}%)")
        print(f"403 Errors: {error_403_count} ({error_403_count/num_tests*100:.1f}%)")
        print(f"Other Errors: {other_error_count} ({other_error_count/num_tests*100:.1f}%)")
        
        # Show error details
        if error_403_count > 0 or other_error_count > 0:
            print("\nERROR DETAILS:")
            for i, result in enumerate(results):
                if not result['success']:
                    print(f"Test {i+1}: {result['error']}")
        
        return results

    def find_folder_by_name(self, folder_name):
        """Find a folder ID by name"""
        try:
            results = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            if folders:
                return folders[0]['id']
            else:
                print(f"Folder '{folder_name}' not found")
                return None
        except Exception as error:
            print(f"Error finding folder: {error}")
            return None

def main():
    """Main function to run the tests"""
    print("Google Drive Upload Tester")
    print("=" * 50)
    
    # Initialize the tester
    try:
        tester = DriveUploadTester()
    except Exception as e:
        print(f"Failed to initialize Drive service: {e}")
        print("\nMake sure you have:")
        print("1. Downloaded your OAuth credentials as 'credentials.json'")
        print("2. Enabled the Google Drive API in your GCP project")
        return
    
    # Test options
    print("Choose test location:")
    print("1. My Drive (root)")
    print("2. Specific folder (you'll enter folder name)")
    print("3. Specific folder (you'll enter folder ID)")
    
    choice = input("Enter choice (1-3): ").strip()
    folder_id = None
    
    if choice == "2":
        folder_name = input("Enter folder name: ").strip()
        folder_id = tester.find_folder_by_name(folder_name)
        if not folder_id:
            return
    elif choice == "3":
        folder_id = input("Enter folder ID: ").strip()
    
    # Test parameters
    num_tests = int(input("Number of tests to run (default 20): ") or "20")
    delay = float(input("Delay between tests in seconds (default 1): ") or "1")
    
    # Run the tests
    results = tester.run_test_batch(
        num_tests=num_tests, 
        delay_between_tests=delay,
        folder_id=folder_id
    )
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"drive_test_results_{timestamp}.json"
    
    with open(os.path.join(dir,results_file), 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")

if __name__ == "__main__":
    main()