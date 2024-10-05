from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from django.db.models import F, Q, Sum, Count
from django.utils import timezone

from chickenapi.models import Content, Author, Tag, ContentTag, Category
from chickenapi.serializers import ContentSerializer, CategorySerializer


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'items_per_page'


class ContentAPIView(APIView):

    def get(self, request):

        query_params = request.query_params.dict()
        queryset = Content.objects.select_related('author').prefetch_related('content_tags__tag').all()

        author_id = query_params.get('author_id', None)
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        author_username = query_params.get('author_username')
        if author_username:
            queryset = queryset.filter(author__username=author_username)

        timeframe = query_params.get('timeframe', None)
        if timeframe:
            days = int(timeframe)
            queryset = queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=days))

        tag_id = query_params.get('tag_id', None)
        if tag_id:
            queryset = queryset.filter(content_tags__tag_id=tag_id)

        title = query_params.get('title', None)
        if title:
            queryset = queryset.filter(title__icontains=title)

        queryset = queryset.order_by('-id')

        paginator = CustomPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serialized = ContentSerializer(paginated_queryset, many=True)

        for serialized_data in serialized.data:
            # Calculating `Total Engagement`
            # Calculating `Engagement Rate`

            like_count = serialized_data.get("like_count", 0)
            comment_count = serialized_data.get("comment_count", 0)
            share_count = serialized_data.get("share_count", 0)
            view_count = serialized_data.get("view_count", 0)

            total_engagement = like_count + comment_count + share_count
            if view_count > 0:
                engagement_rate = total_engagement / view_count
            else:
                engagement_rate = 0
            serialized_data["content"]["engagement_rate"] = engagement_rate
            serialized_data["content"]["total_engagement"] = total_engagement
            tags = list(
                ContentTag.objects.filter(
                    content_id=serialized_data["content"]["id"]
                ).values_list("tag__name", flat=True)
            )
            serialized_data["content"]["tags"] = tags
        return Response(serialized.data, status=status.HTTP_200_OK)


class ContentStatsAPIView(APIView):

    def get(self, request):
        query_params = request.query_params.dict()
        queryset = Content.objects.select_related('author').prefetch_related('content_tags__tag').all()

        author_id = query_params.get('author_id')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        author_username = query_params.get('author_username')
        if author_username:
            queryset = queryset.filter(author__username=author_username)

        tag_id = query_params.get('tag_id')
        if tag_id:
            queryset = queryset.filter(content_tags__tag_id=tag_id)

        tag_name = query_params.get('tag')
        if tag_name:
            queryset = queryset.filter(content_tags__tag)

        title = query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)

        if not queryset:
            return Response({"msg": "No data found"}, status=status.HTTP_404_NOT_FOUND)
        stats = queryset.aggregate(
            total_likes=Sum('like_count'),
            total_shares=Sum('share_count'),
            total_comments=Sum('comment_count'),
            total_views=Sum('view_count'),
            total_contents=Count('id'),
            total_followers=Sum('author__followers')
        )

        total_engagement = stats['total_likes'] + stats['total_shares'] + stats['total_comments']
        total_engagement_rate = total_engagement / stats['total_views'] if stats['total_views'] else 0

        data = {
            "total_likes": stats['total_likes'] or 0,
            "total_shares": stats['total_shares'] or 0,
            "total_views": stats['total_views'] or 0,
            "total_comments": stats['total_comments'] or 0,
            "total_engagement": total_engagement,
            "total_engagement_rate": total_engagement_rate,
            "total_contents": stats['total_contents'] or 0,
            "total_followers": stats['total_followers'] or 0,
        }

        return Response(data, status=status.HTTP_200_OK)


class CategoryListView(APIView):
    """
    API View to fetch all categories and their respective tags.
    """
    def get(self, request):
        categories = Category.objects.prefetch_related('tags').all()
        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)