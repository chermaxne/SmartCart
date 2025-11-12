from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create default admin users'
    
    def handle(self, *args, **kwargs):
        # Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@auroramart.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('✓ Superuser created'))
        
        # Staff user
        if not User.objects.filter(username='staff').exists():
            user = User.objects.create_user(
                username='staff',
                email='staff@auroramart.com',
                password='staff123',
                first_name='Staff',
                last_name='Member'
            )
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS('✓ Staff user created'))
        
        self.stdout.write('\n=== Login Credentials ===')
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Staff: staff / staff123')