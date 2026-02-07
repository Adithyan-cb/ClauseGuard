"""
Management command to test and diagnose ChromaDB functionality.

Usage:
    python manage.py test_chromadb
    python manage.py test_chromadb --collection SERVICE_AGREEMENT_INDIA
    python manage.py test_chromadb --search "payment terms"
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import json
import logging

# Import our services
from myapp.services.chroma_manager import ChromaManager, CHROMADB_AVAILABLE
from myapp.services.contract_clause_mapping import ContractClauseMapper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test and diagnose ChromaDB functionality for clause mapping'

    def add_arguments(self, parser):
        parser.add_argument(
            '--collection',
            type=str,
            help='Test specific collection (e.g., SERVICE_AGREEMENT_INDIA)',
        )
        parser.add_argument(
            '--search',
            type=str,
            help='Test search with specific query text',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all ChromaDB collections (delete and reinitialize)',
        )
        parser.add_argument(
            '--init-clauses',
            action='store_true',
            help='Initialize/load all standard clauses into ChromaDB',
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(self.style.HTTP_INFO("\n" + "="*80))
        self.stdout.write(self.style.HTTP_INFO("ChromaDB Diagnostic Tool"))
        self.stdout.write(self.style.HTTP_INFO("="*80 + "\n"))

        # Check if ChromaDB is available
        if not CHROMADB_AVAILABLE:
            self.stdout.write(
                self.style.ERROR(
                    "✗ ChromaDB is NOT installed or available!\n"
                    "Install with: pip install chromadb 'sentence-transformers[torch]'"
                )
            )
            return

        self.stdout.write(self.style.SUCCESS("✓ ChromaDB is available\n"))

        # Initialize ChromaManager
        try:
            self.stdout.write("Initializing ChromaManager...")
            chroma = ChromaManager()
            
            if not chroma.available:
                self.stdout.write(
                    self.style.ERROR("✗ ChromaManager failed to initialize")
                )
                return
            
            self.stdout.write(self.style.SUCCESS("✓ ChromaManager initialized\n"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error initializing ChromaManager: {str(e)}")
            )
            return

        # Initialize ContractClauseMapper
        try:
            self.stdout.write("Loading standard clauses...")
            mapper = ContractClauseMapper()
            contract_types = mapper.get_all_contract_types()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Loaded {len(contract_types)} contract types\n")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Error loading clauses: {str(e)}")
            )
            return

        # Handle --reset option
        if options.get('reset'):
            self._handle_reset(chroma, mapper, contract_types)

        # Handle --init-clauses option
        if options.get('init_clauses'):
            self._handle_init_clauses(chroma, mapper, contract_types)

        # Run general diagnostics
        self._run_diagnostics(chroma, mapper, contract_types)

        # Handle --collection option
        if options.get('collection'):
            self._handle_collection(
                chroma, mapper, options['collection']
            )

        # Handle --search option
        if options.get('search'):
            self._handle_search(
                chroma, mapper, options['search']
            )

        self.stdout.write(self.style.HTTP_INFO("="*80 + "\n"))

    def _run_diagnostics(self, chroma, mapper, contract_types):
        """Run general diagnostics"""
        self.stdout.write(self.style.HTTP_INFO("\n📊 DIAGNOSTICS\n"))

        # 1. Check ChromaDB persistence directory
        persist_dir = getattr(
            settings,
            'CHROMA_DATA_DIR',
            os.path.join(settings.BASE_DIR, 'chroma_data')
        )
        
        self.stdout.write(f"\n1️⃣  ChromaDB Persistence Directory:")
        self.stdout.write(f"   Path: {persist_dir}")
        
        if os.path.exists(persist_dir):
            self.stdout.write(self.style.SUCCESS(f"   ✓ Directory exists"))
            
            # Check for database files
            sqlite_file = os.path.join(persist_dir, 'chroma.sqlite3')
            if os.path.exists(sqlite_file):
                size_kb = os.path.getsize(sqlite_file) / 1024
                self.stdout.write(
                    self.style.SUCCESS(f"   ✓ Database file found: {size_kb:.2f} KB")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"   ⚠ No database file found (will be created on first insert)")
                )
        else:
            self.stdout.write(self.style.WARNING(f"   ⚠ Directory doesn't exist yet"))

        # 2. Standard Clauses File
        self.stdout.write(f"\n2️⃣  Standard Clauses JSON File:")
        json_path = mapper._get_json_path()
        self.stdout.write(f"   Path: {json_path}")
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                clauses_data = json.load(f)
            total_clauses = 0
            for contract_type, data in clauses_data.items():
                count = (
                    len(data.get('critical_clauses', [])) +
                    len(data.get('important_clauses', [])) +
                    len(data.get('optional_clauses', []))
                )
                total_clauses += count
            
            self.stdout.write(self.style.SUCCESS(f"   ✓ File found"))
            self.stdout.write(f"   Contract types: {len(clauses_data)}")
            self.stdout.write(f"   Total clauses: {total_clauses}")
        else:
            self.stdout.write(self.style.ERROR(f"   ✗ File not found!"))

        # 3. Contract Types
        self.stdout.write(f"\n3️⃣  Supported Contract Types: ({len(contract_types)})")
        for i, contract_type_key in enumerate(contract_types, 1):
            # Correctly parse contract type and jurisdiction
            parts = contract_type_key.rsplit('_', 1)
            if len(parts) == 2:
                contract_type, jurisdiction = parts
            else:
                contract_type = contract_type_key
                jurisdiction = 'INDIA'
            
            all_clauses = mapper.get_all_clauses_flat(contract_type, jurisdiction)
            total = len(all_clauses)
            self.stdout.write(f"   {i}. {contract_type_key}: {total} clauses")

    def _handle_collection(self, chroma, mapper, collection_name):
        """Handle --collection option"""
        self.stdout.write(
            self.style.HTTP_INFO(f"\n🔍 COLLECTION ANALYSIS: {collection_name}\n")
        )

        # Get collection from ChromaDB
        collection = chroma.get_or_create_collection(collection_name)
        
        if collection is None:
            self.stdout.write(
                self.style.WARNING(f"   ⚠ Collection exists but couldn't be accessed")
            )
            return

        # Count documents in collection
        try:
            # Try to get collection count
            result = collection.get()
            doc_count = len(result['ids']) if result['ids'] else 0
            
            self.stdout.write(f"Collection: {collection_name}")
            self.stdout.write(f"Documents in ChromaDB: {doc_count}")
            
            if doc_count > 0:
                self.stdout.write(self.style.SUCCESS(f"✓ ChromaDB has {doc_count} clauses stored"))
                
                # Show first few documents
                self.stdout.write(f"\nFirst {min(5, doc_count)} clauses:")
                for i, (id_, doc, metadata) in enumerate(
                    zip(result['ids'][:5], result['documents'][:5], result['metadatas'][:5]),
                    1
                ):
                    self.stdout.write(f"\n   {i}. ID: {id_}")
                    self.stdout.write(f"      Type: {metadata.get('type', 'N/A')}")
                    self.stdout.write(f"      Text (first 100 chars): {doc[:100]}...")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠ No clauses found in ChromaDB for {collection_name}\n"
                        f"   Run: python manage.py test_chromadb --init-clauses"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"   ⚠ Could not fetch collection data: {str(e)}")
            )

    def _handle_search(self, chroma, mapper, query_text):
        """Handle --search option"""
        self.stdout.write(self.style.HTTP_INFO(f"\n🔎 SEARCH TEST\n"))
        self.stdout.write(f"Query: '{query_text}'\n")

        # Test with first available contract type
        contract_types = mapper.get_all_contract_types()
        if not contract_types:
            self.stdout.write(
                self.style.ERROR("No contract types available")
            )
            return

        test_collection = contract_types[0]
        self.stdout.write(f"Testing with collection: {test_collection}\n")

        # Perform search
        results = chroma.search_similar_clauses(
            collection_name=test_collection,
            query_text=query_text,
            top_k=3
        )

        if not results or not results['documents']:
            self.stdout.write(
                self.style.WARNING(f"⚠ No similar clauses found")
            )
            return

        self.stdout.write(self.style.SUCCESS(f"✓ Found {len(results['documents'])} similar clauses:\n"))

        for i, (doc, metadata, distance) in enumerate(
            zip(results['documents'], results['metadatas'], results['distances']),
            1
        ):
            similarity = 1 - distance if distance else 0  # Convert distance to similarity
            self.stdout.write(f"\n   Match {i} (Similarity: {similarity:.2%}):")
            self.stdout.write(f"      Type: {metadata.get('type', 'N/A')}")
            self.stdout.write(f"      Text: {doc[:150]}...")

    def _handle_init_clauses(self, chroma, mapper, contract_types):
        """Handle --init-clauses option"""
        self.stdout.write(
            self.style.HTTP_INFO(f"\n⬆️  INITIALIZING CLAUSES IN CHROMADB\n")
        )

        total_added = 0

        for contract_type_key in contract_types:
            # Parse contract type and jurisdiction
            parts = contract_type_key.rsplit('_', 1)
            if len(parts) == 2:
                contract_type, jurisdiction = parts
            else:
                contract_type = contract_type_key
                jurisdiction = 'INDIA'

            self.stdout.write(f"\nProcessing {contract_type_key}...")

            # Get all clauses for this type
            all_clauses = mapper.get_all_clauses_flat(contract_type, jurisdiction)

            if not all_clauses:
                self.stdout.write(f"  ⚠ No clauses found")
                continue

            # Prepare clauses for ChromaDB
            clauses_for_chroma = []
            for clause in all_clauses:
                clauses_for_chroma.append({
                    'type': clause.get('type', ''),
                    'text': clause.get('standard_text', clause.get('text', '')),
                    'jurisdiction': jurisdiction,
                    'contract_type': contract_type,
                    'recommendations': clause.get('recommendations', '')
                })

            try:
                chroma.add_standard_clauses(
                    collection_name=contract_type_key,
                    clauses=clauses_for_chroma
                )
                total_added += len(clauses_for_chroma)
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Added {len(clauses_for_chroma)} clauses")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Error: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Successfully added {total_added} clauses to ChromaDB")
        )

    def _handle_reset(self, chroma, mapper, contract_types):
        """Handle --reset option"""
        self.stdout.write(
            self.style.WARNING(f"\n🗑️  RESETTING CHROMADB\n")
        )

        if not self._confirm_action("Are you sure you want to delete all ChromaDB collections?"):
            self.stdout.write("Reset cancelled.")
            return

        deleted_count = 0
        for contract_type_key in contract_types:
            try:
                chroma.delete_collection(contract_type_key)
                self.stdout.write(f"  ✓ Deleted {contract_type_key}")
                deleted_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  ⚠ Error deleting {contract_type_key}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Deleted {deleted_count} collections")
        )

    def _confirm_action(self, prompt):
        """Ask user for confirmation"""
        while True:
            response = input(f"{prompt} (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                self.stdout.write("Please enter 'yes' or 'no'")
