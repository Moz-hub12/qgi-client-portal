import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from supabase import create_client, Client
from werkzeug.datastructures import FileStorage

class SupabaseService:
    """Service class for Supabase storage operations"""
    
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.client: Optional[Client] = None
        
        if self.url and self.key and self.url != 'your_supabase_url':
            try:
                self.client = create_client(self.url, self.key)
                print("Supabase client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            print("Supabase credentials not configured - running in demo mode")
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return self.client is not None
    
    def upload_file(self, file: FileStorage, bucket: str, folder: str = "", user_id: int = None) -> Dict[str, Any]:
        """
        Upload a file to Supabase storage
        
        Args:
            file: FileStorage object from Flask request
            bucket: Supabase storage bucket name
            folder: Optional folder path within bucket
            user_id: Optional user ID for organizing files
            
        Returns:
            Dict containing file path, public URL, and metadata
        """
        if not file or not file.filename:
            raise Exception("No file provided")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Build file path
        path_parts = []
        if folder:
            path_parts.append(folder)
        if user_id:
            path_parts.append(f"user_{user_id}")
        path_parts.append(unique_filename)
        
        file_path = "/".join(path_parts)
        
        if not self.is_configured():
            # Demo mode - simulate successful upload
            print(f"Demo mode: Simulating upload of {file.filename} to {file_path}")
            file.seek(0)
            file_content = file.read()
            
            return {
                'file_path': file_path,
                'public_url': f"https://demo.supabase.co/storage/v1/object/public/{bucket}/{file_path}",
                'bucket': bucket,
                'original_filename': file.filename,
                'content_type': file.content_type,
                'file_size': len(file_content),
                'uploaded_at': datetime.utcnow().isoformat()
            }
        
        try:
            # Upload file to Supabase storage
            file.seek(0)  # Reset file pointer
            file_content = file.read()
            
            response = self.client.storage.from_(bucket).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": file.content_type or "application/octet-stream"
                }
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Upload failed: {response.json()}")
            
            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            
            return {
                'file_path': file_path,
                'public_url': public_url,
                'bucket': bucket,
                'original_filename': file.filename,
                'content_type': file.content_type,
                'file_size': len(file_content),
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def get_signed_url(self, bucket: str, file_path: str, expires_in: int = 3600) -> str:
        """
        Generate a signed URL for private file access
        
        Args:
            bucket: Supabase storage bucket name
            file_path: Path to file in storage
            expires_in: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Signed URL string
        """
        if not self.is_configured():
            # Demo mode - return placeholder signed URL
            print(f"Demo mode: Generating placeholder signed URL for {file_path}")
            return f"https://demo.supabase.co/storage/v1/object/sign/{bucket}/{file_path}?expires={expires_in}"
        
        try:
            response = self.client.storage.from_(bucket).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            
            if 'signedURL' in response:
                return response['signedURL']
            else:
                raise Exception("Failed to generate signed URL")
                
        except Exception as e:
            raise Exception(f"Failed to generate signed URL: {str(e)}")
    
    def delete_file(self, bucket: str, file_path: str) -> bool:
        """
        Delete a file from Supabase storage
        
        Args:
            bucket: Supabase storage bucket name
            file_path: Path to file in storage
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            raise Exception("Supabase is not configured")
        
        try:
            response = self.client.storage.from_(bucket).remove([file_path])
            return response.status_code in [200, 204]
            
        except Exception as e:
            print(f"Failed to delete file: {str(e)}")
            return False
    
    def list_files(self, bucket: str, folder: str = "", limit: int = 100) -> list:
        """
        List files in a bucket/folder
        
        Args:
            bucket: Supabase storage bucket name
            folder: Optional folder path
            limit: Maximum number of files to return
            
        Returns:
            List of file objects
        """
        if not self.is_configured():
            raise Exception("Supabase is not configured")
        
        try:
            response = self.client.storage.from_(bucket).list(
                path=folder,
                limit=limit
            )
            
            return response if isinstance(response, list) else []
            
        except Exception as e:
            print(f"Failed to list files: {str(e)}")
            return []
    
    def get_file_info(self, bucket: str, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information
        
        Args:
            bucket: Supabase storage bucket name
            file_path: Path to file in storage
            
        Returns:
            File information dictionary or None
        """
        if not self.is_configured():
            return None
        
        try:
            # List files in the directory containing the file
            folder = "/".join(file_path.split("/")[:-1])
            files = self.list_files(bucket, folder)
            
            filename = file_path.split("/")[-1]
            for file_info in files:
                if file_info.get('name') == filename:
                    return file_info
            
            return None
            
        except Exception as e:
            print(f"Failed to get file info: {str(e)}")
            return None

# Global instance
supabase_service = SupabaseService()

