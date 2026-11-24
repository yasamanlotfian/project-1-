
from database import SessionLocal, engine, Base

from passlib.context import CryptContext

from tables.user import User
from tables.blog import Blog
from tables.gallery import Gallery
from tables.comment import Comment
from tables.tag import Tag
from tables.category import Category


Base.metadata.create_all(bind=engine)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def seed_data():

    print("DATA GENERATION STARTED")

    db = SessionLocal()

    try:

        if db.query(User).first():

            print("Users already exist. Adding comments...")

            admin_user = (
                db.query(User)
                .filter(User.username == "admin")
                .first()
            )

            if not admin_user:
                admin_user = db.query(User).first()

            english_blogs = [
                Blog(
                    title="Important Hair Care Tips",
                    slug="hair-care-tips-en",
                    seo_title="Best Hair Care Tips",
                    description="Simple tips for having healthy and beautiful hair.",
                    content="""
Hair care is important for having healthy and beautiful hair.

Choose a suitable shampoo, use conditioner and hair masks,
and avoid excessive heat styling.
""",
                    view_num=0,
                    user_id=admin_user.id,
                    language="en"
                ),
                Blog(
                    title="How to Take Care of Your Nails",
                    slug="nail-care-tips-en",
                    seo_title="Best Nail Care Tips",
                    description="Simple tips for having healthy and beautiful nails.",
                    content="""
Taking care of your nails is important for keeping your hands healthy.

Keep your nails clean, trim them regularly,
and use suitable moisturizing products.
""",
                    view_num=0,
                    user_id=admin_user.id,
                    language="en"
                ),
                Blog(
                    title="Skin Care Before Makeup",
                    slug="skin-care-before-makeup-en",
                    seo_title="Skin Care Before Makeup",
                    description="Useful tips for preparing your skin before applying makeup.",
                    content="""
Preparing your skin before makeup is important.

Cleanse your skin properly, apply a suitable moisturizer,
and use sunscreen during the day.
""",
                    view_num=0,
                    user_id=admin_user.id,
                    language="en"
                ),
                Blog(
                    title="How to Care for Dry Hair",
                    slug="dry-hair-care-en",
                    seo_title="Best Ways to Care for Dry Hair",
                    description="Simple ways to care for and strengthen dry hair.",
                    content="""
Dry hair usually needs extra moisture and care.

Use a suitable shampoo, conditioner, and hair mask
to help maintain moisture.
""",
                    view_num=0,
                    user_id=admin_user.id,
                    language="en"
                )
            ]

            for english_blog in english_blogs:

                existing_blog = (
                    db.query(Blog)
                    .filter(Blog.slug == english_blog.slug)
                    .first()
                )

                if not existing_blog:
                    db.add(english_blog)

            blogs = db.query(Blog).order_by(Blog.id).limit(4).all()

            if not blogs:
                print("No blogs found!")
                return

            comments_data = [
                ("سارا", "مقاله خیلی مفیدی بود."),
                ("مریم", "نکات مراقبت از ناخن خیلی خوب بود."),
                ("نگار", "مطلب مفیدی درباره مراقبت از پوست بود."),
                ("زهرا", "نکات مراقبت از موهای خشک خیلی مفید بود."),
            ]

            for blog, (name, content) in zip(blogs, comments_data):

                db.add(
                    Comment(
                        blog_id=blog.id,
                        name=name,
                        content=content
                    )
                )

            db.commit()

            print("Comments added successfully!")
            return

        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=pwd_context.hash("12345893"),
            role="admin"
        )

        operator_user = User(
            username="operator",
            email="operator@example.com",
            password=pwd_context.hash("12345679"),
            role="operator"
        )

        normal_user = User(
            username="user",
            email="user@example.com",
            password=pwd_context.hash("23453682"),
            role="user"
        )

        db.add_all([
            admin_user,
            operator_user,
            normal_user
        ])

        db.flush()

        blog1 = Blog(
            title="نکات مهم برای مراقبت از مو",
            slug="hair-care-tips",
            seo_title="بهترین روش مراقبت از مو",
            description="چند نکته ساده برای داشتن موهایی سالم و زیبا.",
            content="""
مراقبت از مو یکی از مهم‌ترین کارها برای داشتن موهایی سالم و زیبا است.

برای مراقبت از مو باید به شست‌وشوی صحیح، انتخاب شامپوی مناسب،
استفاده از نرم‌کننده و ماسک مو توجه کرد.

همچنین بهتر است استفاده از سشوار و اتو مو را کاهش دهید.
""",
            view_num=0,
            user_id=admin_user.id,
            language="fa"
        )

        blog2 = Blog(
            title="چگونه از ناخن‌های خود مراقبت کنیم؟",
            slug="nail-care-tips",
            seo_title="روش‌های مراقبت از ناخن",
            description="نکات ساده برای داشتن ناخن‌های سالم و زیبا.",
            content="""
مراقبت از ناخن‌ها برای داشتن دست‌هایی زیبا و سالم اهمیت زیادی دارد.

تمیز نگه داشتن ناخن‌ها، کوتاه کردن منظم آن‌ها و استفاده از محصولات
مراقبتی مناسب می‌تواند به سلامت ناخن کمک کند.
""",
            view_num=0,
            user_id=admin_user.id,
            language="fa"
        )

        blog3 = Blog(
            title="مراقبت از پوست قبل از آرایش",
            slug="skin-care-before-makeup",
            seo_title="مراقبت از پوست قبل از میکاپ",
            description="چند نکته کاربردی برای آماده کردن پوست قبل از آرایش.",
            content="""
آماده کردن پوست قبل از آرایش یکی از مهم‌ترین مراحل برای داشتن
یک میکاپ زیبا و ماندگار است.

ابتدا باید پوست را به خوبی تمیز کرد و سپس از مرطوب‌کننده مناسب
استفاده کرد.
""",
            view_num=0,
            user_id=admin_user.id,
            language="fa"
        )

        blog4 = Blog(
            title="روش‌های مراقبت از موهای خشک",
            slug="dry-hair-care",
            seo_title="بهترین روش مراقبت از موهای خشک",
            description="روش‌های ساده برای مراقبت و تقویت موهای خشک.",
            content="""
موهای خشک معمولاً به مراقبت و رطوبت بیشتری نیاز دارند.

استفاده از شامپوی مناسب، نرم‌کننده و ماسک مو می‌تواند
به حفظ رطوبت مو کمک کند.
""",
            view_num=0,
            user_id=admin_user.id,
            language="fa"
        )

        blog5 = Blog(
            title="Important Hair Care Tips",
            slug="hair-care-tips-en",
            seo_title="Best Hair Care Tips",
            description="Simple tips for having healthy and beautiful hair.",
            content="""
Hair care is important for having healthy and beautiful hair.

Choose a suitable shampoo, use conditioner and hair masks,
and avoid excessive heat styling.
""",
            view_num=0,
            user_id=admin_user.id,
            language="en"
        )

        blog6 = Blog(
            title="How to Take Care of Your Nails",
            slug="nail-care-tips-en",
            seo_title="Best Nail Care Tips",
            description="Simple tips for having healthy and beautiful nails.",
            content="""
Taking care of your nails is important for keeping your hands healthy.

Keep your nails clean, trim them regularly,
and use suitable moisturizing products.
""",
            view_num=0,
            user_id=admin_user.id,
            language="en"
        )

        blog7 = Blog(
            title="Skin Care Before Makeup",
            slug="skin-care-before-makeup-en",
            seo_title="Skin Care Before Makeup",
            description="Useful tips for preparing your skin before applying makeup.",
            content="""
Preparing your skin before makeup is important.

Cleanse your skin properly, apply a suitable moisturizer,
and use sunscreen during the day.
""",
            view_num=0,
            user_id=admin_user.id,
            language="en"
        )

        blog8 = Blog(
            title="How to Care for Dry Hair",
            slug="dry-hair-care-en",
            seo_title="Best Ways to Care for Dry Hair",
            description="Simple ways to care for and strengthen dry hair.",
            content="""
Dry hair usually needs extra moisture and care.

Use a suitable shampoo, conditioner, and hair mask
to help maintain moisture.
""",
            view_num=0,
            user_id=admin_user.id,
            language="en"
        )

        db.add_all([
            blog1,
            blog2,
            blog3,
            blog4,
            blog5,
            blog6,
            blog7,
            blog8
        ])

        db.flush()

        category1 = Category(
            name="مراقبت از مو",
        )

        category2 = Category(
            name="مراقبت از ناخن",
        )

        category3 = Category(
            name="مراقبت از پوست",
        )

        db.add_all([
            category1,
            category2,
            category3
        ])

        db.flush()

        tag1 = Tag(name="مو")
        tag2 = Tag(name="ناخن")
        tag3 = Tag(name="پوست")
        tag4 = Tag(name="مراقبت و زیبایی")

        db.add_all([
            tag1,
            tag2,
            tag3,
            tag4
        ])

        db.flush()

        comment1 = Comment(
            blog_id=blog1.id,
            name="سارا",
            content="مقاله خیلی مفیدی بود."
        )

        comment2 = Comment(
            blog_id=blog2.id,
            name="مریم",
            content="نکات مراقبت از ناخن خیلی خوب بود."
        )

        comment3 = Comment(
            blog_id=blog3.id,
            name="نگار",
            content="مطلب مفیدی درباره مراقبت از پوست بود."
        )

        comment4 = Comment(
            blog_id=blog4.id,
            name="زهرا",
            content="نکات مراقبت از موهای خشک خیلی مفید بود."
        )

        db.add_all([
            comment1,
            comment2,
            comment3,
            comment4
        ])

        db.flush()

        gallery1 = Gallery(
            title="مراقبت از مو",
            file_id=1,
        )

        gallery2 = Gallery(
            title="مراقبت از ناخن",
            file_id=2,
        )

        gallery3 = Gallery(
            title="مراقبت از پوست",
            file_id=3,
        )

        gallery4 = Gallery(
            title="مراقبت از موهای خشک",
            file_id=4,
        )

        db.add_all([
            gallery1,
            gallery2,
            gallery3,
            gallery4
        ])

        db.flush()

        db.commit()

        print("DATA GENERATION COMPLETED")
        print("Users: 3")
        print("Blogs: 8")
        print("Comments: 4")
        print("Galleries: 4")

    except Exception as e:

        db.rollback()

        print("ERROR:", e)

    finally:

        db.close()


if __name__ == "__main__":
    seed_data()
