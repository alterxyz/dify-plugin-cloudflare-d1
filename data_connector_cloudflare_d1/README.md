# Cloudflare D1 Data Connector for Dify

A Dify plugin that allows you to connect to Cloudflare D1 databases, execute SQL queries, and integrate database operations into your AI applications.

## Overview

Cloudflare D1 is a serverless SQL database with SQLite semantics, offering:

- Built-in disaster recovery
- Worker and HTTP API access
- Horizontal scaling across multiple smaller databases
- Time Travel for point-in-time recovery

This connector enables seamless integration with Dify's AI workflow, allowing your AI agents to directly query and retrieve data from your D1 databases.

## Features

- **SQL Query Execution**: Execute SQL queries against Cloudflare D1 databases
- **Token Verification**: Verify Cloudflare API token validity
- **Parameterized Queries**: Support for secure parameterized SQL queries
- **Error Handling**: Comprehensive error reporting and handling

## Setup Requirements

### Prerequisites

- A Cloudflare account
- At least one D1 database created
- API token with D1 access permissions

### Required Credentials

1. **Cloudflare API Token**:

    - Create at: <https://developers.cloudflare.com/fundamentals/api/get-started/create-token/>
    - Required permissions: D1 read/write access

2. **Cloudflare Account ID**:
    - Find at: <https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/>

### Database Information

For each query, you'll need:

- **Database ID**: The unique identifier of your D1 database
- **SQL Query**: The query to execute
- **Parameters** (optional): Values for parameterized queries

## Error Handling

The connector provides detailed error information when queries fail:

- **API Errors**: Returns specific Cloudflare API error codes and messages
- **HTTP Errors**: Returns status codes and error details
- **Connection Errors**: Provides relevant connection error information

## Best Practices

1. **Use Parameterized Queries**: Always use parameter placeholders (`?`) for dynamic values
2. **Verify Tokens**: Test API token validity with the verification tool before executing queries
3. **Handle Errors**: Always implement proper error handling in your applications

## Limitations

- Follows Cloudflare D1 service limits (see: <https://developers.cloudflare.com/d1/platform/limits/>)
- Maximum recommended database size: 10GB
- Connection timeouts may occur for very complex queries

## Additional Resources

- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/)
- [Cloudflare API Documentation](https://developers.cloudflare.com/api/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
