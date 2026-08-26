import os
import sys
import pymongo
from pymongo import ASCENDING, DESCENDING

# Configure UTF-8 for console output on Windows
if sys.stdout and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def load_env_mongodb_uri():
    # Attempt to load MONGODB_URI from the .env file in the root
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("MONGODB_URI="):
                    return line.strip().split("=", 1)[1].strip('"').strip("'")
    return None

def setup_database():
    mongo_uri = load_env_mongodb_uri()
    if not mongo_uri:
        # Fallback to the known Atlas connection string
        mongo_uri = "mongodb+srv://vovankhanh937_db_user:QahIPyBiiGa8t65L@cluster0.ozrzc9i.mongodb.net/?retryWrites=true&w=majority"
    
    db_name = "Mova"
    print(f"Connecting to MongoDB Atlas at URI: {mongo_uri[:50]}...")
    
    try:
        client = pymongo.MongoClient(mongo_uri)
        client.admin.command('ping')
        print("✅ Connected successfully to MongoDB Atlas!")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)

    db = client[db_name]
    print(f"\n--- INITIALIZING COLLECTIONS & INDEXES FOR DATABASE '{db_name}' ---")

    # 1. users
    print("Creating indexes for: users")
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.users.create_index([("email", ASCENDING)], unique=True)

    # 2. user_followers
    print("Creating indexes for: user_followers")
    db.user_followers.create_index([("follower_id", ASCENDING), ("following_id", ASCENDING)], unique=True)
    db.user_followers.create_index([("following_id", ASCENDING)])

    # 3. posts
    print("Creating indexes for: posts")
    db.posts.create_index([("user_id", ASCENDING)])
    db.posts.create_index([("created_at", DESCENDING)])

    # 4. post_likes
    print("Creating indexes for: post_likes")
    db.post_likes.create_index([("user_id", ASCENDING), ("post_id", ASCENDING)], unique=True)

    # 5. post_comments
    print("Creating indexes for: post_comments")
    db.post_comments.create_index([("post_id", ASCENDING)])

    # 6. saved_posts
    print("Creating indexes for: saved_posts")
    db.saved_posts.create_index([("user_id", ASCENDING), ("post_id", ASCENDING)], unique=True)

    # 7. hashtags
    print("Creating indexes for: hashtags")
    db.hashtags.create_index([("name", ASCENDING)], unique=True)
    db.hashtags.create_index([("usage_count", DESCENDING)])

    # 8. post_hashtags
    print("Creating indexes for: post_hashtags")
    db.post_hashtags.create_index([("post_id", ASCENDING), ("hashtag_id", ASCENDING)], unique=True)
    db.post_hashtags.create_index([("hashtag_id", ASCENDING)])

    # 9. notifications
    print("Creating indexes for: notifications")
    db.notifications.create_index([("user_id", ASCENDING), ("is_read", ASCENDING)])

    # 10. direct_messages
    print("Creating indexes for: direct_messages")
    db.direct_messages.create_index([("receiver_id", ASCENDING), ("is_read", ASCENDING)])
    db.direct_messages.create_index([("sender_id", ASCENDING), ("receiver_id", ASCENDING)])

    # 11. assets
    print("Creating indexes for: assets")
    db.assets.create_index([("owner_id", ASCENDING)])
    db.assets.create_index([("public_id", ASCENDING)], unique=True)

    # 12. scripts
    print("Creating indexes for: scripts")
    db.scripts.create_index([("owner_id", ASCENDING)])

    # 13. video_tasks
    print("Creating indexes for: video_tasks")
    db.video_tasks.create_index([("owner_id", ASCENDING)])
    db.video_tasks.create_index([("script_id", ASCENDING)])
    db.video_tasks.create_index([("temporal_workflow_id", ASCENDING)])

    # 14. credit_logs
    print("Creating indexes for: credit_logs")
    db.credit_logs.create_index([("user_id", ASCENDING)])

    # 15. scraped_docs
    print("Creating indexes for: scraped_docs")
    db.scraped_docs.create_index([("url", ASCENDING)], unique=True)

    # 16. rag_chunks
    print("Creating indexes for: rag_chunks")
    db.rag_chunks.create_index([("doc_id", ASCENDING)])
    db.rag_chunks.create_index([("qdrant_vector_id", ASCENDING)], unique=True)

    print("\n✅ COMPLETE! All 16 collections and Indexes initialized successfully.")

if __name__ == "__main__":
    setup_database()
