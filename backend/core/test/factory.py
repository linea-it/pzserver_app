# from django.test import TestCase

# # Create your tests here.
# from faker import Faker as FakerClass
# from typing import Any, Sequence
# from factory import django, Faker, post_generation

# from django.contrib.auth.models import User

# from core.models import Release


# class ReleaseFactory(django.DjangoModelFactory):
#     class Meta:
#         model = Release

#     name = Faker("name")
#     display_name = Faker("name")
#     description = Faker("sentence")


# class UserFactory(django.DjangoModelFactory):
#     class Meta:
#         model = User

#     username = Faker("user_name")
#     @post_generation
#     def password(self, create: bool, extracted: Sequence[Any], **kwargs):
#         password = (
#             extracted
#             if extracted
#             else FakerClass().password(
#                 length=30,
#                 special_chars=True,
#                 digits=True,
#                 upper_case=True,
#                 lower_case=True,
#             )
#         )
#         self.set_password(password)
