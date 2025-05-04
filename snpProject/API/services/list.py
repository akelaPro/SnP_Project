from service_objects.services import Service
from django.db.models import Count, Q
from  galery.models import Photo


class PhotoListService(Service):
    def process(self):
        action = self.data['action']
        include_deleted = self.data.get('include_deleted', False)
        search = self.data.get('search', '')
        ordering = self.data.get('ordering', '-published_at')
        request = self.data.get('request')
        
        queryset = Photo.objects.all()
        
        # Фильтрация по модерации
        if not include_deleted and action != 'restore_photo':
            queryset = queryset.filter(moderation='3')
        elif action == 'restore_photo' or include_deleted:
            queryset = queryset.filter(moderation__in=['1', '3'])
        
        # Применяем поиск
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__username__icontains=search) |
                Q(description__icontains=search)
            )
        # Аннотации для счетчиков
        queryset = queryset.annotate(
            votes_count=Count('votes', distinct=True),
            comments_count=Count('comments', distinct=True)
        )
        
        # Применяем сортировку
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset