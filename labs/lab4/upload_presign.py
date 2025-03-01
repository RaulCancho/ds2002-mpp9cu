import boto3
import requests
import os
import sys
import mimetypes

# Ensure correct usage
if len(sys.argv) != 4:
    print("Usage: python upload_and_presign.py <image_url> <bucket_name> <expiration_time>")
    sys.exit(1)

# Get arguments from command line
image_url = sys.argv[1]
bucket_name = sys.argv[2]
expiration_time = int(sys.argv[3])

# Extract the correct filename (remove URL parameters)
filename = image_url.split("/")[-1].split("?")[0]  # Removes extra parameters
local_path = f"/tmp/{filename}"  # Save file temporarily

# Download the image
print(f"Downloading image from {image_url}...")
try:
    response = requests.get(image_url)
    response.raise_for_status()  # Raises an exception for HTTP errors
    
    with open(local_path, "wb") as f:
        f.write(response.content)
    print(f"Image saved as {local_path}")
    
    # Try to determine content type
    content_type = response.headers.get('Content-Type')
    if not content_type:
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
except Exception as e:
    print(f"Error: Failed to download image. {e}")
    sys.exit(1)

# Upload the file to S3
try:
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.upload_file(
        local_path, 
        bucket_name, 
        filename, 
        ExtraArgs={"ContentType": content_type}
    )
    print(f"File uploaded to S3 bucket: {bucket_name}")
    
    # Generate a presigned URL
    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": filename},
        ExpiresIn=expiration_time
    )
    print(f"Presigned URL (valid for {expiration_time} seconds):\n{presigned_url}")
    
    # Clean up the temporary file
    os.remove(local_path)
    print(f"Temporary file removed: {local_path}")
    
except Exception as e:
    print(f"Error during S3 operations: {e}")
    sys.exit(1)