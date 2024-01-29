from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Модель Author
class Author(models.Model):
    # Поле - cвязь «один к одному» с встроенной моделью пользователей User
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)

    # Поле - рейтинг пользователя.
    ratingAuthor = models.SmallIntegerField(default=0)

    # Метод update_rating() модели Author, который обновляет рейтинг текущего автора
    # (метод принимает в качестве аргумента только self)
    def update_rating(self):
        # Суммарный рейтинг каждой статьи автора умножается на 3
        # Если значение не найдено, то возврат. 0. Избегаю использования временных переменных.
        prat = self.post_set.aggregate(postRating=Sum('rating')).get('postRating') or 0

        # Суммарный рейтинг всех комментариев автора. Та же аналогия.
        crat = self.authorUser.comment_set.aggregate(commentRating=Sum('rating')).get('commentRating') or 0

        # Суммарный рейтинг всех комментариев к статьям автора
        self.ratingAuthor = prat * 3 + crat
        self.save()


class Category(models.Model):
    # Поле - название категории, имеет уникальность.
    name = models.CharField(max_length=64, unique=True)


class Post(models.Model):
    # Поле автор - связь «один ко многим» с моделью Author.
    author = models.ForeignKey('Author', on_delete=models.CASCADE)

    # Поле с выбором — «статья» или «новость»
    ARTICLE = "AR"
    NEWS = "NW"
    CATEGORY_CHOICES = (
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    )
    categoryTypes = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=ARTICLE)

    # Поле - автоматическая дата и время создания.
    dateCreate = models.DateTimeField(auto_now_add=True)

    # Поле категорий - связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory)
    postCategory = models.ManyToManyField('Category', through='PostCategory')

    # Поле - заголовок статьи/новости
    title = models.CharField(max_length=128)

    # Поле - текст статьи/новости
    text = models.TextField()

    # Поле - рейтинг статьи/новости
    rating = models.SmallIntegerField(default=0)

    # Метод возвращает начало статьи (предварительный просмотр) длиной 124 символа и добовляет многоточие в конец.
    def preview(self):
        # Если длина текста меньше или равна 124 символам, то возвращаем весь текст.
        if len(self.text) <= 124:
            return "{}".format(self.text)
        # Иначе, длина текста больше 124 символов, то возвращаем 124 символа с добавлением многоточия в конце.
        else:
            return "{}{}".format(self.text[:124], '...')

    # Метод увеличивающий рейтинг на единицу
    def like(self):
        self.rating += 1
        self.save()

    # Метод уменьшающий рейтинг на единицу
    def dislike(self):
        self.rating -= 1
        self.save()


class PostCategory(models.Model):
    # Поле - связь «один ко многим» с моделью Post
    postThrough = models.ForeignKey('Post', on_delete=models.CASCADE)

    # Поле - связь «один ко многим» с моделью Category
    categoryThrough = models.ForeignKey('Category', on_delete=models.CASCADE)


class Comment(models.Model):
    # Поле - связь «один ко многим» с моделью Post
    commentPost = models.ForeignKey('Post', on_delete=models.CASCADE)

    # Поле - связь «один ко многим» со встроенной моделью User
    # (комментарии может оставить любой пользователь, необязательно автор)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)

    # Поле - текст комментария
    commentText = models.TextField()

    # Поле - дата и время создания комментария
    dateCreate = models.DateTimeField(auto_now_add=True)

    # Поле - рейтинг комментария
    rating = models.SmallIntegerField(default=0)

    # Метод увеличивающий рейтинг на единицу
    def like(self):
        self.rating += 1
        self.save()

    # Метод уменьшающий рейтинг на единицу
    def dislike(self):
        self.rating -= 1
        self.save()
