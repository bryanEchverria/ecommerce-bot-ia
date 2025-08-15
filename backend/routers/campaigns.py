from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from uuid import uuid4
from database import get_db
from models import Campaign as CampaignModel
from schemas import Campaign, CampaignCreate, CampaignUpdate
import crud

router = APIRouter()

@router.get("/campaigns", response_model=List[Campaign])
def get_campaigns(db: Session = Depends(get_db)):
    campaigns = crud.get_campaigns(db)
    # Convert product_ids from JSON string to list
    for campaign in campaigns:
        if campaign.product_ids:
            try:
                campaign.product_ids = json.loads(campaign.product_ids)
            except json.JSONDecodeError:
                campaign.product_ids = []
        else:
            campaign.product_ids = []
    return campaigns

@router.get("/campaigns/{campaign_id}", response_model=Campaign)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Convert product_ids from JSON string to list
    if campaign.product_ids:
        try:
            campaign.product_ids = json.loads(campaign.product_ids)
        except json.JSONDecodeError:
            campaign.product_ids = []
    else:
        campaign.product_ids = []
    
    return campaign

@router.post("/campaigns", response_model=Campaign)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    campaign_id = str(uuid4())
    
    # Convert product_ids list to JSON string for storage
    campaign_dict = campaign.dict()
    campaign_dict['product_ids'] = json.dumps(campaign.product_ids)
    
    db_campaign = crud.create_campaign(db=db, campaign=campaign_dict, campaign_id=campaign_id)
    
    # Convert back to list for response
    db_campaign.product_ids = campaign.product_ids
    return db_campaign

@router.put("/campaigns/{campaign_id}", response_model=Campaign)
def update_campaign(campaign_id: str, campaign: CampaignUpdate, db: Session = Depends(get_db)):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Convert product_ids list to JSON string if provided
    update_data = campaign.dict(exclude_unset=True)
    if 'product_ids' in update_data:
        update_data['product_ids'] = json.dumps(update_data['product_ids'])
    
    updated_campaign = crud.update_campaign(db=db, campaign_id=campaign_id, campaign=update_data)
    
    # Convert back to list for response
    if updated_campaign.product_ids:
        try:
            updated_campaign.product_ids = json.loads(updated_campaign.product_ids)
        except json.JSONDecodeError:
            updated_campaign.product_ids = []
    else:
        updated_campaign.product_ids = []
    
    return updated_campaign

@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    crud.delete_campaign(db=db, campaign_id=campaign_id)
    return {"message": "Campaign deleted successfully"}