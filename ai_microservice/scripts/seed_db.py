import os
import sys
import uuid


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from shared.database import SessionLocal, Property
from shared.embedding_service import get_embedding

MOCK_PROPERTIES = [
    {
        "title": "Downtown Commercial Plaza",
        "description": "High-yield commercial fractional real estate located in the heart of Casablanca business district. Ideal for capital appreciation and stable passive income.",
        "min_investment": 1000.0,
        "investment_period": 36, # 3 years
        "risk_assessment": "medium",
        "rental_yield": 7.5,
        "expected_roi": 12.0,
        "price": 5000000.0,
        "location": "Casablanca",
        "property_type": "commercial",
    },
    {
        "title": "Marrakech Residential Villa",
        "description": "Luxury residential villa in Marrakech, perfect for short-term vacation rentals. Offers low risk with steady tourist demand.",
        "min_investment": 5000.0,
        "investment_period": 60, # 5 years
        "risk_assessment": "low",
        "rental_yield": 5.0,
        "expected_roi": 9.0,
        "price": 3000000.0,
        "location": "Marrakech",
        "property_type": "residential",
    },
    {
        "title": "Tangier Port Warehouse",
        "description": "Industrial warehouse near the Tangier Med port. High growth potential but requires a longer lock-in period and carries higher risk.",
        "min_investment": 2000.0,
        "investment_period": 84, # 7 years
        "risk_assessment": "high",
        "rental_yield": 9.5,
        "expected_roi": 14.0,
        "price": 8000000.0,
        "location": "Tangier",
        "property_type": "industrial",
    }
]

def seed_db():
    db = SessionLocal()
    

    if db.query(Property).count() > 0:
        print("Database already seeded. Clearing old data for a fresh start...")
        db.query(Property).delete()
        db.commit()
        
    print("Generating embeddings and seeding database...")
    for p_data in MOCK_PROPERTIES:
        text_to_embed = f"{p_data['title']}. {p_data['description']} Risk: {p_data['risk_assessment']}."
        embedding = get_embedding(text_to_embed)
        
        prop = Property(
            id=str(uuid.uuid4()),
            title=p_data["title"],
            description=p_data["description"],
            price=p_data["price"],
            min_investment=p_data["min_investment"],
            investment_period=p_data["investment_period"],
            risk_assessment=p_data["risk_assessment"],
            rental_yield=p_data["rental_yield"],
            expected_roi=p_data["expected_roi"],
            location=p_data["location"],
            property_type=p_data["property_type"],
            embedding=embedding
        )
        db.add(prop)
        
    db.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_db()
