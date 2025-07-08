#!/usr/bin/env python3
"""
Database seeding script for ChromaDB
Adds 100 diverse documents with realistic content for testing search functionality
"""

import random
from services.chroma import collection

# Diverse document content covering various topics
documents = [
    # Technology & Programming
    "Python is a versatile programming language used for web development, data science, and automation.",
    "Machine learning algorithms can predict customer behavior and improve business outcomes.",
    "Docker containers provide consistent environments across different development stages.",
    "REST APIs enable communication between different software systems over HTTP.",
    "Git version control helps developers track changes and collaborate on code projects.",
    "JavaScript frameworks like React and Vue.js simplify frontend development.",
    "Database optimization techniques can significantly improve application performance.",
    "Cloud computing services like AWS and Azure provide scalable infrastructure solutions.",
    "Microservices architecture allows for better scalability and maintainability.",
    "DevOps practices bridge the gap between development and operations teams.",
    
    # Science & Nature
    "Photosynthesis is the process by which plants convert sunlight into chemical energy.",
    "The human brain contains approximately 86 billion neurons and trillions of connections.",
    "Climate change affects global weather patterns and sea levels worldwide.",
    "DNA contains the genetic instructions for building and maintaining living organisms.",
    "The theory of evolution explains how species change over time through natural selection.",
    "Quantum physics describes the behavior of matter at the smallest scales.",
    "Biodiversity is essential for maintaining healthy ecosystems and human survival.",
    "Renewable energy sources like solar and wind power reduce carbon emissions.",
    "The water cycle continuously moves water between the atmosphere, land, and oceans.",
    "Plate tectonics explains the movement of Earth's crust and formation of mountains.",
    
    # Health & Medicine
    "Regular exercise improves cardiovascular health and reduces stress levels.",
    "A balanced diet rich in fruits and vegetables supports immune system function.",
    "Sleep is essential for memory consolidation and overall brain health.",
    "Mental health awareness has increased significantly in recent years.",
    "Vaccines protect against infectious diseases by stimulating immune responses.",
    "Antibiotics treat bacterial infections but are ineffective against viruses.",
    "Chronic stress can lead to various health problems including heart disease.",
    "Meditation and mindfulness practices reduce anxiety and improve focus.",
    "Genetic testing can identify inherited health conditions and disease risks.",
    "Telemedicine provides remote healthcare access through digital platforms.",
    
    # Business & Economics
    "Supply chain management optimizes the flow of goods from suppliers to customers.",
    "Marketing strategies help businesses connect with their target audiences.",
    "Financial planning involves budgeting, saving, and investment decisions.",
    "Customer relationship management systems improve business efficiency.",
    "E-commerce platforms enable online shopping and digital transactions.",
    "Project management methodologies ensure successful project delivery.",
    "Data analytics helps businesses make informed strategic decisions.",
    "Human resources departments handle employee recruitment and development.",
    "Inventory management systems track product levels and prevent stockouts.",
    "Business intelligence tools provide insights into company performance.",
    
    # Education & Learning
    "Online learning platforms make education accessible to people worldwide.",
    "Critical thinking skills are essential for problem-solving and decision-making.",
    "Language learning apps use spaced repetition to improve retention.",
    "STEM education prepares students for careers in science and technology.",
    "Lifelong learning helps individuals adapt to changing job market demands.",
    "Educational technology enhances classroom engagement and learning outcomes.",
    "Distance learning programs provide flexibility for working professionals.",
    "Assessment methods evaluate student understanding and progress.",
    "Curriculum development ensures educational content meets learning objectives.",
    "Teacher training programs improve classroom instruction quality.",
    
    # Travel & Geography
    "Sustainable tourism practices protect natural environments and local cultures.",
    "Travel planning apps help tourists navigate unfamiliar destinations.",
    "Cultural exchange programs promote understanding between different societies.",
    "Ecotourism supports conservation efforts while providing economic benefits.",
    "Historical landmarks preserve cultural heritage for future generations.",
    "Geographic information systems map and analyze spatial data.",
    "Climate zones determine weather patterns and vegetation types.",
    "Urban planning creates livable and sustainable city environments.",
    "Transportation networks connect communities and facilitate trade.",
    "Natural disasters require emergency response and recovery planning.",
    
    # Food & Cooking
    "Fermentation processes create foods like yogurt, cheese, and kimchi.",
    "Molecular gastronomy explores the science behind cooking techniques.",
    "Sustainable farming practices protect soil health and reduce pollution.",
    "Food safety regulations ensure consumer protection and public health.",
    "Culinary traditions preserve cultural heritage and family recipes.",
    "Nutrition science studies how food affects human health and wellness.",
    "Restaurant management involves operations, marketing, and customer service.",
    "Food preservation methods extend shelf life and reduce waste.",
    "Wine production combines agricultural science with artistic craftsmanship.",
    "Baking chemistry explains how ingredients interact during cooking.",
    
    # Arts & Culture
    "Digital art tools enable new forms of creative expression and collaboration.",
    "Museum collections preserve cultural artifacts and historical objects.",
    "Film production involves storytelling, cinematography, and post-production.",
    "Music theory provides the foundation for composition and performance.",
    "Literature reflects societal values and human experiences across time.",
    "Architecture combines aesthetic design with functional requirements.",
    "Photography captures moments and tells visual stories.",
    "Theater performances bring stories to life through acting and staging.",
    "Fashion design reflects cultural trends and individual expression.",
    "Art conservation preserves valuable works for future generations.",
    
    # Sports & Fitness
    "Sports psychology helps athletes improve performance and mental resilience.",
    "Nutrition timing optimizes athletic performance and recovery.",
    "Injury prevention programs reduce sports-related health risks.",
    "Team sports develop leadership and collaboration skills.",
    "Endurance training improves cardiovascular fitness and stamina.",
    "Strength training builds muscle mass and bone density.",
    "Sports analytics use data to improve team strategies and player performance.",
    "Rehabilitation programs help athletes recover from injuries.",
    "Sports medicine combines medical knowledge with athletic training.",
    "Olympic games showcase international athletic competition and unity.",
    
    # Environment & Sustainability
    "Carbon footprint reduction helps combat climate change impacts.",
    "Waste management systems process and dispose of materials safely.",
    "Green building practices create energy-efficient and sustainable structures.",
    "Water conservation techniques preserve freshwater resources.",
    "Recycling programs reduce landfill waste and resource consumption.",
    "Environmental impact assessments evaluate project sustainability.",
    "Clean energy technologies reduce dependence on fossil fuels.",
    "Sustainable agriculture practices protect soil and water quality.",
    "Wildlife conservation efforts protect endangered species and habitats.",
    "Environmental education raises awareness about ecological issues.",
    
    # Social Issues & Society
    "Social media platforms connect people but can impact mental health.",
    "Diversity and inclusion initiatives create more equitable workplaces.",
    "Community development programs strengthen local neighborhoods.",
    "Mental health awareness reduces stigma and improves access to care.",
    "Digital privacy protection safeguards personal information online.",
    "Work-life balance improves employee satisfaction and productivity.",
    "Social entrepreneurship addresses societal problems through business solutions.",
    "Volunteer programs support community needs and personal growth.",
    "Civic engagement strengthens democratic processes and community bonds.",
    "Social justice movements advocate for equality and human rights.",
    
    # Finance & Investment
    "Compound interest allows investments to grow exponentially over time.",
    "Diversification reduces investment risk by spreading assets across categories.",
    "Retirement planning ensures financial security in later years.",
    "Cryptocurrency markets operate 24/7 and are highly volatile.",
    "Real estate investment provides both income and appreciation potential.",
    "Stock market analysis helps investors make informed decisions.",
    "Tax planning strategies minimize tax liability and maximize savings.",
    "Insurance products protect against financial losses and risks.",
    "Budgeting tools help individuals track spending and save money.",
    "Financial literacy education improves money management skills."
]

def seed_database():
    """
    Seed the ChromaDB collection with 100 diverse documents
    """
    try:
        # Generate unique IDs for each document
        ids = [f"doc_{i:03d}" for i in range(1, len(documents) + 1)]
        
        # Upsert documents into the collection
        collection.upsert(
            documents=documents,
            ids=ids
        )
        
        print(f"✅ Successfully seeded database with {len(documents)} documents")
        print(f"📊 Collection now contains {collection.count()} total documents")
        
        # Display some sample documents
        print("\n📝 Sample documents added:")
        for i in range(5):
            print(f"  {i+1}. {documents[i][:80]}...")
        
        print(f"\n🔍 You can now test your search endpoint with queries like:")
        print("   - 'machine learning'")
        print("   - 'sustainable practices'")
        print("   - 'health and wellness'")
        print("   - 'business strategies'")
        print("   - 'environmental protection'")
        
        return {
            "success": True,
            "message": f"Database seeded with {len(documents)} documents",
            "total_documents": collection.count()
        }
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        return {
            "success": False,
            "message": f"Error seeding database: {str(e)}"
        }

def clear_database():
    """
    Clear all documents from the collection (use with caution!)
    """
    try:
        # Delete all documents
        collection.delete(ids=collection.get()['ids'])
        print("🗑️  Database cleared successfully")
        return {
            "success": True,
            "message": "Database cleared successfully"
        }
    except Exception as e:
        print(f"❌ Error clearing database: {str(e)}")
        return {
            "success": False,
            "message": f"Error clearing database: {str(e)}"
        }

if __name__ == "__main__":
    print("🌱 ChromaDB Seeding Script")
    print("=" * 50)
    
    # Check if user wants to clear first
    response = input("Do you want to clear existing documents first? (y/N): ").lower()
    if response == 'y':
        clear_database()
    
    # Seed the database
    result = seed_database()
    
    if result["success"]:
        print(f"\n🎉 Seeding completed successfully!")
    else:
        print(f"\n💥 Seeding failed: {result['message']}") 