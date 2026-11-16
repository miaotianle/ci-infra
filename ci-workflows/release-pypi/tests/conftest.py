"""Shared registry of matrix-release.yml features that are currently disabled (commented out) in the workflow."""

from pathlib import Path

import pytest
import yaml


WORKFLOW_PATH = Path(__file__).resolve().parents[3] / ".github/workflows/matrix-release.yml"

# Tests covering these features are skipped until the feature is restored; remove the entry when re-enabling it.
DISABLED_JOBS = frozenset({"publish-sdist", "update-metadata", "post-release-data"})
DISABLED_STEPS = frozenset({
    ("prepare-matrix", "Validate caller organization"),
    ("matrix-job", "Repack wheel"),
    ("matrix-job", "Rename wheel"),
    ("matrix-job", "Upload wheel to Artifactory"),
    ("matrix-job", "Generate release data JSON"),
    ("matrix-job", "Save release data JSON"),
    ("matrix-job", "Record matrix job success"),
    ("matrix-job", "Save matrix job success marker"),
})


def feature_present(workflow, job, step=None):
    jobs = workflow["jobs"]
    if step is None:
        return job in jobs
    return job in jobs and any(item.get("name") == step for item in jobs[job]["steps"])


@pytest.fixture
def disabled_workflow_features():
    return {"jobs": DISABLED_JOBS, "steps": DISABLED_STEPS}


@pytest.fixture
def skip_if_disabled():
    workflow = yaml.load(WORKFLOW_PATH.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    def skip(job, step=None):
        disabled = job in DISABLED_JOBS if step is None else (job, step) in DISABLED_STEPS
        if not disabled:
            return
        feature = f"job {job}" if step is None else f"step {job}/{step}"
        # A registered feature that is present again must fail loudly instead of silently skipping its tests.
        if feature_present(workflow, job, step):
            pytest.fail(f"{feature} is enabled again in matrix-release.yml; remove it from the disabled registry in conftest.py")
        pytest.skip(f"{feature} is disabled in matrix-release.yml")

    return skip
