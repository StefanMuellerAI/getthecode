#!/usr/bin/env python3
"""
Migration script to encrypt existing plaintext data in the database.

This script reads all unencrypted data from the database and encrypts
the relevant fields in place.

USAGE:
    # Set the encryption key first
    export ENCRYPTION_KEY="your-base64-encoded-32-byte-key"
    
    # Run the migration (dry run by default)
    python scripts/migrate_encryption.py
    
    # Run the actual migration
    python scripts/migrate_encryption.py --execute

WARNINGS:
    - BACKUP YOUR DATABASE BEFORE RUNNING THIS SCRIPT!
    - Once encrypted, data can only be decrypted with the same key
    - Key loss = permanent data loss
"""
import asyncio
import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg
from app.config import get_settings
from app.encryption import encrypt_field, is_encryption_enabled, ENCRYPTION_PREFIX


async def get_connection():
    """Create a database connection."""
    settings = get_settings()
    return await asyncpg.connect(settings.database_url)


def is_already_encrypted(value: str | None) -> bool:
    """Check if a value is already encrypted."""
    if value is None:
        return True  # Nothing to encrypt
    return value.startswith(ENCRYPTION_PREFIX)


async def migrate_messages(conn: asyncpg.Connection, dry_run: bool = True) -> int:
    """Encrypt content and sanitized_content in messages table."""
    print("\n📝 Migrating messages table...")
    
    # Fetch all messages with unencrypted content
    rows = await conn.fetch(
        """
        SELECT id, content, sanitized_content 
        FROM messages 
        WHERE content IS NOT NULL AND content NOT LIKE $1
        """,
        f"{ENCRYPTION_PREFIX}%"
    )
    
    count = 0
    for row in rows:
        content = row["content"]
        sanitized = row["sanitized_content"]
        
        if is_already_encrypted(content) and is_already_encrypted(sanitized):
            continue
        
        encrypted_content = encrypt_field(content)
        encrypted_sanitized = encrypt_field(sanitized)
        
        if not dry_run:
            await conn.execute(
                """
                UPDATE messages 
                SET content = $1, sanitized_content = $2 
                WHERE id = $3
                """,
                encrypted_content, encrypted_sanitized, row["id"]
            )
        
        count += 1
        if count % 100 == 0:
            print(f"  Processed {count} messages...")
    
    print(f"  {'Would encrypt' if dry_run else 'Encrypted'} {count} messages")
    return count


async def migrate_gift_codes(conn: asyncpg.Connection, dry_run: bool = True) -> int:
    """Encrypt code field in gift_codes table."""
    print("\n🎁 Migrating gift_codes table...")
    
    rows = await conn.fetch(
        """
        SELECT id, code 
        FROM gift_codes 
        WHERE code IS NOT NULL AND code NOT LIKE $1
        """,
        f"{ENCRYPTION_PREFIX}%"
    )
    
    count = 0
    for row in rows:
        if is_already_encrypted(row["code"]):
            continue
        
        encrypted_code = encrypt_field(row["code"])
        
        if not dry_run:
            await conn.execute(
                "UPDATE gift_codes SET code = $1 WHERE id = $2",
                encrypted_code, row["id"]
            )
        
        count += 1
    
    print(f"  {'Would encrypt' if dry_run else 'Encrypted'} {count} gift codes")
    return count


async def migrate_claims(conn: asyncpg.Connection, dry_run: bool = True) -> int:
    """Encrypt claimed_code and claim_message in winner_claims table."""
    print("\n🏆 Migrating winner_claims table...")
    
    rows = await conn.fetch(
        """
        SELECT id, claimed_code, claim_message 
        FROM winner_claims 
        WHERE claimed_code NOT LIKE $1 OR (claim_message IS NOT NULL AND claim_message NOT LIKE $1)
        """,
        f"{ENCRYPTION_PREFIX}%"
    )
    
    count = 0
    for row in rows:
        claimed_code = row["claimed_code"]
        claim_message = row["claim_message"]
        
        if is_already_encrypted(claimed_code) and is_already_encrypted(claim_message):
            continue
        
        encrypted_code = encrypt_field(claimed_code)
        encrypted_message = encrypt_field(claim_message)
        
        if not dry_run:
            await conn.execute(
                """
                UPDATE winner_claims 
                SET claimed_code = $1, claim_message = $2 
                WHERE id = $3
                """,
                encrypted_code, encrypted_message, row["id"]
            )
        
        count += 1
    
    print(f"  {'Would encrypt' if dry_run else 'Encrypted'} {count} claims")
    return count


async def migrate_email_verifications(conn: asyncpg.Connection, dry_run: bool = True) -> int:
    """Encrypt code field in email_verifications table."""
    print("\n✉️ Migrating email_verifications table...")
    
    rows = await conn.fetch(
        """
        SELECT id, code 
        FROM email_verifications 
        WHERE code IS NOT NULL AND code NOT LIKE $1
        """,
        f"{ENCRYPTION_PREFIX}%"
    )
    
    count = 0
    for row in rows:
        if is_already_encrypted(row["code"]):
            continue
        
        encrypted_code = encrypt_field(row["code"])
        
        if not dry_run:
            await conn.execute(
                "UPDATE email_verifications SET code = $1 WHERE id = $2",
                encrypted_code, row["id"]
            )
        
        count += 1
    
    print(f"  {'Would encrypt' if dry_run else 'Encrypted'} {count} verification codes")
    return count


async def migrate_challenge_attempts(conn: asyncpg.Connection, dry_run: bool = True) -> int:
    """Encrypt user_prompt and ai_response in challenge_attempts table."""
    print("\n🎯 Migrating challenge_attempts table...")
    
    rows = await conn.fetch(
        """
        SELECT id, user_prompt, ai_response 
        FROM challenge_attempts 
        WHERE user_prompt NOT LIKE $1 OR ai_response NOT LIKE $1
        """,
        f"{ENCRYPTION_PREFIX}%"
    )
    
    count = 0
    for row in rows:
        prompt = row["user_prompt"]
        response = row["ai_response"]
        
        if is_already_encrypted(prompt) and is_already_encrypted(response):
            continue
        
        encrypted_prompt = encrypt_field(prompt)
        encrypted_response = encrypt_field(response)
        
        if not dry_run:
            await conn.execute(
                """
                UPDATE challenge_attempts 
                SET user_prompt = $1, ai_response = $2 
                WHERE id = $3
                """,
                encrypted_prompt, encrypted_response, row["id"]
            )
        
        count += 1
        if count % 100 == 0:
            print(f"  Processed {count} attempts...")
    
    print(f"  {'Would encrypt' if dry_run else 'Encrypted'} {count} challenge attempts")
    return count


async def run_migration(dry_run: bool = True):
    """Run the full encryption migration."""
    print("=" * 60)
    print("DATABASE ENCRYPTION MIGRATION")
    print("=" * 60)
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made")
        print("   Run with --execute to apply changes\n")
    else:
        print("\n🔐 EXECUTING MIGRATION - Changes will be applied\n")
    
    # Check if encryption is enabled
    if not is_encryption_enabled():
        print("❌ ERROR: ENCRYPTION_KEY is not set!")
        print("   Set the ENCRYPTION_KEY environment variable first.")
        print("   Generate one with: python -c \"import os, base64; print(base64.b64encode(os.urandom(32)).decode())\"")
        return False
    
    print("✅ Encryption key is configured")
    
    conn = await get_connection()
    
    try:
        total = 0
        
        total += await migrate_messages(conn, dry_run)
        total += await migrate_gift_codes(conn, dry_run)
        total += await migrate_claims(conn, dry_run)
        total += await migrate_email_verifications(conn, dry_run)
        total += await migrate_challenge_attempts(conn, dry_run)
        
        print("\n" + "=" * 60)
        if dry_run:
            print(f"📊 SUMMARY: Would encrypt {total} total records")
            print("   Run with --execute to apply changes")
        else:
            print(f"✅ COMPLETED: Encrypted {total} total records")
        print("=" * 60)
        
        return True
        
    finally:
        await conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Encrypt existing plaintext data in the database"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the migration (default is dry run)"
    )
    
    args = parser.parse_args()
    
    success = asyncio.run(run_migration(dry_run=not args.execute))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

