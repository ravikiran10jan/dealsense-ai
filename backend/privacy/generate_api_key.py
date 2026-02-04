"""
API Key Generation CLI
Command-line tool to generate and manage API keys.
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from privacy.auth import get_auth_manager, ROLES


def main():
    parser = argparse.ArgumentParser(
        description='Generate and manage DealSense AI API keys',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  Generate admin key:
    python -m privacy.generate_api_key --user admin@example.com --role admin
    
  Generate seller key with expiration:
    python -m privacy.generate_api_key --user seller@example.com --role seller --expires 90
    
  List all keys:
    python -m privacy.generate_api_key --list
    
  Revoke all keys for a user:
    python -m privacy.generate_api_key --revoke-user seller@example.com

Available roles:
  admin    - Full access including PII and audit management
  seller   - Create deals, query RAG, manage own deals  
  readonly - Query RAG and view deals only
        '''
    )
    
    parser.add_argument(
        '--user', '-u',
        help='User ID (email or username) for the API key'
    )
    
    parser.add_argument(
        '--role', '-r',
        choices=list(ROLES.keys()),
        help='Role to assign to the user'
    )
    
    parser.add_argument(
        '--description', '-d',
        help='Optional description for the API key'
    )
    
    parser.add_argument(
        '--expires', '-e',
        type=int,
        help='Expiration in days (default: never expires)'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all API keys (metadata only)'
    )
    
    parser.add_argument(
        '--list-user',
        help='List API keys for a specific user'
    )
    
    parser.add_argument(
        '--revoke-user',
        help='Revoke all API keys for a user'
    )
    
    args = parser.parse_args()
    
    auth_manager = get_auth_manager()
    
    # List keys
    if args.list:
        keys = auth_manager.list_keys()
        if not keys:
            print("No API keys found.")
            return
        
        print(f"\n{'User ID':<30} {'Role':<10} {'Created':<20} {'Status':<10}")
        print("-" * 75)
        for key in keys:
            status = "Revoked" if key['revoked'] else "Active"
            if key['expires_at'] and not key['revoked']:
                from datetime import datetime
                expires = datetime.fromisoformat(key['expires_at'])
                if datetime.utcnow() > expires:
                    status = "Expired"
            
            created = key['created_at'][:10] if key['created_at'] else 'Unknown'
            print(f"{key['user_id']:<30} {key['role']:<10} {created:<20} {status:<10}")
        return
    
    # List keys for specific user
    if args.list_user:
        keys = auth_manager.list_keys(args.list_user)
        if not keys:
            print(f"No API keys found for user: {args.list_user}")
            return
        
        print(f"\nAPI keys for {args.list_user}:")
        print("-" * 50)
        for key in keys:
            status = "Revoked" if key['revoked'] else "Active"
            print(f"  Role: {key['role']}, Status: {status}")
            if key['description']:
                print(f"  Description: {key['description']}")
            if key['last_used']:
                print(f"  Last used: {key['last_used']}")
            print()
        return
    
    # Revoke keys for user
    if args.revoke_user:
        count = auth_manager.revoke_user_keys(args.revoke_user)
        print(f"Revoked {count} API key(s) for user: {args.revoke_user}")
        return
    
    # Generate new key
    if not args.user or not args.role:
        parser.error("--user and --role are required to generate a new API key")
    
    try:
        api_key = auth_manager.generate_api_key(
            user_id=args.user,
            role=args.role,
            description=args.description,
            expires_in_days=args.expires
        )
        
        print("\n" + "=" * 60)
        print("API KEY GENERATED SUCCESSFULLY")
        print("=" * 60)
        print(f"\nUser:   {args.user}")
        print(f"Role:   {args.role}")
        if args.expires:
            print(f"Expires: In {args.expires} days")
        else:
            print("Expires: Never")
        
        print(f"\nAPI Key: {api_key}")
        print("\n" + "-" * 60)
        print("IMPORTANT: Store this key securely!")
        print("It will NOT be shown again.")
        print("-" * 60 + "\n")
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
