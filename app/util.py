from flask import session
from app.models import Version


# Helper function for procedure route.
# @return A list of tuples mapping steps and results
def get_test_steps_and_results(steps, version_id):
    results = []
    for step in steps:
        runs = list(filter(lambda x: x.version_id == version_id, step.runs))
        if len(runs) == 0:
            results.append(0)
        else:
            recent_run = max(runs, key=lambda x: x.timestamp)
            results.append(1 if recent_run.passing else -1)
    return list(zip(steps, results))


# Ensure session variables contains a valid version id. Otherwise
# set it to a default.
def ensure_version(project_id):
    versions = list(Version.query.filter_by(project_id=project_id))
    assert len(versions) != 0
    if "version_id" not in session or not any(
        x.id == session["version_id"] for x in versions
    ):
        curr_version = versions[0]
        session["version_id"] = curr_version.id
        print("changed")
