import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from core.models import (
    GroupMembership,
    GroupMetadata,
    Product,
    ProductType,
    Profile,
    Release,
)
from core.saml2 import LineaSaml2Backend
from core.services.access_control import AccessControlService
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.test import TestCase, TransactionTestCase
from django.utils import timezone as django_timezone


class TestSAML2GroupManagementBase(TransactionTestCase):
    """
    Base class for SAML2/IDP group management tests.
    Uses TransactionTestCase to support nested transactions.
    """

    fixtures = [
        "core/fixtures/initial_data.yaml",
    ]

    def setUp(self):
        """Set up basic data for tests."""
        self.backend = LineaSaml2Backend()

        # Create test user
        self.test_user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass123"
        )
        # Create profile for user (or get if already exists)
        self.test_profile, _ = Profile.objects.get_or_create(user=self.test_user)

        # Get Admin group from fixtures
        self.admin_group = Group.objects.get(name="Admin")

        # Create local test groups
        self.local_group = Group.objects.create(name="LocalTestGroup")
        GroupMetadata.objects.create(
            group=self.local_group,
            source=GroupMetadata.GroupSource.LOCAL,
            display_name="Local Test Group",
            description="A local test group",
        )

        # Create test release with access control
        self.test_release = Release.objects.create(
            name="test_release",
            display_name="Test Release",
            description="A test release for access control",
            indexing_column="id",
        )

        # Create test product type
        self.test_product_type = ProductType.objects.create(
            name="test_type",
            display_name="Test Type",
            order=1,
            description="Test product type",
        )

    def tearDown(self):
        """Clean up data after each test."""
        # Clear many-to-many relationships
        for user in User.objects.all():
            user.groups.clear()

        # Clean up data created during tests
        GroupMembership.objects.all().delete()
        GroupMetadata.objects.exclude(group=self.admin_group).delete()
        Group.objects.exclude(name="Admin").delete()
        Release.objects.exclude(id__in=[1]).delete()  # Keep release from fixtures
        ProductType.objects.exclude(
            id__in=[1, 2, 3, 4, 5, 6, 7]
        ).delete()  # Keep from fixtures
        Product.objects.all().delete()
        Profile.objects.exclude(user=self.test_user).delete()
        User.objects.exclude(username="testuser").delete()

    def create_saml_attributes(
        self,
        uid="testuser",
        status="Active",
        groups=None,
        display_name="Test User",
        email="testuser@example.com",
    ):
        """
        Create simulated SAML attributes for tests.

        Args:
            uid: User ID
            status: User status (Active, Pending, etc.)
            groups: List of user groups
            display_name: Display name
            email: User email

        Returns:
            Dict with SAML attributes
        """
        if groups is None:
            groups = []

        return {
            "uid": [uid] if isinstance(uid, str) else uid,
            "schacUserStatus": [status] if isinstance(status, str) else status,
            "member": groups,
            "displayName": (
                [display_name] if isinstance(display_name, str) else display_name
            ),
            "email": [email] if isinstance(email, str) else email,
            "knowledgeInformation": "Test knowledge info",
        }

    def create_session_info(self, attributes):
        """
        Create simulated SAML session information.

        Args:
            attributes: Dictionary with SAML attributes

        Returns:
            Dict with session information
        """
        return {
            "ava": attributes,
            "issuer": "test_idp",
            "came_from": "/",
            "subject": "test_subject",
        }


class TestLineaSaml2Backend(TestSAML2GroupManagementBase):
    """Tests for the custom SAML2 backend."""

    def test_authenticate_with_no_session_info(self):
        """Test authentication without session information."""
        request = Mock()
        result = self.backend.authenticate(request, session_info=None)

        self.assertIsNone(result)

    def test_authenticate_with_pending_status(self):
        """Test authentication with pending status."""
        request = Mock()
        request.session = {}

        attributes = self.create_saml_attributes(status="Pending")
        session_info = self.create_session_info(attributes)

        result = self.backend.authenticate(request, session_info=session_info)

        self.assertIsNone(result)
        self.assertTrue(request.session.get("pending_approval"))

    def test_authenticate_with_inactive_status(self):
        """Test authentication with inactive status."""
        request = Mock()
        request.session = {}

        attributes = self.create_saml_attributes(status="Inactive")
        session_info = self.create_session_info(attributes)

        result = self.backend.authenticate(request, session_info=session_info)

        self.assertIsNone(result)

    def test_authenticate_without_uid(self):
        """Test authentication without UID."""
        request = Mock()
        request.session = {}

        attributes = self.create_saml_attributes(uid=None)
        del attributes["uid"]  # Remove UID completely
        session_info = self.create_session_info(attributes)

        result = self.backend.authenticate(request, session_info=session_info)

        self.assertIsNone(result)
        self.assertTrue(request.session.get("needs_registration"))

    def test_get_user_status_from_list(self):
        """Test status extraction when it's a list."""
        attributes = {"schacUserStatus": ["Active", "Other"]}
        status = self.backend._get_user_status(attributes)

        self.assertEqual(status, "Active")

    def test_get_user_status_from_string(self):
        """Test status extraction when it's a string."""
        attributes = {"schacUserStatus": "Pending"}
        status = self.backend._get_user_status(attributes)

        self.assertEqual(status, "Pending")

    def test_get_user_status_missing(self):
        """Test status extraction when it doesn't exist."""
        attributes = {}
        status = self.backend._get_user_status(attributes)

        self.assertEqual(status, "Unknown")

    def test_update_user_info(self):
        """Test basic user information update."""
        attributes = self.create_saml_attributes(
            display_name="João Silva Santos", email="joao.santos@example.com"
        )

        self.backend._update_user_info(self.test_user, attributes)

        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.first_name, "João")
        self.assertEqual(self.test_user.last_name, "Silva Santos")
        self.assertEqual(self.test_user.email, "joao.santos@example.com")

        # Verify profile was updated
        self.test_profile.refresh_from_db()
        self.assertEqual(self.test_profile.display_name, "João Silva Santos")


class TestLineaGroupSynchronization(TestSAML2GroupManagementBase):
    """Tests for LIneA group synchronization."""

    def test_sync_linea_groups_create_new_group(self):
        """Test creation of new LIneA group."""
        attributes = self.create_saml_attributes(groups=["LinEA_TestGroup1"])

        self.backend._sync_linea_groups(self.test_user, attributes)

        # Verify group was created
        group = Group.objects.get(name="LinEA_TestGroup1")
        self.assertTrue(self.test_user.groups.filter(id=group.id).exists())

        # Verify metadata
        metadata = group.metadata
        self.assertEqual(metadata.source, GroupMetadata.GroupSource.LINEA)
        self.assertEqual(metadata.display_name, "Linea_Testgroup1")
        self.assertIsNotNone(metadata.last_sync)

        # Verify membership tracking
        membership = GroupMembership.objects.get(user=self.test_user, group=group)
        self.assertIsNotNone(membership)

    def test_sync_linea_groups_multiple_groups(self):
        """Test synchronization with multiple groups."""
        groups = ["LinEA_Group1", "LinEA_Group2", "LinEA_Group3"]
        attributes = self.create_saml_attributes(groups=groups)

        self.backend._sync_linea_groups(self.test_user, attributes)

        # Verify all groups were created
        for group_name in groups:
            group = Group.objects.get(name=group_name)
            self.assertTrue(self.test_user.groups.filter(id=group.id).exists())
            self.assertTrue(group.metadata.is_linea_group)

    def test_sync_linea_groups_convert_local_to_linea(self):
        """Test conversion of local group to LIneA."""
        # Create local group with same name that will come from IDP
        existing_group = Group.objects.create(name="ConvertGroup")
        local_metadata = GroupMetadata.objects.create(
            group=existing_group,
            source=GroupMetadata.GroupSource.LOCAL,
            display_name="Local Convert Group",
        )

        attributes = self.create_saml_attributes(groups=["ConvertGroup"])

        with self.assertLogs("saml", level="WARNING") as cm:
            self.backend._sync_linea_groups(self.test_user, attributes)

        # Verify it was converted to LIneA
        local_metadata.refresh_from_db()
        self.assertEqual(local_metadata.source, GroupMetadata.GroupSource.LINEA)

        # Verify warning log was emitted
        self.assertTrue(any("converting to LIneA" in message for message in cm.output))

    def test_sync_linea_groups_existing_group_sync_update(self):
        """Test sync timestamp update for existing LIneA group."""
        # Create existing LIneA group
        existing_group = Group.objects.create(name="ExistingGroup")
        metadata = GroupMetadata.objects.create(
            group=existing_group, source=GroupMetadata.GroupSource.LINEA
        )
        old_sync_time = metadata.last_sync

        attributes = self.create_saml_attributes(groups=["ExistingGroup"])

        self.backend._sync_linea_groups(self.test_user, attributes)

        # Verify sync timestamp was updated
        metadata.refresh_from_db()
        self.assertNotEqual(metadata.last_sync, old_sync_time)

    def test_sync_linea_groups_existing_membership(self):
        """Test handling of existing membership."""
        # Create group and existing membership
        group = Group.objects.create(name="TestExistingGroup")
        GroupMetadata.objects.create(
            group=group, source=GroupMetadata.GroupSource.LINEA
        )
        existing_membership = GroupMembership.objects.create(
            user=self.test_user, group=group
        )

        attributes = self.create_saml_attributes(groups=["TestExistingGroup"])

        self.backend._sync_linea_groups(self.test_user, attributes)

        # Verify membership still exists
        existing_membership.refresh_from_db()
        self.assertIsNotNone(existing_membership)

    def test_sync_linea_groups_ignore_empty_groups(self):
        """Testa que grupos vazios ou None são ignorados."""
        attributes = self.create_saml_attributes(groups=["ValidGroup", "", None, "   "])

        self.backend._sync_linea_groups(self.test_user, attributes)

        # Apenas o grupo válido deve ter sido criado
        created_groups = Group.objects.filter(name__in=["ValidGroup", "", "   "])
        self.assertEqual(created_groups.count(), 1)
        self.assertEqual(created_groups.first().name, "ValidGroup")

    def test_sync_linea_groups_no_groups_in_attributes(self):
        """Testa sincronização quando não há grupos nos atributos."""
        attributes = self.create_saml_attributes(groups=[])

        initial_group_count = Group.objects.count()

        self.backend._sync_linea_groups(self.test_user, attributes)

        # Nenhum grupo novo deve ter sido criado
        final_group_count = Group.objects.count()
        self.assertEqual(initial_group_count, final_group_count)


class TestLineaGroupDeletion(TestSAML2GroupManagementBase):
    """Tests for LIneA group membership deletion."""

    def setUp(self):
        super().setUp()

        # Create LIneA test groups
        self.linea_group1 = Group.objects.create(name="LinEA_Group1")
        GroupMetadata.objects.create(
            group=self.linea_group1, source=GroupMetadata.GroupSource.LINEA
        )

        self.linea_group2 = Group.objects.create(name="LinEA_Group2")
        GroupMetadata.objects.create(
            group=self.linea_group2, source=GroupMetadata.GroupSource.LINEA
        )

        # Add user to groups
        self.test_user.groups.add(self.linea_group1, self.linea_group2)

        # Create memberships
        GroupMembership.objects.create(user=self.test_user, group=self.linea_group1)
        GroupMembership.objects.create(user=self.test_user, group=self.linea_group2)

    def test_remove_missing_linea_groups(self):
        """Test removal of LIneA groups that are no longer present."""
        # User remains only in LinEA_Group1
        current_groups = [self.linea_group1]

        with self.assertLogs("saml", level="DEBUG") as cm:
            self.backend._remove_missing_linea_groups(self.test_user, current_groups)

        # Verify membership2 was deleted
        with self.assertRaises(GroupMembership.DoesNotExist):
            GroupMembership.objects.get(user=self.test_user, group=self.linea_group2)

        # Verify user was removed from Django group
        self.assertFalse(self.test_user.groups.filter(id=self.linea_group2.id).exists())

        # Verify Group1 membership still exists
        membership1 = GroupMembership.objects.get(
            user=self.test_user, group=self.linea_group1
        )
        self.assertIsNotNone(membership1)
        self.assertTrue(self.test_user.groups.filter(id=self.linea_group1.id).exists())

    def test_remove_group_memberships_when_no_groups(self):
        """Testa remoção de memberships quando usuário não tem mais grupos no IdP."""
        # Remove usuário de ambos os grupos
        current_groups = []

        with self.assertLogs("saml", level="DEBUG") as cm:
            self.backend._remove_missing_linea_groups(
                self.test_user, current_groups
            )

        # Verifica se os memberships foram removidos
        self.assertEqual(
            GroupMembership.objects.filter(user=self.test_user).count(), 0
        )

        # Verifica logs de remoção
        self.assertTrue(any("removed" in message for message in cm.output))

    def test_deactivate_preserve_group_with_other_active_members(self):
        """Testa que grupo com outros membros ativos não é desativado."""
        # Criar outro usuário no mesmo grupo
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com"
        )
        Profile.objects.get_or_create(user=other_user)
        GroupMembership.objects.create(
            user=other_user, group=self.linea_group1
        )

        # Remove test_user do grupo, mas other_user permanece
        current_groups = []

        self.backend._remove_missing_linea_groups(self.test_user, current_groups)

        # Como o campo is_active foi removido, verificamos apenas se o grupo ainda existe
        self.linea_group1.metadata.refresh_from_db()
        self.assertTrue(GroupMetadata.objects.filter(group=self.linea_group1).exists())

        # Group2 ainda deve existir pois os grupos não são mais automaticamente desativados
        self.linea_group2.metadata.refresh_from_db()
        self.assertTrue(GroupMetadata.objects.filter(group=self.linea_group2).exists())

    def test_remove_handles_group_without_metadata(self):
        """Testa tratamento de grupo sem metadata LIneA."""
        # Criar grupo sem metadata LIneA
        problematic_group = Group.objects.create(name="ProblematicGroup")
        GroupMembership.objects.create(
            user=self.test_user, group=problematic_group
        )

        current_groups = []

        with self.assertLogs("saml", level="WARNING") as cm:
            self.backend._remove_missing_linea_groups(
                self.test_user, current_groups
            )

        # Verifica se foi emitido warning sobre grupo sem metadata
        self.assertTrue(
            any(
                "doesn't have correct LIneA metadata" in message
                for message in cm.output
            )
        )


class TestAccessControlService(TestSAML2GroupManagementBase):
    """Testes para o serviço de controle de acesso."""

    def setUp(self):
        super().setUp()

        # Criar grupos para testes de acesso
        self.access_group1 = Group.objects.create(name="AccessGroup1")
        GroupMetadata.objects.create(
            group=self.access_group1,
            source=GroupMetadata.GroupSource.LINEA,
        )

        self.access_group2 = Group.objects.create(name="AccessGroup2")
        GroupMetadata.objects.create(
            group=self.access_group2,
            source=GroupMetadata.GroupSource.LINEA,
        )

        self.inactive_group = Group.objects.create(name="InactiveGroup")
        GroupMetadata.objects.create(
            group=self.inactive_group,
            source=GroupMetadata.GroupSource.LINEA,
        )

    def test_get_user_groups_all_groups(self):
        """Testa obtenção de todos os grupos do usuário (is_active removido)."""
        # Adicionar usuário aos grupos
        self.test_user.groups.add(
            self.access_group1, self.access_group2, self.inactive_group
        )

        user_groups = AccessControlService.get_user_groups(
            self.test_user
        )
        group_names = [g.name for g in user_groups]

        # Como is_active foi removido, todos os grupos são retornados
        self.assertIn("AccessGroup1", group_names)
        self.assertIn("AccessGroup2", group_names)
        self.assertIn("InactiveGroup", group_names)

    def test_get_user_groups_consistency(self):
        """Testa consistência na obtenção de grupos (teste redundante agora)."""
        self.test_user.groups.add(
            self.access_group1, self.access_group2, self.inactive_group
        )

        user_groups = AccessControlService.get_user_groups(
            self.test_user
        )
        group_names = [g.name for g in user_groups]

        # Como is_active foi removido, todos os grupos são sempre retornados
        self.assertEqual(len(group_names), 3)
        self.assertIn("AccessGroup1", group_names)
        self.assertIn("AccessGroup2", group_names)
        self.assertIn("InactiveGroup", group_names)

    def test_get_user_groups_without_metadata(self):
        """Testa grupos sem metadata (considerados ativos)."""
        group_without_metadata = Group.objects.create(name="NoMetadataGroup")
        self.test_user.groups.add(group_without_metadata)

        active_groups = AccessControlService.get_user_groups(self.test_user)
        group_names = [g.name for g in active_groups]

        self.assertIn("NoMetadataGroup", group_names)

    @patch("core.services.access_control.log")
    def test_filter_accessible_releases_admin_user(self, mock_log):
        """Testa filtragem de releases para usuário admin."""
        # Adicionar usuário ao grupo Admin
        self.test_user.groups.add(self.admin_group)

        # Criar releases de teste
        restricted_release = Release.objects.create(
            name="restricted",
            display_name="Restricted Release",
            description="A restricted release",
            indexing_column="id",
        )

        accessible_releases = AccessControlService.filter_accessible_releases(
            self.test_user
        )

        # Admin deve ter acesso a todas as releases
        self.assertIn(self.test_release, accessible_releases)
        self.assertIn(restricted_release, accessible_releases)

    @patch("core.services.access_control.log")
    def test_filter_accessible_releases_public_releases(self, mock_log):
        """Testa acesso a releases públicas."""
        # Usuário não é admin (não está no grupo Admin)

        # Criar release pública
        public_release = Release.objects.create(
            name="public",
            display_name="Public Release",
            description="A public release",
            indexing_column="id",
            is_public=True,
        )

        accessible_releases = AccessControlService.filter_accessible_releases(
            self.test_user
        )

        # Usuário deve ter acesso à release pública
        self.assertIn(public_release, accessible_releases)

    @patch("core.services.access_control.log")
    def test_filter_accessible_releases_by_group(self, mock_log):
        """Testa filtragem de releases por grupo do usuário."""
        # Usuário não é admin (não está no grupo Admin)

        # Adicionar usuário ao grupo
        self.test_user.groups.add(self.access_group1)

        # Criar release com controle de acesso por grupo
        restricted_release = Release.objects.create(
            name="group_restricted",
            display_name="Group Restricted Release",
            description="A group restricted release",
            indexing_column="id",
            is_public=False,
        )
        restricted_release.access_groups.add(self.access_group1)

        accessible_releases = AccessControlService.filter_accessible_releases(
            self.test_user
        )

        # Usuário deve ter acesso devido ao grupo
        self.assertIn(restricted_release, accessible_releases)

    def test_add_user_to_group_success(self):
        """Testa adição bem-sucedida de usuário ao grupo."""
        result = AccessControlService.add_user_to_group(
            self.test_user, self.access_group1
        )

        self.assertTrue(result)
        self.assertTrue(self.test_user.groups.filter(id=self.access_group1.id).exists())

    def test_add_user_to_group_already_member(self):
        """Testa adição de usuário já presente no grupo."""
        self.test_user.groups.add(self.access_group1)

        result = AccessControlService.add_user_to_group(
            self.test_user, self.access_group1
        )

        self.assertTrue(result)  # Ainda deve retornar True

    def test_remove_user_from_linea_group_without_force(self):
        """Testa remoção de usuário de grupo LIneA sem force."""
        self.test_user.groups.add(self.access_group1)

        result = AccessControlService.remove_user_from_group(
            self.test_user, self.access_group1
        )

        self.assertFalse(result)  # Deve falhar
        self.assertTrue(self.test_user.groups.filter(id=self.access_group1.id).exists())

    def test_remove_user_from_linea_group_with_force(self):
        """Testa remoção forçada de usuário de grupo LIneA."""
        self.test_user.groups.add(self.access_group1)

        result = AccessControlService.remove_user_from_group(
            self.test_user, self.access_group1, force=True
        )

        self.assertTrue(result)
        self.assertFalse(
            self.test_user.groups.filter(id=self.access_group1.id).exists()
        )

    def test_remove_user_from_local_group(self):
        """Testa remoção de usuário de grupo local."""
        self.test_user.groups.add(self.local_group)

        result = AccessControlService.remove_user_from_group(
            self.test_user, self.local_group
        )

        self.assertTrue(result)
        self.assertFalse(self.test_user.groups.filter(id=self.local_group.id).exists())

    def test_get_group_members_active_group(self):
        """Testa obtenção de membros de grupo ativo."""
        self.access_group1.user_set.add(self.test_user)

        members = AccessControlService.get_group_members(self.access_group1)

        self.assertIn(self.test_user, members)

    def test_get_group_members_all_groups(self):
        """Testa obtenção de membros de qualquer grupo (is_active removido)."""
        self.inactive_group.user_set.add(self.test_user)

        # Como o campo is_active foi removido, todos os membros são retornados
        members = AccessControlService.get_group_members(
            self.inactive_group
        )
        self.assertIn(self.test_user, members)


class TestSAML2IntegrationScenarios(TestSAML2GroupManagementBase):
    """Testes de cenários de integração completos."""

    def test_complete_user_login_flow(self):
        """Testa fluxo completo de login de usuário via SAML2."""
        request = Mock()
        request.session = {}

        # Simular atributos SAML com grupos
        attributes = self.create_saml_attributes(
            uid="newuser",
            status="Active",
            groups=["LinEA_Scientists", "LinEA_DataAnalysts"],
            display_name="Dr. João Silva",
            email="joao.silva@linea.gov.br",
        )
        session_info = self.create_session_info(attributes)

        # Mock do método pai authenticate
        with patch("djangosaml2.backends.Saml2Backend.authenticate") as mock_super_auth:
            # Criar usuário que seria retornado pelo método pai
            new_user = User.objects.create_user(
                username="newuser", email="joao.silva@linea.gov.br"
            )
            Profile.objects.get_or_create(user=new_user)
            mock_super_auth.return_value = new_user

            # Mock do método _update_user que é chamado pelo pai
            with patch.object(
                self.backend, "_update_user", return_value=None
            ) as mock_update:
                # Executar autenticação
                result = self.backend.authenticate(request, session_info=session_info)

                # Verificar se usuário foi autenticado
                self.assertEqual(result, new_user)

                # Simular sincronização de grupos manualmente (já que mockamos _update_user)
                self.backend._sync_linea_groups(new_user, attributes)

                # Verificar se grupos foram criados
                scientists_group = Group.objects.get(name="LinEA_Scientists")
                analysts_group = Group.objects.get(name="LinEA_DataAnalysts")

                # Verificar se usuário foi adicionado aos grupos
                self.assertTrue(new_user.groups.filter(id=scientists_group.id).exists())
                self.assertTrue(new_user.groups.filter(id=analysts_group.id).exists())

                # Verificar metadatas
                self.assertTrue(scientists_group.metadata.is_linea_group)
                self.assertTrue(analysts_group.metadata.is_linea_group)

                # Verificar memberships
                self.assertTrue(
                    GroupMembership.objects.filter(
                        user=new_user, group=scientists_group
                    ).exists()
                )

    def test_user_group_changes_between_logins(self):
        """Testa mudanças de grupos entre logins."""
        # Primeiro login com grupos iniciais
        initial_groups = ["LinEA_Group1", "LinEA_Group2", "LinEA_Group3"]
        attributes1 = self.create_saml_attributes(groups=initial_groups)

        self.backend._sync_linea_groups(self.test_user, attributes1)

        # Verificar grupos iniciais
        self.assertEqual(self.test_user.groups.count(), len(initial_groups))

        # Segundo login com grupos modificados (removido Group2, adicionado Group4)
        updated_groups = ["LinEA_Group1", "LinEA_Group3", "LinEA_Group4"]
        attributes2 = self.create_saml_attributes(groups=updated_groups)

        self.backend._sync_linea_groups(self.test_user, attributes2)

        # Verificar se Group4 foi adicionado
        self.assertTrue(self.test_user.groups.filter(name="LinEA_Group4").exists())

        # Verificar se Group2 foi removido do usuário
        self.assertFalse(self.test_user.groups.filter(name="LinEA_Group2").exists())

        # Verificar se membership do Group2 foi removido (nova lógica)
        group2 = Group.objects.get(name="LinEA_Group2")
        # Com a nova lógica, quando um grupo não está mais presente no IdP,
        # o membership é completamente removido
        self.assertFalse(GroupMembership.objects.filter(user=self.test_user, group=group2).exists())

    def test_multiple_users_same_groups(self):
        """Testa múltiplos usuários nos mesmos grupos."""
        # Criar usuários adicionais
        user2 = User.objects.create_user("user2", "user2@example.com")
        user3 = User.objects.create_user("user3", "user3@example.com")
        Profile.objects.get_or_create(user=user2)
        Profile.objects.get_or_create(user=user3)

        # Adicionar todos aos mesmos grupos
        shared_groups = ["LinEA_SharedGroup1", "LinEA_SharedGroup2"]
        attributes = self.create_saml_attributes(groups=shared_groups)

        for user in [self.test_user, user2, user3]:
            self.backend._sync_linea_groups(user, attributes)

        # Verificar se todos estão nos grupos
        for group_name in shared_groups:
            group = Group.objects.get(name=group_name)
            for user in [self.test_user, user2, user3]:
                self.assertTrue(user.groups.filter(id=group.id).exists())

        # Primeiro, verificar se todos estão nos grupos
        for group_name in shared_groups:
            group = Group.objects.get(name=group_name)
            for user in [self.test_user, user2, user3]:
                self.assertTrue(user.groups.filter(id=group.id).exists())

        # Simular que IDP não retorna mais grupos para user2 (lista vazia)
        # Isso deve resultar na remoção do user2 dos grupos
        current_groups = []  # user2 não tem mais grupos no IDP
        self.backend._remove_missing_linea_groups(user2, current_groups)

        # Verificar que user2 foi removido mas os outros permaneceram
        for group_name in shared_groups:
            group = Group.objects.get(name=group_name)
            self.assertFalse(user2.groups.filter(id=group.id).exists())
            self.assertTrue(self.test_user.groups.filter(id=group.id).exists())
            self.assertTrue(user3.groups.filter(id=group.id).exists())

            # Grupo deve permanecer existindo (is_active foi removido)
            self.assertTrue(GroupMetadata.objects.filter(group=group).exists())

    def test_error_handling_during_sync(self):
        """Testa tratamento de erros durante sincronização."""
        attributes = self.create_saml_attributes(groups=["LinEA_TestGroup"])

        # Mock para simular erro durante criação do grupo
        with patch("core.models.GroupMetadata.objects.get_or_create") as mock_create:
            mock_create.side_effect = Exception("Database error")

            with self.assertLogs("saml", level="ERROR") as cm:
                self.backend._sync_linea_groups(self.test_user, attributes)

            # Verificar se erro foi logado
            self.assertTrue(
                any("Error synchronizing" in message for message in cm.output)
            )


class TestSAML2DataCleanup(TestSAML2GroupManagementBase):
    """Testes específicos para limpeza de dados após execução."""

    def test_cleanup_after_group_creation(self):
        """Testa que grupos criados durante teste são limpos."""
        initial_group_count = Group.objects.count()

        # Criar grupos durante o teste
        attributes = self.create_saml_attributes(groups=["TempGroup1", "TempGroup2"])
        self.backend._sync_linea_groups(self.test_user, attributes)

        # Verificar que grupos foram criados
        self.assertTrue(Group.objects.filter(name="TempGroup1").exists())
        self.assertTrue(Group.objects.filter(name="TempGroup2").exists())

        # tearDown é chamado automaticamente
        self.tearDown()

        # Verificar que apenas grupos das fixtures permanecem
        remaining_groups = Group.objects.all()
        self.assertEqual(remaining_groups.count(), 1)  # Apenas Admin
        self.assertEqual(remaining_groups.first().name, "Admin")

    def test_cleanup_memberships_and_metadata(self):
        """Testa limpeza de memberships e metadatas."""
        attributes = self.create_saml_attributes(groups=["CleanupTestGroup"])
        self.backend._sync_linea_groups(self.test_user, attributes)

        # Verificar que dados foram criados
        self.assertTrue(GroupMembership.objects.exists())
        self.assertTrue(
            GroupMetadata.objects.filter(
                source=GroupMetadata.GroupSource.LINEA
            ).exists()
        )

        # tearDown é chamado automaticamente
        self.tearDown()

        # Verificar limpeza
        linea_metadata = GroupMetadata.objects.filter(
            source=GroupMetadata.GroupSource.LINEA
        )
        self.assertEqual(linea_metadata.count(), 0)
        self.assertEqual(GroupMembership.objects.count(), 0)

    def test_isolation_between_tests(self):
        """Testa isolamento entre diferentes testes."""
        # Este teste verifica que dados de testes anteriores não interferem

        # Verificar estado limpo inicial
        self.assertEqual(Group.objects.count(), 2)  # Admin + local_group
        self.assertEqual(GroupMembership.objects.count(), 0)

        # Criar dados
        attributes = self.create_saml_attributes(groups=["IsolationTestGroup"])
        self.backend._sync_linea_groups(self.test_user, attributes)

        # Verificar que dados existem
        self.assertTrue(Group.objects.filter(name="IsolationTestGroup").exists())

        # tearDown será chamado e dados serão limpos para o próximo teste


# Classe utilitária para testes de performance (opcional)
class TestSAML2Performance(TestSAML2GroupManagementBase):
    """Testes de performance para operações SAML2."""

    def test_sync_many_groups_performance(self):
        """Testa performance com muitos grupos."""
        import time

        # Criar lista com muitos grupos
        many_groups = [f"LinEA_PerfGroup{i}" for i in range(100)]
        attributes = self.create_saml_attributes(groups=many_groups)

        start_time = time.time()
        self.backend._sync_linea_groups(self.test_user, attributes)
        end_time = time.time()

        # Verificar que operação foi concluída em tempo razoável (menos de 5 segundos)
        execution_time = end_time - start_time
        self.assertLess(
            execution_time, 5.0, f"Sync took {execution_time:.2f}s, too slow!"
        )

        # Verificar que todos os grupos foram criados
        created_groups = Group.objects.filter(name__startswith="LinEA_PerfGroup")
        self.assertEqual(created_groups.count(), 100)
