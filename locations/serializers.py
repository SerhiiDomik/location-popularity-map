from rest_framework import serializers
from django.core.validators import MaxValueValidator, MinValueValidator
from .models import Location, Review, ReviewReaction, ReactionType


class ReviewReactionSerializer(serializers.ModelSerializer):
    reaction = serializers.ChoiceField(choices=ReactionType.choices)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReviewReaction
        fields = ['id', 'reaction', 'user']


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'comment', 'rating', 'created_at',
            'like_count', 'dislike_count'
        ]

    def get_like_count(self, obj):
        return obj.reactions.filter(reaction=ReactionType.LIKE).count()

    def get_dislike_count(self, obj):
        return obj.reactions.filter(reaction=ReactionType.DISLIKE).count()

    def validate(self, data):
        comment = data.get('comment', '')
        if not comment.strip():
            raise serializers.ValidationError({'comment': 'Comment cannot be empty.'})
        return data


class LocationListSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'category',
            'created_at', 'average_rating',
        ]

    def validate(self, data):
        errors = {}
        name = data.get('name', '')
        if not name.strip():
            errors['name'] = 'Name cannot be empty.'
        elif len(name) > 255:
            errors['name'] = 'Name is too long.'

        description = data.get('description', '')
        if not description.strip():
            errors['description'] = 'Description cannot be empty.'

        category = data.get('category', '')
        if not category.strip():
            errors['category'] = 'Category cannot be empty.'
        elif len(category) > 100:
            errors['category'] = 'Category is too long.'

        if errors:
            raise serializers.ValidationError(errors)
        return data


class LocationDetailSerializer(LocationListSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'description', 'category',
            'created_at', 'average_rating', 'reviews',
        ]
