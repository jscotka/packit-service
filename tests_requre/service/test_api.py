import pytest

from tests_requre.service.conftest import build_info_dict

from packit_service.service.app import get_flask_application
from flask import url_for


@pytest.fixture
def app():
    app = get_flask_application()
    return app


# Check if the API is working
def test_api_health(client):
    response = client.get(url_for("api.healthz_health_check"))
    assert response.json == "We are healthy!"


#  Test Copr Builds
def test_copr_builds_list(client, clean_before_and_after, multiple_copr_builds):
    response = client.get(url_for("api.copr-builds_copr_builds_list"))
    response_dict = response.json
    assert response_dict[0]["project"] == "SomeUser-hello-world-9"
    assert response_dict[0]["build_id"] == "123456"
    assert response_dict[1]["project"] == build_info_dict["project"]
    assert response_dict[1]["owner"] == build_info_dict["owner"]
    assert response_dict[1]["build_id"] == build_info_dict["build_id"]
    assert response_dict[1]["web_url"] == build_info_dict["web_url"]
    assert response_dict[1]["repo_namespace"] == build_info_dict["repo_namespace"]
    assert response_dict[1]["repo_name"] == build_info_dict["repo_name"]
    assert len(response_dict[1]["chroots"]) == 2
    assert len(list(response_dict[1]["status_per_chroot"])) == 2
    assert response_dict[1]["status_per_chroot"]["fedora-43-x86_64"] == "success"
    assert response_dict[1]["status_per_chroot"]["fedora-42-x86_64"] == "pending"
    assert response_dict[1]["build_submitted_time"] is not None
    assert len(response_dict) == 2  # three builds, but two unique build ids


# Test detailed build info
def test_detailed_copr_build_info(client, clean_before_and_after, multiple_copr_builds):
    response = client.get(
        url_for("api.copr-builds_installation_item", id=build_info_dict["build_id"])
    )
    response_dict = response.json
    assert response_dict["project"] == build_info_dict["project"]
    assert response_dict["owner"] == build_info_dict["owner"]
    assert response_dict["build_id"] == build_info_dict["build_id"]
    assert response_dict["commit_sha"] == build_info_dict["commit_sha"]
    assert response_dict["web_url"] == build_info_dict["web_url"]
    assert response_dict["srpm_logs"] == build_info_dict["srpm_logs"]
    assert response_dict["ref"] == build_info_dict["ref"]
    assert response_dict["repo_namespace"] == build_info_dict["repo_namespace"]
    assert response_dict["repo_name"] == build_info_dict["repo_name"]
    assert response_dict["git_repo"] == build_info_dict["git_repo"]
    assert response_dict["https_url"] == build_info_dict["https_url"]
    assert response_dict["pr_id"] == build_info_dict["pr_id"]
    assert len(response_dict["chroots"]) == 2
    assert len(list(response_dict["status_per_chroot"])) == 2
    assert response_dict["status_per_chroot"]["fedora-43-x86_64"] == "success"
    assert response_dict["status_per_chroot"]["fedora-42-x86_64"] == "pending"
    assert response_dict["build_submitted_time"] is not None


# Test Whitelist API (all)
def test_whitelist_all(client, clean_before_and_after, new_whitelist_entry):
    response = client.get(url_for("api.whitelist_white_list"))
    response_dict = response.json
    assert response_dict[0]["account"] == "Rayquaza"
    assert response_dict[0]["status"] == "approved_manually"
    assert len(list(response_dict)) == 1


# Test Whitelist API (specific user)
def test_whitelist_specific(client, clean_before_and_after, new_whitelist_entry):
    user_1 = client.get(url_for("api.whitelist_white_list_item", login="Rayquaza"))
    assert user_1.json["account"] == "Rayquaza"
    assert user_1.json["status"] == "approved_manually"

    user_2 = client.get(url_for("api.whitelist_white_list_item", login="Zacian"))
    assert user_2.status_code == 204  # No content when not in whitelist