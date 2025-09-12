# CI/CD — App Runner via GitHub OIDC

This repo deploys to AWS App Runner using a reusable workflow defined in this same repository. No per-run AWS keys; OIDC-only. Any chat/AI can deploy by commenting `/deploy` or running the action manually.

## Prerequisites (one-time)

1) GitHub org secret
- Name: `GH_WORKFLOW_TOKEN`
- Scopes: `repo` + `workflow`
- Purpose: used only to send a repository_dispatch event for `/deploy`.

2) GitHub org variables
- `AWS_REGION` — e.g., `us-east-1`
- `AWS_ROLE_DEPLOY` — OIDC role ARN that Actions assumes to deploy, e.g., `arn:aws:iam::<ACCOUNT_ID>:role/FridayDeployRole`

3) Per-repo variable
- `ECR_REPOSITORY` — ECR repo name for this service, e.g., `friday-starter`

## AWS IAM trust (one-time)

- Create OIDC provider: `token.actions.githubusercontent.com` with audience `sts.amazonaws.com`.
- Create deploy role (e.g., `FridayDeployRole`) with trust policy:

```json
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Effect":"Allow",
      "Principal":{"Federated":"arn:aws:iam::```

- Attach permissions to allow:
  - ECR push/pull
  - App Runner create/update service
  - IAM: GetRole
  - Optionally, to let the workflow auto-create the App Runner ECR access role: `iam:CreateRole` and `iam:AttachRolePolicy`. If you prefer not to grant these, pre-create a role named `FridayAppRunnerECRAccess` with policy `AWSAppRunnerServicePolicyForECRAccess`.

## How it works

- Reusable workflow lives at `.github/workflows/apprunner.yml` in this repo.
- The caller workflow `.github/workflows/deploy.yml` invokes it.
- Deploy triggers:
  - Push to `main`
  - Manual run (`workflow_dispatch`)
  - Comment `/deploy` on an issue (sends `repository_dispatch` event)

## Health check

The workflow curls `GET /health`. If your app uses a different path, adjust the URL in the reusable workflow or add a `/health` endpoint.

## Troubleshooting

- Missing `GH_WORKFLOW_TOKEN` or org variables: runs will fail early. Set at org level.
- OIDC trust filter: ensure `sub = repo:jacksonchami117-ui/*:ref:refs/heads/main` or adjust to match your branch pattern.
- App Runner ECR access role: workflow auto-creates `FridayAppRunnerECRAccess` if allowed; otherwise create it manually.