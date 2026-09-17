# API Reference

All protected endpoints require an authenticated web session.

## Health

`GET /health`

Returns:

```json
{"status": "ok", "service": "business-support-platform"}
```

## Dashboard

`GET /api/dashboard`

Returns counts for active customers, ticket statuses and high-priority open tickets.

## Tickets

`GET /api/tickets`

Optional query:

`GET /api/tickets?status=Open`

`POST /api/tickets`

Example:

```json
{
  "title": "Unable to access monthly report",
  "description": "Customer cannot download the report.",
  "priority": "High",
  "customer_id": 1
}
```

Response status: `201 Created`.

## Error responses

- `400` invalid or missing request data
- `401` authentication required
- `403` insufficient role permission
- `404` resource not found
