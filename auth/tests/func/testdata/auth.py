TOKENS = [
    {
        "type": "access_token",
        "payload_fields": ["sub", "device_id", "roles", "exp"],
    },
    {"type": "refresh_token", "payload_fields": ["sub", "device_id", "exp"]},
]

GET_REFRESH_TOKEN_REQUEST = """
    SELECT * FROM public.user
        JOIN public.refresh_token AS token
        ON token.user_id=public.user.id
        WHERE public.user.login='superuser'
"""

INSERT_SUPERUSER_DEVICE_REQUEST = """
    INSERT INTO "device" (
        id,
        user_id,
        user_agent,
        created_at,
        modified_at
        )
    VALUES (
        '8afd98c5-a349-4904-b5a8-403e61517999',
        '11111111-1111-1111-1111-111111111111',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        '2024-04-26 17:26:11.42932',
        '2024-04-26 17:26:11.42932'
    );
"""

INSERT_SUPERUSER_REFRESH_TOKEN_REQUEST = """
    INSERT INTO "refresh_token" (
        id,
        user_id,
        device_id,
        refresh_token,
        created_at
        )
    VALUES (
        '8afd98c5-a349-4904-b5a8-403e61517999',
        '11111111-1111-1111-1111-111111111111',
        '8afd98c5-a349-4904-b5a8-403e61517999',
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzdXBlcnVzZXIiLCJkZXZpY2VfaWQiOiI4YWZkOThjNS1hMzQ5LTQ5MDQtYjVhOC00MDNlNjE1MTc5OTkiLCAiZXhwIjoiMTgxNDIyMTg0MS45NTUyMyJ9.bfb3b273ac81cd272d5c402e806dd9158c085ba629cca3d40eb0e03f39b37995',
        '2024-04-26 17:26:11.42932'
    );
"""


# 'eyd0eXAnOiAnSldUJywgJ2FsZyc6ICdIUzI1Nid9.eydzdWInOiAnc3VwZXJ1c2VyJywgJ2ZpbmdlcnByaW50JzogJzkxMjA2MzA4OTg3NjYwNzMzNScsICdleHAnOiAnMTgxNTUwODAwNS42NTU4Myd9.7b6f957ab28921c15e543f79718cc08b1fe936abf8350c222e391327fba4731f',
