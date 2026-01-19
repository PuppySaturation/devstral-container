#!/usr/bin/env python3
"""Migrate existing streaming response logs to compacted format."""

import sqlite3
import json
import sys

def compact_streaming_response(raw_body: str) -> str:
    """Compact SSE streaming chunks into a single response."""
    chunks = []
    content_parts = []
    metadata = {}

    for line in raw_body.split('\n'):
        line = line.strip()
        if not line.startswith('data:'):
            continue

        data_str = line[5:].strip()
        if data_str == '[DONE]':
            continue

        try:
            chunk = json.loads(data_str)
            chunks.append(chunk)

            # Extract metadata from first chunk
            if not metadata and 'id' in chunk:
                metadata = {
                    'id': chunk.get('id'),
                    'model': chunk.get('model'),
                    'created': chunk.get('created'),
                    'object': 'chat.completion'
                }

            # Extract content from choices
            for choice in chunk.get('choices', []):
                delta = choice.get('delta', {})
                if 'content' in delta and delta['content']:
                    content_parts.append(delta['content'])
                if 'finish_reason' in choice and choice['finish_reason']:
                    metadata['finish_reason'] = choice['finish_reason']
        except json.JSONDecodeError:
            continue

    if not chunks:
        return raw_body

    # Build compacted response
    compacted = {
        **metadata,
        'choices': [{
            'index': 0,
            'message': {
                'role': 'assistant',
                'content': ''.join(content_parts)
            },
            'finish_reason': metadata.get('finish_reason', 'stop')
        }],
        '_streaming': True,
        '_chunk_count': len(chunks)
    }

    return json.dumps(compacted, indent=2)


def migrate(db_path: str, dry_run: bool = False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find all rows with streaming response format
    cursor.execute('''
        SELECT id, response_body FROM api_logs
        WHERE response_body LIKE 'data:%'
    ''')

    rows = cursor.fetchall()
    print(f"Found {len(rows)} streaming responses to migrate")

    migrated = 0
    for row_id, response_body in rows:
        compacted = compact_streaming_response(response_body)

        # Skip if no change (already compacted or not valid streaming)
        if compacted == response_body:
            continue

        if dry_run:
            print(f"Would migrate row {row_id}: {len(response_body)} -> {len(compacted)} bytes")
        else:
            cursor.execute('''
                UPDATE api_logs SET response_body = ? WHERE id = ?
            ''', (compacted, row_id))
            print(f"Migrated row {row_id}: {len(response_body)} -> {len(compacted)} bytes")

        migrated += 1

    if not dry_run:
        conn.commit()
        print(f"\nMigrated {migrated} rows")
    else:
        print(f"\nDry run: would migrate {migrated} rows")

    conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: migrate_logs.py <db_path> [--dry-run]")
        print("Example: migrate_logs.py ~/.config/devstral-container/proxy/logs.db")
        sys.exit(1)

    db_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    migrate(db_path, dry_run)
