from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..schemas.buyers import BuyerProfileCreate
from ..schemas.farmers import FarmerProfileCreate
from ..schemas.users import UserUpdate
from ..utils.security import check_user_role, decode_jwt_token
from .auth import users_repository

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")


# Create a farmer profile (Farmers and Admins)
@router.post("/farmer/")
def create_farmer_profile(
    profile_data: FarmerProfileCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    check_user_role(token, db, ["Farmer", "Admin"])
    user_id = decode_jwt_token(token)
    profile = users_repository.create_profile(db, user_id, profile_data)
    return profile
    # return JSONResponse(
    #     status_code=200,
    #     content={"message": "Farmer profile created"}
    # )
    return Response(content="Farmer profile created", status_code=200)


# Create a buyer profile (Buyers and Admins)
@router.post("/buyer/")
def create_buyer_profile(
    profile_data: BuyerProfileCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    check_user_role(token, db, ["Buyer", "Admin"])
    user_id = decode_jwt_token(token)
    profile = users_repository.create_profile(db, user_id, profile_data)
    return profile
    return JSONResponse(
        status_code=200,
        content={"message": "Buyer profile created"}
    )
    return Response(content="Buyer profile created", status_code=200)


# Get current user's profile
@router.get("/me")
def get_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = decode_jwt_token(token)
    user = users_repository.get_user_by_id(db, user_id)

    # Use the 'profile' property
    profile = user.profile

    # if user.role == "Admin":
    #     return {"message": "Admin users do not have a specific profile."}
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile

@router.patch("/update")
def update_user(
        user_input: UserUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
):
    user_id = decode_jwt_token(token)
    updated_user = users_repository.update_user(db, user_id, user_input)
    return {
        "message": "User updated successfully",
        "user": updated_user,
    }

# @router.get("/me", response_model=UserProfileInfo, status_code=200)
# def get_user_and_profile(
#         token: str = Depends(oauth2_scheme),
#         db: Session = Depends(get_db)
# ):
#     """
#     Return user info along with the profile.
#     """
#     # Decode token to get user ID
#     user_id = decode_jwt_token(token)
#
#     # Fetch user
#     user = users_repository.get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     # Fetch profile
#     profile = user.profile
#     if not profile:
#         raise HTTPException(status_code=404, detail="Profile not found")
#
#     # Combine user info and profile
#     return UserProfileInfo(
#         id=user.id,
#         fullname=user.fullname,
#         email=user.email,
#         phone=user.phone,
#         role=user.role,
#         profile=ProfileInfo(
#             farm_name=profile.farm_name,
#             location=profile.location,
#             farm_size=profile.farm_size
#         ),
#     )



@router.get("/farmer/{farmer_id}")
def get_profile(farmer_id: int, db: Session = Depends(get_db)):
    farmer = users_repository.get_profile_by_id(db, farmer_id)

    # if user.role == "Admin":
    #     return {"message": "Admin users do not have a specific profile."}
    if not farmer:
        raise HTTPException(status_code=404, detail="Profile not found")

    return farmer