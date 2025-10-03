#!/usr/bin/env python3
"""
Initialize notification templates in the database.

This script creates the default notification templates for the Farmers Marketplace.
Run this after creating the notification tables via Alembic migration.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import get_settings
from app.models.shared.notification import NotificationTemplate
from app.services.notification_templates import NotificationTemplates


async def init_templates():
    """Initialize notification templates in the database."""
    print("🚀 Initializing notification templates...")
    
    # Create database engine and session
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        try:
            # Get all default templates
            templates_data = NotificationTemplates.get_default_templates()
            
            created_count = 0
            updated_count = 0
            
            for template_data in templates_data:
                # Check if template already exists
                result = await db.execute(
                    select(NotificationTemplate)
                    .where(NotificationTemplate.name == template_data["name"])
                )
                existing_template = result.scalar_one_or_none()
                
                if existing_template:
                    # Update existing template
                    for key, value in template_data.items():
                        if key != "name":  # Don't update the name
                            setattr(existing_template, key, value)
                    updated_count += 1
                    print(f"  ✅ Updated template: {template_data['name']}")
                else:
                    # Create new template
                    template = NotificationTemplate(**template_data)
                    db.add(template)
                    created_count += 1
                    print(f"  ✨ Created template: {template_data['name']}")
            
            # Commit all changes
            await db.commit()
            
            print(f"\n🎉 Template initialization complete!")
            print(f"   📝 Created: {created_count} templates")
            print(f"   🔄 Updated: {updated_count} templates")
            print(f"   📊 Total: {len(templates_data)} templates")
            
            # List all templates by category
            print(f"\n📋 Templates by category:")
            categories = {}
            for template_data in templates_data:
                category = template_data["category"]
                if category not in categories:
                    categories[category] = []
                categories[category].append(template_data["name"])
            
            for category, template_names in categories.items():
                print(f"   {category.upper()}: {len(template_names)} templates")
                for name in template_names:
                    print(f"     - {name}")
            
        except Exception as e:
            print(f"❌ Error initializing templates: {str(e)}")
            await db.rollback()
            raise
        finally:
            await engine.dispose()


async def main():
    """Main function."""
    print("🌾 Farmers Marketplace - Notification Template Initializer")
    print("=" * 60)
    
    try:
        await init_templates()
        print("\n✅ All done! Notification templates are ready to use.")
        
    except Exception as e:
        print(f"\n❌ Failed to initialize templates: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
