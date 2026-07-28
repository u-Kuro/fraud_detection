import subprocess

from fastapi import APIRouter, Request, Response

from tools.host_bridge.modules.configs.project import ProjectConfig

router = APIRouter(prefix="/repos", tags=["act"])

@router.post(
    "/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches",
    status_code=204,
)
async def dispatch(workflow_file: str, request: Request):
    body = await request.json() if await request.body() else {}
    inputs = body.get("inputs", {})

    cmd = ["act", "workflow_dispatch", "-W", f".github/workflows/{workflow_file}"]
    for k, v in inputs.items():
        cmd += ["--input", f"{k}={v}"]

    subprocess.Popen(cmd, cwd=ProjectConfig.root_path)

    return Response(status_code=204)