# encoding: utf-8
# pylint: disable=invalid-name,missing-docstring
from mock import Mock
import pytest

from werkzeug.exceptions import HTTPException

from app.modules.users import permissions


def test_DenyAbortMixin():
    with pytest.raises(HTTPException):
        permissions.DenyAbortMixin().deny()

def test_WriteAccessRule_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_readonly = False
    assert permissions.WriteAccessRule().check() is True
    authenticated_user_instance.is_readonly = True
    assert permissions.WriteAccessRule().check() is False

def test_ActivatedUserRoleRule_anonymous(anonymous_user_instance):
    # pylint: disable=unused-argument
    assert permissions.ActivatedUserRoleRule().check() is False

def test_ActivatedUserRoleRule_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_active = True
    assert permissions.ActivatedUserRoleRule().check() is True
    authenticated_user_instance.is_active = False
    assert permissions.ActivatedUserRoleRule().check() is False

def test_PasswordRequiredRule(authenticated_user_instance):
    authenticated_user_instance.password = "correct_password"
    assert permissions.PasswordRequiredRule(password="correct_password").check() is True
    assert permissions.PasswordRequiredRule(password="wrong_password").check() is False

def test_AdminRoleRule_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_admin = True
    assert permissions.AdminRoleRule().check() is True
    authenticated_user_instance.is_admin = False
    assert permissions.AdminRoleRule().check() is False

def test_SupervisorRoleRule_authenticated_user(authenticated_user_instance):
    obj = Mock()
    del obj.check_supervisor
    assert permissions.SupervisorRoleRule(obj).check() is False
    obj.check_supervisor = lambda user: user == authenticated_user_instance
    assert permissions.SupervisorRoleRule(obj).check() is True
    obj.check_supervisor = lambda user: False
    assert permissions.SupervisorRoleRule(obj).check() is False

def test_OwnerRoleRule_authenticated_user(authenticated_user_instance):
    obj = Mock()
    del obj.check_owner
    assert permissions.OwnerRoleRule(obj).check() is False
    obj.check_owner = lambda user: user == authenticated_user_instance
    assert permissions.OwnerRoleRule(obj).check() is True
    obj.check_owner = lambda user: False
    assert permissions.OwnerRoleRule(obj).check() is False

def test_PartialPermissionDeniedRule():
    with pytest.raises(RuntimeError):
        permissions.PartialPermissionDeniedRule().check()

def test_PasswordRequiredPermissionMixin():
    mixin = permissions.PasswordRequiredPermissionMixin(
        password_required=False
    )
    with pytest.raises(AttributeError):
        mixin.rule()

def test_WriteAccessPermission_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_readonly = False
    with permissions.WriteAccessPermission():
        pass
    authenticated_user_instance.is_readonly = True
    with pytest.raises(HTTPException):
        with permissions.WriteAccessPermission():
            pass

def test_RolePermission():
    with permissions.RolePermission():
        pass
    with pytest.raises(RuntimeError):
        with permissions.RolePermission(partial=True):
            pass

def test_ActivatedUserRolePermission_anonymous_user(anonymous_user_instance):
    # pylint: disable=unused-argument
    with pytest.raises(HTTPException):
        with permissions.ActivatedUserRolePermission():
            pass

def test_ActivatedUserRolePermission_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_active = True
    with permissions.ActivatedUserRolePermission():
        pass
    authenticated_user_instance.is_active = False
    with pytest.raises(HTTPException):
        with permissions.ActivatedUserRolePermission():
            pass

def test_AdminRolePermission_anonymous_user(anonymous_user_instance):
    # pylint: disable=unused-argument
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission():
            pass

def test_AdminRolePermission_authenticated_user(authenticated_user_instance):
    authenticated_user_instance.is_admin = True
    with permissions.AdminRolePermission():
        pass
    authenticated_user_instance.is_admin = False
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission():
            pass

def test_AdminRolePermission_anonymous_user_with_password(anonymous_user_instance):
    # pylint: disable=unused-argument
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission(password_required=True, password="any_password"):
            pass

def test_AdminRolePermission_authenticated_user_with_password_is_admin(
        authenticated_user_instance
):
    authenticated_user_instance.password = "correct_password"
    authenticated_user_instance.is_admin = True
    with permissions.AdminRolePermission(password_required=True, password="correct_password"):
        pass
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission(password_required=True, password="wrong_password"):
            pass

def test_AdminRolePermission_authenticated_user_with_password_not_admin(
        authenticated_user_instance
):
    authenticated_user_instance.password = "correct_password"
    authenticated_user_instance.is_admin = False
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission(password_required=True, password="correct_password"):
            pass
    with pytest.raises(HTTPException):
        with permissions.AdminRolePermission(password_required=True, password="wrong_password"):
            pass

def test_SupervisorRolePermission_anonymous_user(anonymous_user_instance):
    # pylint: disable=unused-argument
    with pytest.raises(HTTPException):
        with permissions.SupervisorRolePermission():
            pass

def test_SupervisorRolePermission_authenticated_user(authenticated_user_instance):
    obj = Mock()
    obj.check_supervisor = lambda user: user == authenticated_user_instance
    with permissions.SupervisorRolePermission(obj=obj):
        pass
    del obj.check_supervisor
    with pytest.raises(HTTPException):
        with permissions.SupervisorRolePermission():
            pass

def test_SupervisorRolePermission_anonymous_user_with_password(anonymous_user_instance):
    # pylint: disable=unused-argument
    obj = Mock()
    obj.check_supervisor = lambda user: False
    with pytest.raises(HTTPException):
        with permissions.SupervisorRolePermission(
            obj=obj,
            password_required=True,
            password="any_password"
        ):
            pass

def test_SupervisorRolePermission_authenticated_user_with_password_with_check_supervisor(
        authenticated_user_instance
):
    authenticated_user_instance.password = "correct_password"
    obj = Mock()
    obj.check_supervisor = lambda user: user == authenticated_user_instance
    with permissions.SupervisorRolePermission(
        obj=obj,
        password_required=True,
        password="correct_password"
    ):
        pass
    with pytest.raises(HTTPException):
        with permissions.SupervisorRolePermission(
            obj=obj,
            password_required=True,
            password="wrong_password"
        ):
            pass

def test_SupervisorRolePermission_authenticated_user_with_password_without_check_supervisor(
        authenticated_user_instance
):
    authenticated_user_instance.password = "correct_password"
    obj = Mock()
    del obj.check_supervisor
    with pytest.raises(HTTPException):
        with permissions.SupervisorRolePermission(
            obj=obj,
            password_required=True,
            password="correct_password"
        ):
            pass
    with pytest.raises(HTTPException):
        with permissions.SupervisorRolePermission(
            obj=obj,
            password_required=True,
            password="wrong_password"
        ):
            pass

def test_OwnerRolePermission_anonymous_user(anonymous_user_instance):
    # pylint: disable=unused-argument
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission():
            pass

def test_OwnerRolePermission_authenticated_user(authenticated_user_instance):
    obj = Mock()
    obj.check_owner = lambda user: user == authenticated_user_instance
    with permissions.OwnerRolePermission(obj=obj):
        pass
    del obj.check_Owner
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission():
            pass

def test_OwnerRolePermission_anonymous_user_with_password(anonymous_user_instance):
    # pylint: disable=unused-argument
    obj = Mock()
    obj.check_owner = lambda user: False
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission(
            obj=obj,
            password_required=True,
            password="any_password"
        ):
            pass

def test_OwnerRolePermission_authenticated_user_with_password_with_check_owner(
        authenticated_user_instance
):
    authenticated_user_instance.password = "correct_password"
    obj = Mock()
    obj.check_owner = lambda user: user == authenticated_user_instance
    with permissions.OwnerRolePermission(
        obj=obj,
        password_required=True,
        password="correct_password"
    ):
        pass
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission(
            obj=obj,
            password_required=True,
            password="wrong_password"
        ):
            pass

def test_OwnerRolePermission_authenticated_user_with_password_without_check_owner(
        authenticated_user_instance
):
    authenticated_user_instance.password = "correct_password"
    obj = Mock()
    del obj.check_owner
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission(
            obj=obj,
            password_required=True,
            password="correct_password"
        ):
            pass
    with pytest.raises(HTTPException):
        with permissions.OwnerRolePermission(
            obj=obj,
            password_required=True,
            password="wrong_password"
        ):
            pass