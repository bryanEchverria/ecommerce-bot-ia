from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import json
from uuid import uuid4
from database import get_async_db
from models import Campaign as CampaignModel
from schemas import Campaign, CampaignCreate, CampaignUpdate
from tenant_middleware import get_tenant_id
import crud_async

router = APIRouter()

def _convert_product_ids_to_list(product_ids_json: str) -> List[str]:
    """Helper function to convert product_ids JSON string to list"""
    if product_ids_json:
        try:
            return json.loads(product_ids_json)
        except json.JSONDecodeError:
            return []
    return []

@router.get("/campaigns", response_model=List[Campaign])
async def get_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_async_db)
):
    """Get campaigns with async pagination and SQL filtering - filtered by tenant"""
    # Get tenant_id from middleware context
    tenant_id = get_tenant_id()
    
    campaigns = await crud_async.get_campaigns_async(
        db, skip=skip, limit=limit, status=status, client_id=tenant_id
    )
    
    # Convert product_ids from JSON string to list
    for campaign in campaigns:
        campaign.product_ids = _convert_product_ids_to_list(campaign.product_ids)
    
    return campaigns

@router.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get a single campaign by ID"""
    campaign = await crud_async.get_campaign_async(db, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Convert product_ids from JSON string to list
    campaign.product_ids = _convert_product_ids_to_list(campaign.product_ids)
    
    return campaign

@router.post("/campaigns", response_model=Campaign)
async def create_campaign(campaign: CampaignCreate, db: AsyncSession = Depends(get_async_db)):
    """Create a new campaign with JSON product_ids serialization"""
    campaign_id = str(uuid4())
    
    # Convert product_ids list to JSON string for storage
    campaign_dict = campaign.dict()
    campaign_dict['product_ids'] = json.dumps(campaign.product_ids)
    
    db_campaign = await crud_async.create_campaign_async(db=db, campaign=campaign_dict, campaign_id=campaign_id)
    
    # Convert back to list for response
    db_campaign.product_ids = campaign.product_ids
    return db_campaign

@router.put("/campaigns/{campaign_id}", response_model=Campaign)
async def update_campaign(campaign_id: str, campaign: CampaignUpdate, db: AsyncSession = Depends(get_async_db)):
    """Update an existing campaign"""
    db_campaign = await crud_async.get_campaign_async(db, campaign_id=campaign_id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Convert product_ids list to JSON string if provided
    update_data = campaign.dict(exclude_unset=True)
    if 'product_ids' in update_data:
        update_data['product_ids'] = json.dumps(update_data['product_ids'])
    
    updated_campaign = await crud_async.update_campaign_async(db=db, campaign_id=campaign_id, campaign=update_data)
    
    # Convert back to list for response
    updated_campaign.product_ids = _convert_product_ids_to_list(updated_campaign.product_ids)
    
    return updated_campaign

@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(campaign_id: str, db: AsyncSession = Depends(get_async_db)):
    """Delete a campaign"""
    db_campaign = await crud_async.get_campaign_async(db, campaign_id=campaign_id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    await crud_async.delete_campaign_async(db=db, campaign_id=campaign_id)
    return {"message": "Campaign deleted successfully"}