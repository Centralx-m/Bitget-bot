# API Documentation - XTAAGC Bot

## Authentication
All API endpoints require JWT authentication via Bearer token.

### Login
`POST /api/auth/login`
```json
{
  "username": "user",
  "password": "pass"
}