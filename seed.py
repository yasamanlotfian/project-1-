
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
            user_id=admin_user.id
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
            user_id=admin_user.id
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
            user_id=admin_user.id
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
            user_id=admin_user.id
        )

        db.add_all([
            blog1,
            blog2,
            blog3,
            blog4
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
        print("Blogs: 4")
        print("Comments: 4")
        print("Galleries: 4")

    except Exception as e:

        db.rollback()

        print("ERROR:", e)

    finally:

        db.close()


if __name__ == "__main__":
    seed_data()
