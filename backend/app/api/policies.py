from fastapi import APIRouter, HTTPException

from app.data.policies import POLICIES

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.get("/{policy_type}")
def get_policy(policy_type: str):
    policy = POLICIES.get(policy_type)
    if policy is None:
        raise HTTPException(status_code=404, detail="Unknown policy type.")
    return policy


@router.get("")
def list_policies():
    return POLICIES