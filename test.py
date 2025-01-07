import dropbox
import os
from typing import List
from dropbox import DropboxTeam
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DropboxFileSearcher:
    def __init__(self, access_token: str):
        self.dbx_team = DropboxTeam(access_token)
        self.team_members = self.list_team_members()

    def list_team_members(self) -> List[dict]:
        """
        List all team members in the Dropbox Business account
        """
        try:
            members = []
            result = self.dbx_team.team_members_list()
            for member in result.members:
                members.append({
                    'team_member_id': member.profile.team_member_id,
                    'email': member.profile.email,
                    'name': member.profile.name.display_name
                })
            return members
        except Exception as e:
            print(f"Error listing team members: {e}")
            return []

    def search_member_files(self, member: dict, keywords: List[str], file_types: List[str] = None) -> List[dict]:
        """
        Search files for a specific team member
        """
        try:
            results = []
            dbx = self.dbx_team.as_user(member['team_member_id'])
            print(f"Starting search in {member['name']}'s account...")
            
            # Start with root folder
            folder_path = ''
            files_checked = 0
            
            try:
                # Get all files recursively
                has_more = True
                cursor = None
                
                while has_more:
                    try:
                        if cursor:
                            folder_list = dbx.files_list_folder_continue(cursor)
                        else:
                            folder_list = dbx.files_list_folder(folder_path, recursive=True)
                        
                        # Process each entry
                        for entry in folder_list.entries:
                            files_checked += 1
                            if files_checked % 100 == 0:  # Progress update every 100 files
                                print(f"Checked {files_checked} files in {member['name']}'s account...")
                            
                            if isinstance(entry, dropbox.files.FileMetadata):
                                # Check if file matches any of the extensions
                                if file_types:
                                    matches_extension = any(entry.path_lower.endswith(f".{ext.lower()}") for ext in file_types)
                                    if not matches_extension:
                                        continue
                                
                                # Check if file matches any of the keywords
                                if keywords:
                                    matches_keyword = any(keyword.lower() in entry.path_lower for keyword in keywords)
                                    if not matches_keyword:
                                        continue
                                
                                results.append({
                                    'name': entry.name,
                                    'path': entry.path_display,
                                    'size': entry.size,
                                    'last_modified': entry.client_modified,
                                    'owner': member['name'],
                                    'email': member['email'],
                                    'team_member_id': member['team_member_id']
                                })
                                print(f"Found matching file: {entry.name} in {member['name']}'s account")
                        
                        # Update cursor and check if there's more
                        cursor = folder_list.cursor
                        has_more = folder_list.has_more
                        
                    except dropbox.exceptions.ApiError as e:
                        print(f"API error in {member['name']}'s account: {e}")
                        time.sleep(2)  # Wait before retrying
                        continue
                    
            except Exception as e:
                print(f"Error during file listing for {member['name']}: {e}")
            
            print(f"Completed search in {member['name']}'s account. Checked {files_checked} files, found {len(results)} matches.")
            return results
            
        except Exception as e:
            print(f"Error processing files for {member['name']}: {e}")
            return []

    def search_all_files(self, keywords: List[str], file_types: List[str] = None) -> List[dict]:
        """
        Search files across all team members' accounts in parallel
        """
        all_results = []
        
        # Print team members being searched
        print("Searching through accounts:")
        for member in self.team_members:
            print(f"- {member['name']} ({member['email']})")
        print("\nStarting search...\n")
        
        # Reduce number of workers to avoid rate limiting
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_list = [
                (executor.submit(
                    self.search_member_files,
                    member,
                    keywords,
                    file_types
                ), member)
                for member in self.team_members
            ]
            
            for future, member in future_list:
                try:
                    results = future.result(timeout=600)  # 10 minute timeout per member
                    if results:
                        all_results.extend(results)
                except TimeoutError:
                    print(f"Search timeout for {member['name']}'s account")
                except Exception as e:
                    print(f"Error searching {member['name']}'s account: {str(e)}")
                    continue

        return all_results

    def download_file(self, file_info: dict, local_path: str) -> bool:
        """
        Download a file from a team member's Dropbox
        """
        try:
            dbx = self.dbx_team.as_user(file_info['team_member_id'])
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                metadata, response = dbx.files_download(file_info['path'])
                f.write(response.content)
            return True
        except dropbox.exceptions.DropboxException as e:
            print(f"Error downloading file: {e}")
            return False

def main():
    # Load access token from environment variable
    ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')
    if not ACCESS_TOKEN or ACCESS_TOKEN == 'your_access_token_here':
        print("Error: DROPBOX_ACCESS_TOKEN environment variable not set correctly")
        print("Please set it with your Dropbox access token in the .env file or environment")
        return
    
    # Create searcher
    searcher = DropboxFileSearcher(ACCESS_TOKEN)
    
    if not searcher.team_members:
        print("No team members found. Please check your access token and permissions.")
        return
    
    print(f"Found {len(searcher.team_members)} team members")
    
    # Example usage
    keywords = ["floorplan", "architecture"]
    file_types = ["pdf", "ai", "png", "jpg"]
    
    print(f"\nSearching for files with extensions: {file_types}")
    print(f"And containing keywords: {keywords}")
    print("This may take a while as we search through all team members' accounts...\n")
    
    try:
        # Search for files across all accounts
        results = searcher.search_all_files(keywords, file_types)
        
        if not results:
            print("\nNo files found matching the criteria")
            return

        # Print results
        print(f"\nFound {len(results)} total matching files:")
        for result in results:
            print(f"\nFile: {result['name']}")
            print(f"Owner: {result['owner']} ({result['email']})")
            print(f"Path: {result['path']}")
            print(f"Size: {result['size']} bytes")
            print(f"Last modified: {result['last_modified']}")
            
            # Download example
            download_dir = os.path.join("downloads", result['owner'])
            local_path = os.path.join(download_dir, result['name'])
            
            if searcher.download_file(result, local_path):
                print(f"Successfully downloaded to {local_path}")
            else:
                print(f"Failed to download {result['name']}")
                
    except KeyboardInterrupt:
        print("\nSearch interrupted by user. Processing any results found so far...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main() 