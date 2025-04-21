from app.schemas.user import User, UserCreate, UserUpdate, UserInDB, Token, TokenPayload
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithPostCount
from app.schemas.post import Post, PostCreate, PostUpdate, PostList
from app.schemas.series import (
    Author, AuthorCreate, AuthorUpdate,
    Series, SeriesCreate, SeriesUpdate, SeriesWithDetails,
    SeriesArticle, SeriesArticleCreate, SeriesArticleUpdate
)
from app.schemas.booklet import (
    Booklet, BookletCreate, BookletUpdate, BookletWithDetails,
    BookletChapter, BookletChapterCreate, BookletChapterUpdate,
    BookletUpdate as BookletUpdateSchema, BookletUpdateCreate, BookletUpdateUpdate
)
from app.schemas.learning_path import (
    LearningPath, LearningPathCreate, LearningPathUpdate, LearningPathWithDetails,
    LearningPathModule, LearningPathModuleCreate, LearningPathModuleUpdate, LearningPathModuleWithItems,
    LearningPathContentItem, LearningPathContentItemCreate, LearningPathContentItemUpdate,
    LearningPathResource, LearningPathResourceCreate, LearningPathResourceUpdate
)
from app.schemas.quiz import (
    Quiz, QuizCreate, QuizUpdate, QuizWithUserAttempt,
    QuizQuestion, QuizQuestionCreate, QuizQuestionUpdate,
    QuizAnswer, QuizAnswerCreate, QuizAnswerUpdate,
    UserQuizAttempt, UserQuizAttemptCreate, UserQuizAttemptUpdate
)
from app.schemas.award import (
    Award, AwardCreate, AwardUpdate, AwardWithDetails,
    UserAward, UserAwardCreate, UserAwardUpdate, UserWithAwards
)
from app.schemas.course import (
    CourseCategory, CourseCategoryCreate, CourseCategoryUpdate, CourseCategoryWithSubcategories,
    Course, CourseCreate, CourseUpdate, CourseWithDetails,
    CourseModule, CourseModuleCreate, CourseModuleUpdate, CourseModuleWithTopics,
    CourseTopic, CourseTopicCreate, CourseTopicUpdate, CourseTopicWithLessons,
    TopicLesson, TopicLessonCreate, TopicLessonUpdate, TopicLessonWithQuiz,
    CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentUpdate,
    CourseProgress, CourseProgressCreate, CourseProgressUpdate
)
from app.schemas.marketing import (
    NewsletterSubscription, NewsletterSubscriptionCreate, NewsletterSubscriptionUpdate,
    MarketingBanner, MarketingBannerCreate, MarketingBannerUpdate, BannerStatisticsUpdate
)
