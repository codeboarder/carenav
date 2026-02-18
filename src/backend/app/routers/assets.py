"""Asset sale pipeline API endpoints for CareNav Florida (Ticket 8)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import Asset, get_async_session_maker
from app.schemas import AssetCreate, AssetResponse, AssetUpdate

router = APIRouter(prefix="/assets", tags=["assets"])


async def get_db():
    """Get database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session


@router.post("/{patient_id}", response_model=AssetResponse)
async def create_asset(
    patient_id: int,
    asset_data: AssetCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new asset for a patient."""
    asset = Asset(
        patient_id=patient_id,
        name=asset_data.name,
        asset_type=asset_data.asset_type,
        owner=asset_data.owner,
        estimated_value=asset_data.estimated_value,
        title_status=asset_data.title_status,
        sale_status=asset_data.sale_status,
        sale_channel=asset_data.sale_channel,
        linked_insurance=asset_data.linked_insurance,
        notes=asset_data.notes,
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.get("/{patient_id}", response_model=list[AssetResponse])
async def get_patient_assets(
    patient_id: int,
    owner: str = None,
    sale_status: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all assets for a patient."""
    query = select(Asset).where(Asset.patient_id == patient_id)
    if owner:
        query = query.where(Asset.owner == owner)
    if sale_status:
        query = query.where(Asset.sale_status == sale_status)
    query = query.order_by(Asset.asset_type, Asset.name)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{patient_id}/pipeline")
async def get_asset_sale_pipeline(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get asset sale pipeline for dashboard."""
    query = select(Asset).where(Asset.patient_id == patient_id)
    result = await db.execute(query)
    assets = result.scalars().all()
    
    pipeline = {
        "not_for_sale": [],
        "preparing": [],
        "listed": [],
        "pending_sale": [],
        "sold": [],
    }
    
    total_estimated = 0
    total_sold = 0
    pending_title = []
    
    for asset in assets:
        status = asset.sale_status or "not_for_sale"
        if status in pipeline:
            asset_info = {
                "id": asset.id,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "owner": asset.owner,
                "estimated_value": float(asset.estimated_value) if asset.estimated_value else 0,
                "title_status": asset.title_status,
                "sale_channel": asset.sale_channel,
                "linked_insurance": asset.linked_insurance,
            }
            pipeline[status].append(asset_info)
        
        if asset.estimated_value:
            total_estimated += float(asset.estimated_value)
        if status == "sold" and asset.actual_sale_price:
            total_sold += float(asset.actual_sale_price)
        if asset.title_status in ["ordered", "in_transit"]:
            pending_title.append({
                "id": asset.id,
                "name": asset.name,
                "title_status": asset.title_status,
            })
    
    return {
        "pipeline": pipeline,
        "total_estimated_value": total_estimated,
        "total_sold_value": total_sold,
        "pending_title": pending_title,
        "total_assets": len(assets),
    }


@router.patch("/{asset_id}")
async def update_asset(
    asset_id: int,
    update_data: AssetUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update asset status or sale details."""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    if update_data.title_status is not None:
        asset.title_status = update_data.title_status
    if update_data.sale_status is not None:
        asset.sale_status = update_data.sale_status
    if update_data.sale_channel is not None:
        asset.sale_channel = update_data.sale_channel
    if update_data.actual_sale_price is not None:
        asset.actual_sale_price = update_data.actual_sale_price
    if update_data.sale_date is not None:
        asset.sale_date = update_data.sale_date
    if update_data.notes is not None:
        asset.notes = update_data.notes
    
    await db.commit()
    return {
        "id": asset_id,
        "title_status": asset.title_status,
        "sale_status": asset.sale_status,
    }


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an asset."""
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    await db.delete(asset)
    await db.commit()
    return {"deleted": True}
