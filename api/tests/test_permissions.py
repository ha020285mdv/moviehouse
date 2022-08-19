from django.test import RequestFactory, TestCase

from api.API.permissions import IsAdminOrReadOnly, IsAdminOrCreateOnly, IsAdminOrCreateOnlyForUsers, \
    IsAdminOrCreateOnlyOrReadOwnForOrder
from cinema.tests.factories import SuperUserFactory, UserFactory


class IsAdminOrReadOnlyTest(TestCase):
    def setUp(self):
        self.admin_user = SuperUserFactory()
        self.user = UserFactory()
        self.factory = RequestFactory()
        self.permission_check = IsAdminOrReadOnly()

    def test_admin_user_returns_true(self):
        request = self.factory.post('/')
        request.user = self.admin_user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_admin_user_returns_true_on_safe(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_no_admin_user_returns_false(self):
        request = self.factory.post('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertFalse(permission)

    def test_no_admin_user_returns_true_on_safe(self):
        request = self.factory.get('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)


class IsAdminOrCreateOnlyTest(TestCase):
    def setUp(self):
        self.admin_user = SuperUserFactory()
        self.user = UserFactory()
        self.factory = RequestFactory()
        self.permission_check = IsAdminOrCreateOnly()

    def test_admin_user_returns_true(self):
        request = self.factory.post('/')
        request.user = self.admin_user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_admin_user_returns_true_on_delete(self):
        request = self.factory.delete('/')
        request.user = self.admin_user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_no_admin_user_returns_false_on_delete(self):
        request = self.factory.delete('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertFalse(permission)

    def test_no_admin_user_returns_false_on_put(self):
        request = self.factory.put('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertFalse(permission)

    def test_no_admin_user_returns_true_on_create(self):
        request = self.factory.post('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)


class IsAdminOrCreateOnlyOrReadOwnForOrderTest(TestCase):
    def setUp(self):
        self.admin_user = SuperUserFactory()
        self.user = UserFactory()
        self.factory = RequestFactory()
        self.permission_check = IsAdminOrCreateOnlyOrReadOwnForOrder()

    def test_admin_user_returns_true(self):
        request = self.factory.post('/')
        request.user = self.admin_user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_admin_user_returns_true_on_delete(self):
        request = self.factory.delete('/')
        request.user = self.admin_user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_no_admin_user_returns_false_on_delete(self):
        request = self.factory.delete('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertFalse(permission)

    def test_no_admin_user_returns_false_on_put(self):
        request = self.factory.put('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertFalse(permission)

    def test_no_admin_user_returns_true_on_create(self):
        request = self.factory.post('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)


class IsAdminOrCreateOnlyForUsersTest(TestCase):
    def setUp(self):
        self.admin_user = SuperUserFactory()
        self.user = UserFactory()
        self.factory = RequestFactory()
        self.permission_check = IsAdminOrCreateOnlyForUsers()

    def test_admin_user_returns_true(self):
        request = self.factory.post('/')
        request.user = self.admin_user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_admin_user_returns_true_on_delete(self):
        request = self.factory.delete('/')
        request.user = self.admin_user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_no_admin_user_returns_true_on_delete(self):
        request = self.factory.delete('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_no_admin_user_returns_true_on_create(self):
        request = self.factory.post('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)

    def test_no_admin_user_returns_true_on_get(self):
        request = self.factory.get('/')
        request.user = self.user
        permission = self.permission_check.has_permission(request, None)
        self.assertTrue(permission)
