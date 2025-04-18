from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.kernel import sk_kernel
from semantic_kernel.planners import SequentialPlanner
from services.redis_memory_store import RedisMemoryStore
from semantic_kernel.functions.kernel_arguments import KernelArguments

router = APIRouter()
memory_store = RedisMemoryStore()

class AssistRequest(BaseModel):
    message: str

@router.post("/assist")
async def assist(req: AssistRequest):
    try:
        planner = SequentialPlanner(sk_kernel, service_id="default")

        # Create a plan based on natural language message
        plan = await planner.create_plan(req.message)

        print("Planner generated the following steps:")
        for i, step in enumerate(plan.steps):
            print(f"Step {i + 1}: {step.plugin_name}.{step.name}")
            print("Step parameters:", step.parameters)

        print("Full plan description:\n", plan.description)

        # Convert extracted planner parameters into KernelArguments
        extracted_args = {}
        for step in plan.steps:
            extracted_args.update(step.parameters)

        print("Extracted arguments from planner:", extracted_args)

        # Create a single KernelArguments object to pass into invoke
        
        kernel_args = KernelArguments(extracted_args)
        # Invoke the plan
        result = await plan.invoke(kernel=sk_kernel, arguments=kernel_args)
        return {
            "plan": plan.description,
            "result": str(result),
            "arguments_used": extracted_args
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{customer_id}")
async def get_history(customer_id: str):
    try:
        history = await memory_store.get_conversation_history(customer_id)

        return {
            "customer_id": customer_id,
            "history": history if history else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

