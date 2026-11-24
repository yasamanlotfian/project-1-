
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

        admin_user = db.query(User).filter(
            User.username == "admin"
        ).first()

        if not admin_user:

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

        blog1 = db.query(Blog).filter(
            Blog.slug == "hair-care-tips-fa"
        ).first()

        if not blog1:
            blog1 = Blog(
                title="نکات مهم برای مراقبت از مو",
                slug="hair-care-tips-fa",
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
            db.add(blog1)

        blog2 = db.query(Blog).filter(
            Blog.slug == "nail-care-tips-fa"
        ).first()

        if not blog2:
            blog2 = Blog(
                title="چگونه از ناخن‌های خود مراقبت کنیم؟",
                slug="nail-care-tips-fa",
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
            db.add(blog2)

        blog3 = db.query(Blog).filter(
            Blog.slug == "skin-care-before-makeup-fa"
        ).first()

        if not blog3:
            blog3 = Blog(
                title="مراقبت از پوست قبل از آرایش",
                slug="skin-care-before-makeup-fa",
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
            db.add(blog3)

        blog4 = db.query(Blog).filter(
            Blog.slug == "dry-hair-care-fa"
        ).first()

        if not blog4:
            blog4 = Blog(
                title="روش‌های مراقبت از موهای خشک",
                slug="dry-hair-care-fa",
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
            db.add(blog4)

        blog5 = db.query(Blog).filter(
            Blog.slug == "hair-care-tips-en"
        ).first()

        if not blog5:
            blog5 = Blog(
                title="Important Hair Care Tips",
                slug="hair-care-tips-en",
                seo_title="Best Hair Care Tips",
                description="Simple tips for having healthy and beautiful hair.",
                content="""
Hair care is important for maintaining healthy and beautiful hair.

Choose a suitable shampoo, use conditioner and hair masks,
and avoid excessive use of hair dryers and straighteners.
""",
                view_num=0,
                user_id=admin_user.id,
                language="en"
            )
            db.add(blog5)

        blog6 = db.query(Blog).filter(
            Blog.slug == "nail-care-tips-en"
        ).first()

        if not blog6:
            blog6 = Blog(
                title="How to Take Care of Your Nails",
                slug="nail-care-tips-en",
                seo_title="Nail Care Tips",
                description="Simple tips for keeping your nails healthy and beautiful.",
                content="""
Taking care of your nails is important for healthy hands.

Keep your nails clean, trim them regularly, and use suitable
nail care products to maintain healthy nails.
""",
                view_num=0,
                user_id=admin_user.id,
                language="en"
            )
            db.add(blog6)

        blog7 = db.query(Blog).filter(
            Blog.slug == "skin-care-before-makeup-en"
        ).first()

        if not blog7:
            blog7 = Blog(
                title="Skin Care Before Makeup",
                slug="skin-care-before-makeup-en",
                seo_title="Skin Care Before Makeup",
                description="Practical tips for preparing your skin before makeup.",
                content="""
Preparing your skin before makeup is important for achieving
a beautiful and long-lasting makeup look.

Clean your skin properly and apply a suitable moisturizer
before applying makeup.
""",
                view_num=0,
                user_id=admin_user.id,
                language="en"
            )
            db.add(blog7)

        blog8 = db.query(Blog).filter(
            Blog.slug == "dry-hair-care-en"
        ).first()

        if not blog8:
            blog8 = Blog(
                title="How to Care for Dry Hair",
                slug="dry-hair-care-en",
                seo_title="Best Care for Dry Hair",
                description="Simple ways to care for and strengthen dry hair.",
                content="""
Dry hair usually needs extra moisture and care.

Using a suitable shampoo, conditioner, and hair mask
can help maintain moisture in your hair.
""",
                view_num=0,
                user_id=admin_user.id,
                language="en"
            )
            db.add(blog8)

        db.flush()

        category1 = db.query(Category).filter(
            Category.name == "مراقبت از مو"
        ).first()

        if not category1:
            category1 = Category(name="مراقبت از مو")
            db.add(category1)

        category2 = db.query(Category).filter(
            Category.name == "مراقبت از ناخن"
        ).first()

        if not category2:
            category2 = Category(name="مراقبت از ناخن")
            db.add(category2)

        category3 = db.query(Category).filter(
            Category.name == "مراقبت از پوست"
        ).first()

        if not category3:
            category3 = Category(name="مراقبت از پوست")
            db.add(category3)

        db.flush()

        tag1 = db.query(Tag).filter(Tag.name == "مو").first()
        if not tag1:
            tag1 = Tag(name="مو")
            db.add(tag1)

        tag2 = db.query(Tag).filter(Tag.name == "ناخن").first()
        if not tag2:
            tag2 = Tag(name="ناخن")
            db.add(tag2)

        tag3 = db.query(Tag).filter(Tag.name == "پوست").first()
        if not tag3:
            tag3 = Tag(name="پوست")
            db.add(tag3)

        tag4 = db.query(Tag).filter(
            Tag.name == "مراقبت و زیبایی"
        ).first()

        if not tag4:
            tag4 = Tag(name="مراقبت و زیبایی")
            db.add(tag4)

        db.flush()

        comments_data = [
            ("hair-care-tips-fa", "سارا", "مقاله خیلی مفیدی بود."),
            ("nail-care-tips-fa", "مریم", "نکات مراقبت از ناخن خیلی خوب بود."),
            ("skin-care-before-makeup-fa", "نگار", "مطلب مفیدی درباره مراقبت از پوست بود."),
            ("dry-hair-care-fa", "زهرا", "نکات مراقبت از موهای خشک خیلی مفید بود."),
        ]

        for slug, name, content in comments_data:

            blog = db.query(Blog).filter(
                Blog.slug == slug
            ).first()

            if blog:

                existing_comment = db.query(Comment).filter(
                    Comment.blog_id == blog.id,
                    Comment.name == name,
                    Comment.content == content
                ).first()

                if not existing_comment:

                    db.add(
                        Comment(
                            blog_id=blog.id,
                            name=name,
                            content=content
                        )
                    )

        db.flush()

        gallery_data = [
            ("مراقبت از مو", 1),
            ("مراقبت از ناخن", 2),
            ("مراقبت از پوست", 3),
            ("مراقبت از موهای خشک", 4),
        ]

        for title, file_id in gallery_data:

            existing_gallery = db.query(Gallery).filter(
                Gallery.title == title
            ).first()

            if not existing_gallery:

                db.add(
                    Gallery(
                        title=title,
                        file_id=file_id
                    )
                )

        db.commit()

        print("DATA GENERATION COMPLETED")
        print("Users: 3")
        print("Blogs: 8")
        print("Persian blogs: 4")
        print("English blogs: 4")
        print("Comments: 4")
        print("Galleries: 4")

    except Exception as e:

        db.rollback()

        print("ERROR:", e)

    finally:

        db.close()


if __name__ == "__main__":
    seed_data()
