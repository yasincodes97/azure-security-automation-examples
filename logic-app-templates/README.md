# Azure Logic App Templates

Example Azure Logic App workflow definitions demonstrating practical automation patterns in Microsoft Azure.

## Templates

| File | Purpose |
|---|---|
| [`entra-id-offboarding-notification.json`](./entra-id-offboarding-notification.json) | Polls Entra ID for newly disabled user accounts and notifies a Teams channel to confirm offboarding checklist completion (license removal, mailbox handling, group cleanup) - with deduplication to avoid repeat notifications |
| [`cost-anomaly-alert.json`](./cost-anomaly-alert.json) | Scheduled daily check comparing Azure spend against a stored baseline average, alerting a Teams channel and logging to Log Analytics when spend increases significantly |

## Architecture Patterns

**Entra ID Offboarding Notification** - event-driven polling pattern:
1. Recurrence trigger polls Entra ID every 15 minutes for disabled accounts
2. For each disabled user, check Azure Table Storage to avoid duplicate notifications
3. Post a Teams notification with user details for the IT/security team to act on
4. Record that the notification was sent

**Cost Anomaly Alert** - scheduled comparison pattern:
1. Daily recurrence trigger queries Azure Cost Management for the previous day's spend
2. Compare against a stored baseline average
3. If the increase exceeds a threshold (20%), alert a Teams channel and log the anomaly for tracking

Both patterns are adaptable - swap the notification channel (Teams, Slack, email), the data source, or the threshold logic to fit different use cases.

## Note

All connection IDs, resource names, subscription IDs, and tenant-specific values in these templates are placeholders. Replace with your own Azure resource references before use.
