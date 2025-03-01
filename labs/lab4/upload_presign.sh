#!/bin/bash

# Check if the correct number of arguments is provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <local_file> <bucket_name> <expiration_in_seconds>"
    exit 1
fi

# Assign arguments to variables
LOCAL_FILE=$1
BUCKET_NAME=$2
EXPIRATION=$3

# Validate that the local file exists
if [ ! -f "$LOCAL_FILE" ]; then
    echo "Error: File '$LOCAL_FILE' does not exist."
    exit 1
fi

# Upload the file to the S3 bucket
aws s3 cp "$LOCAL_FILE" "s3://$BUCKET_NAME/" --acl private
if [ $? -ne 0 ]; then
    echo "Error: Failed to upload '$LOCAL_FILE' to bucket '$BUCKET_NAME'."
    exit 1
fi

# Extract the file name for the presigned URL
FILE_NAME=$(basename "$LOCAL_FILE")

# Generate a presigned URL with the specified expiration time
PRESIGNED_URL=$(aws s3 presign "s3://$BUCKET_NAME/$FILE_NAME" --expires-in $EXPIRATION)

if [ $? -ne 0 ]; then
    echo "Error: Failed to generate presigned URL."
    exit 1
fi

# Display the presigned URL
echo "Presigned URL (expires in $EXPIRATION seconds):"
echo $PRESIGNED_URL
