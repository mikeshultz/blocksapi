#!/bin/bash

VERSION="$1"
AWS_ACCOUNT_ID="525686199231"

echo "Logging in to ECR..."
$(aws --profile gointo ecr get-login --no-include-email --region us-west-2)

echo "Building and deploying..."
docker build -t blocksapi:$VERSION . && \
docker tag blocksapi:$VERSION $AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/blocksapi:$VERSION && \
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/blocksapi:$VERSION

echo "Fin."