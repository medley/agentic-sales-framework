# ZoomInfo Client Quick Start

**Production-ready ZoomInfo API client for contact search and company enrichment using PKI authentication**

## 30-Second Setup

```python
from prospecting.src.zoominfo_jwt_manager import ZoomInfoJWTManager
from prospecting.src.zoominfo_client import ZoomInfoClient

# Initialize JWT manager (reads from .env)
jwt_manager = ZoomInfoJWTManager()

# Create client with JWT authentication
client = ZoomInfoClient(jwt_manager)

# Search for a contact
contact = client.search_contact("John Smith", "Acme Corp")

# Enrich company (if contact found)
if contact and contact.get('company_id'):
    company = client.enrich_company(contact['company_id'])
```

## Environment Setup

Create a `.env` file with your ZoomInfo PKI credentials:

```bash
# Get these from your ZoomInfo admin console
ZOOMINFO_USERNAME=your_username@example.com
ZOOMINFO_CLIENT_ID=your-client-id-uuid
ZOOMINFO_PRIVATE_KEY_FILE=.zoominfo_private_key.pem
```

## Methods

### `search_contact(name, company_name)`

**Returns:** Contact info or None

```python
{
    'contact_id': str,
    'first_name': str,
    'last_name': str,
    'title': str,
    'email': str,
    'phone': str,
    'company_id': str
}
```

**Name formats supported:**
- "John Smith"
- "Smith, John"
- "John Robert Smith"

**Error handling:**
- Returns `None` on timeout/connection errors
- Raises `ZoomInfoRateLimitError` on 429
- Raises `ZoomInfoAPIError` on other errors

### `enrich_company(company_id)`

**Returns:** Company data

```python
{
    'revenue': str,              # e.g., "$100M-$500M"
    'employee_count': int,
    'industry': str,
    'tech_stack': List[str],
    'intent_signals': List[str]
}
```

## Error Handling

```python
from prospecting.src.zoominfo_client import (
    ZoomInfoRateLimitError,
    ZoomInfoAPIError
)

jwt_manager = ZoomInfoJWTManager()
client = ZoomInfoClient(jwt_manager)

try:
    contact = client.search_contact(name, company)
    if contact:
        company = client.enrich_company(contact['company_id'])
except ZoomInfoRateLimitError:
    # Wait and retry
    pass
except ZoomInfoAPIError as e:
    # Handle other errors
    pass
```

## Features

- ✓ PKI/JWT authentication (username + client_id + private key)
- ✓ Automatic retries (3x with exponential backoff)
- ✓ Request timeout (30s default)
- ✓ Comprehensive logging
- ✓ Type hints throughout
- ✓ Name parsing (multiple formats)
- ✓ Specific exception types
- ✓ Rate limit detection

## Testing

```bash
# Ensure .env is configured with credentials
python scripts/utilities/test_zoominfo.py "John Smith" "Acme Corporation"
```

## File Location

**Target files:**
- `src/zoominfo_client.py` - Main client
- `src/zoominfo_jwt_manager.py` - JWT authentication handler

## Integration Points

**1. Research orchestrator** (`research_orchestrator.py`)
```python
jwt_manager = ZoomInfoJWTManager()
zoominfo = ZoomInfoClient(jwt_manager)
contact = zoominfo.search_contact(name, company)
```

**2. Pre-call prep** (enrich contact data)
```python
# Get latest company intel before call
company_data = client.enrich_company(company_id)
intent_signals = company_data.get('intent_signals', [])
```

## Design Principles

1. **Fail gracefully** - Return None instead of raising on timeouts
2. **Log everything** - All API calls logged with context
3. **Type safety** - Full type hints for IDE support
4. **Specific errors** - Different exceptions for different failure modes
5. **Production-ready** - Retries, timeouts, error handling built-in

## See Also

- **Test script:** `scripts/utilities/test_zoominfo.py`
- **Source code:** `src/zoominfo_client.py`, `src/zoominfo_jwt_manager.py`
