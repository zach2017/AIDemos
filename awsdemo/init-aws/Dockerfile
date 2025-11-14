# Use the same base image
FROM amazon/aws-cli:2.13.25

# Install the "zip" utility, which the init.sh script needs
RUN apk add --no-cache zip

# Copy the init script from the host (relative to build context)
# and make it executable
COPY ./init-aws/init.sh /scripts/init.sh
RUN chmod +x /scripts/init.sh

# Copy the lambda code from the host (relative to build context)
# so the init script can find it to create the zip
COPY ./lambda /lambda_code