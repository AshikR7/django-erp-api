from django.core.management.base import BaseCommand
from api.models import Role


class Command(BaseCommand):
    help = 'Create default roles for the ERP system'

    def handle(self, *args, **options):
        roles_data = [
            {'name': 'admin', 'description': 'System administrator with full access'},
            {'name': 'manager', 'description': 'Department manager with team access'},
            {'name': 'employee', 'description': 'Regular employee with limited access'},
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Role already exists: {role.name}')
                )