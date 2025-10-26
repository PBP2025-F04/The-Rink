import os
import random
import django
from faker import Faker
from django.contrib.auth.models import User
from forum.models import Post, Reply, UpVote

# --- setup Django environment ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "the_rink.settings")
django.setup()

fake = Faker()

# --- Clear old data ---
print("🧹 Deleting old data...")
UpVote.objects.all().delete()
Reply.objects.all().delete()
Post.objects.all().delete()

# --- Create dummy users ---
print("👥 Creating users...")
users = []
for i in range(10):
    user, _ = User.objects.get_or_create(
        username=f"user{i+1}",
        defaults={"email": f"user{i+1}@example.com"}
    )
    users.append(user)

# --- thumbnail URLs ---
thumbnail_urls = [
    "https://images.unsplash.com/photo-1574629810360-7efbbe195018?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1604948501466-0e3b3c31c9c7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1517495306984-937e6e1e251f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1587385789090-98b3b931a9b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1611131805859-df8eac655a2a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1604933762899-c25c25ddbab3?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1602080756183-0d0eaf4388af?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1584267385606-5d1b4b8b3a0f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1602940659805-f578c13c3d7b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
]

# --- Example titles ---
titles = [
    "Tips for Maintaining Your Ice Skates",
    "Best Hockey Gear for Beginners in 2025",
    "How to Master Backward Skating Fast",
    "My Experience Visiting The New Ice Arena",
    "Top 5 Hockey Teams This Season",
    "Why I Love Playing at Night Sessions",
    "How to Fix Dull Skate Blades",
    "What to Bring for Your First Skating Lesson",
    "The Psychology Behind Team Spirit on Ice",
    "Hidden Gems: Best Ice Rinks Around Jakarta",
]

# --- Create posts ---
print("📝 Creating posts...")
posts = []
for i in range(50):
    author = random.choice(users)
    title = random.choice(titles)
    content = (
        f"{fake.paragraph(nb_sentences=4)}\n\n"
        f"Have you guys ever tried this before? I’d love to hear your opinions below!"
    )
    img = random.choice(thumbnail_urls)
    post = Post.objects.create(
        author=author,
        title=title,
        content=content,
        thumbnail_url=img,
    )
    posts.append(post)

# --- Create replies ---
print("💬 Creating replies...")
replies = []
reply_templates = [
    "I totally agree with you!",
    "That’s an interesting point, thanks for sharing.",
    "I had a similar experience last week.",
    "Could you share more about this?",
    "This helped me a lot, thanks!",
    "I think it depends on the rink condition.",
    "Nice post, I’ll try that tip soon!",
]
for post in posts:
    for _ in range(5):
        author = random.choice(users)
        content = random.choice(reply_templates)
        reply = Reply.objects.create(post=post, author=author, content=content)
        replies.append(reply)

# --- Create random upvotes/downvotes ---
print("👍👎 Creating votes...")
for post in posts:
    voters = random.choices(users, k=random.randint(20, 60))
    for voter in voters:
        is_up = random.random() < 0.75  # 75% like
        UpVote.objects.create(user=voter, post=post, is_upvote=is_up)

for reply in replies:
    voters = random.choices(users, k=random.randint(5, 15))
    for voter in voters:
        is_up = random.random() < 0.7
        UpVote.objects.create(user=voter, reply=reply, is_upvote=is_up)

print("✅ Successfully created 50 posts, 250 replies, and thousands of votes!")
