import random
from django.contrib.auth.models import User
from forum.models import Post, Reply, UpVote

UpVote.objects.all().delete()
Reply.objects.all().delete()
Post.objects.all().delete()

author_names = ["skater", "snowrider", "snowboarder", "skihunter", "icecoach"]
authors = []

for uname in author_names:
    user, created = User.objects.get_or_create(
        username=uname,
        defaults={"email": f"{uname}@example.com"}
    )
    if created:
        user.set_password("password123")
        user.save()
    authors.append(user)

print(f"Total authors: {len(authors)}")

thumbnails = [
    "https://tse2.mm.bing.net/th/id/OIP.REreGpO_pdlHVCNqg5-eZgHaFj?cb=ucfimg2&ucfimg=1&rs=1&pid=ImgDetMain&o=7&rm=3",
    "https://png.pngtree.com/png-vector/20220810/ourlarge/pngtree-people-jump-in-snow-png-image_5724003.png",
    "https://c.pxhere.com/photos/30/2a/snow_snowboarding_elevator_cable_car_winter_sport-1076356.jpg!d",
    "https://tse2.mm.bing.net/th/id/OIP.uYiRtuDzcAICbZIkYDFpwQHaE8?cb=ucfimg2&ucfimg=1&rs=1&pid=ImgDetMain&o=7&rm=3",
    "https://c.pxhere.com/photos/77/d6/winter_snow_paraglider_skis_mountains_nature_sport-1196079.jpg!d",
    "https://png.pngtree.com/thumb_back/fw800/background/20221214/pngtree-skiing-on-fresh-snow-during-winter-with-perfect-sunny-weather-photo-image_42923350.jpg",
    "https://th.bing.com/th/id/OIP.-1TWLqrRR8Vvo8nEhNmktwHaGK?w=216&h=180&c=7&r=0&o=7&cb=ucfimg2&dpr=1.5&pid=1.7&rm=3&ucfimg=1",
    "https://tse3.mm.bing.net/th/id/OIP.bTivT2UCW4XA3S53OjmKMgHaFA?cb=ucfimg2&ucfimg=1&rs=1&pid=ImgDetMain&o=7&rm=3",
    "https://snow-cab.transforms.svdcdn.com/production/images/SnowCab_People_0009.jpeg?w=1500&q=82&auto=format&fit=crop&dm=1570101926&s=98b2f9a361e8ba2628f3db4ddfc3ae7b",
    "https://tse1.mm.bing.net/th/id/OIP.Jr3PxrW99EiUGX8w2Qd7nAHaEH?cb=ucfimg2&ucfimg=1&rs=1&pid=ImgDetMain&o=7&rm=3",
]

sports = [
    "Ice Skating",
    "Snowboarding",
    "Ski Alpine",
    "Ski Cross Country",
    "Ice Hockey",
    "Curling",
    "Snowshoeing",
    "Freestyle Ski",
    "Figure Skating",
    "Snow Park Training",
]

title_templates = [
    "Panduan Dasar {sport} untuk Pemula",
    "Tips Latihan {sport} yang Aman dan Menyenangkan",
    "Hal yang Harus Kamu Tahu Sebelum Coba {sport}",
    "Kesalahan Umum Saat Main {sport} dan Cara Menghindarinya",
    "Latihan {sport} untuk Meningkatkan Keseimbangan dan Kontrol",
]

content_templates = [
    (
        "Olahraga salju seperti {sport} membutuhkan keseimbangan, kontrol tubuh, dan "
        "pemahaman dasar tentang teknik pengereman di permukaan bersalju atau es. "
        "Pada post ini, kita bahas langkah awal yang bisa kamu lakukan, mulai dari "
        "pemilihan perlengkapan, pemanasan, hingga tips supaya tidak cepat lelah di arena."
    ),
    (
        "{sport} sering dianggap sulit, padahal kalau dibiasakan pelan-pelan justru sangat "
        "menyenangkan. Di post ini, fokusnya adalah bagaimana membangun rasa percaya diri "
        "di atas es/salju, kapan waktu yang pas untuk latihan, dan apa saja kebiasaan buruk "
        "yang sebaiknya dihindari."
    ),
    (
        "Buat kamu yang baru mau mencoba {sport}, penting untuk memahami teknik dasar jatuh "
        "yang aman, cara bangkit, serta bagaimana menjaga sendi lutut dan pergelangan kaki "
        "tetap kuat. Post ini juga menyinggung pentingnya pemanasan dan pendinginan "
        "setelah latihan olahraga salju."
    ),
]

reply_templates = [
    "Wah penjelasannya membantu banget, aku jadi makin pengen coba {sport} musim liburan nanti!",
    "Aku pernah jatuh lumayan parah waktu pertama kali {sport}, tips di post ini bikin aku lebih siap.",
    "Kalau untuk pemula, kira-kira berapa lama sampai lumayan lancar {sport} ya?",
    "Setuju banget soal pentingnya pemanasan, aku merasa badan lebih enak setelah ikutin saran ini.",
    "Mantap! Boleh dong next bahas rekomendasi perlengkapan murah tapi awet buat {sport}.",
]

TOTAL_POSTS = 50
REPLIES_PER_POST = 5

for i in range(1, TOTAL_POSTS + 1):
    sport = random.choice(sports)
    author = random.choice(authors)

    title_template = random.choice(title_templates)
    content_template = random.choice(content_templates)

    title = title_template.format(sport=sport, idx=i)
    content = content_template.format(sport=sport, idx=i)

    thumbnail_url = thumbnails[(i - 1) % len(thumbnails)]

    post = Post.objects.create(
        author=author,
        title=title,
        content=content,
        thumbnail_url=thumbnail_url,
    )

    replies = []
    for j in range(1, REPLIES_PER_POST + 1):
        reply_author = random.choice(authors)
        reply_text = random.choice(reply_templates).format(sport=sport)
        reply = Reply.objects.create(
            post=post,
            author=reply_author,
            content=f"{reply_text}",
        )
        replies.append(reply)

    post_up_count = random.randint(11, 100)     
    post_down_count = random.randint(11, 100)

    for k in range(post_up_count):
        UpVote.objects.create(
            session_key=f"p{post.id}-up-{k}",
            post=post,
            is_upvote=True,
        )

    for k in range(post_down_count):
        UpVote.objects.create(
            session_key=f"p{post.id}-down-{k}",
            post=post,
            is_upvote=False,
        )

    for reply in replies:
        reply_up_count = random.randint(10, 50)
        reply_down_count = random.randint(10, 50)

        for k in range(reply_up_count):
            UpVote.objects.create(
                session_key=f"r{reply.id}-up-{k}",
                reply=reply,
                is_upvote=True,
            )

        for k in range(reply_down_count):
            UpVote.objects.create(
                session_key=f"r{reply.id}-down-{k}",
                reply=reply,
                is_upvote=False,
            )
print("==== DONE ====")
print("Total Post   :", Post.objects.count())
print("Total Replies:", Reply.objects.count())
print("Total UpVote :", UpVote.objects.count())
