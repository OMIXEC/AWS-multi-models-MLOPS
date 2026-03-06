# Azure Blob Storage Setup

This module is responsible for automating the creation of Azure Storage Accounts, Blob Containers, and managing ML model artifact uploads using the `azure-storage-blob` Python SDK.

## Prerequisites
- Authenticate via the Azure CLI (`az login`) or by using connection strings.
- Install the required library:
  ```bash
  pip install azure-storage-blob azure-identity
  ```
