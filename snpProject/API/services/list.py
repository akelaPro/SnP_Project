from service_objects.services import Service
from django.db.models import Count, Q
from  galery.models import Photo


class PhotoListService(Service):
    def process(self):
        action = self.data['action']
        include_deleted = self.data.get('include_deleted', False)
        queryset = Photo.objects.all()
        
        # Фильтрация по модерации
        if not include_deleted and action != 'restore_photo':
            # Для обычных запросов показываем только approved
            queryset = queryset.filter(moderation='3')
        elif action == 'restore_photo' or include_deleted:
            # Для восстановления или запросов с include_deleted показываем все, включая удаленные
            queryset = queryset.filter(moderation__in=['1', '3'])
        
        # Аннотации для счетчиков
        queryset = queryset.annotate(
            votes_count=Count('votes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )
        
        return queryset