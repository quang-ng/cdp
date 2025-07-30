# tap-yotpo

Singer.io tap for extracting email data from the Yotpo API.

## Usage

Install dependencies:

```bash
pip install .
```

Run discovery (prints schema):

```bash
tap-yotpo --config config.json --discover
```

Run sync (extracts emails):

```bash
tap-yotpo --config config.json > output.json
```

## Example `config.json`

```json
{
  "app_key": "your_yotpo_app_key",
  "secret": "your_yotpo_secret",
  "start_date": "2024-01-01T00:00:00Z"
}
```

## Output

Singer-formatted JSON records for the `emails` stream.

## Notes
- This is a minimal example for the Yotpo email stream. Extend as needed for other streams.
- Handles pagination and incremental sync via `start_date`.
