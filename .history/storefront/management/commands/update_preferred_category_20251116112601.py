from django.core.management.base import BaseCommand
from storefront.models import Customer, Category

class Command(BaseCommand):
    help = 'Update a user\'s preferred category'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the customer')
        parser.add_argument('category', type=str, help='Category name or ID')

    def handle(self, *args, **options):
        username = options['username']
        category_input = options['category']
        
        try:
            customer = Customer.objects.get(username=username)
            
            # Try to find category by ID first, then by name
            try:
                category_id = int(category_input)
                category = Category.objects.get(id=category_id)
            except ValueError:
                # Not an ID, try to find by name
                category = Category.objects.get(name__iexact=category_input)
            
            # Update customer's preferred category
            old_category = customer.preferred_category.name if customer.preferred_category else "None"
            customer.preferred_category = category
            customer.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {username}\'s preferred category from "{old_category}" to "{category.name}"'
                )
            )
            
        except Customer.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Customer "{username}" not found')
            )
        except Category.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Category "{category_input}" not found')
            )
            self.stdout.write(self.style.WARNING('Available categories:'))
            for cat in Category.objects.all():
                self.stdout.write(f'  {cat.id}: {cat.name}')
