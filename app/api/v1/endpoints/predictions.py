from fastapi import APIRouter

router = APIRouter(prefix="/predictions", tags=["predictions"])

@router.post("/")
async def create_prediction():
    return {"message": "Create prediction"}

@router.get("/")
async def read_predictions():
    return {"message": "Get all predictions"}

@router.get("/{prediction_id}")
async def read_prediction(prediction_id: int):
    return {"message": f"Get prediction {prediction_id}"}

@router.put("/{prediction_id}")
async def update_prediction(prediction_id: int):
    return {"message": f"Update prediction {prediction_id}"}

@router.delete("/{prediction_id}")
async def delete_prediction(prediction_id: int):
    return {"message": f"Delete prediction {prediction_id}"}
