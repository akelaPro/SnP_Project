from service_objects.services import Service
from django.db.models import Count, Q
from  galery.models import Photo


class PhotoListService(Service):
    """
    Базовый сервис для получения списка фотографий с аннотациями.
    Не включает фильтрацию и сортировку - это будет делать DRF.
    """
    def process(self):
        action = self.data['action']
        queryset = Photo.objects.all()
        
        # Фильтрация по модерации (только approved)
        if action != 'restore_photo':  # Для всех действий, кроме восстановления, фильтруем по moderation='3'
            queryset = queryset.filter(moderation='3')
        
        # Аннотации для счетчиков
        queryset = queryset.annotate(
            votes_count=Count('votes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )
        
        return queryset