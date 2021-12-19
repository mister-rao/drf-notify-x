from notify.models import Notification
from rest_framework import serializers

from core.serializers import DynamicModelSerializer
from users.models.custom_user import CustomUser
from users.serializers.user_serializers import AuthorStampSerializer


class NotificationSerializer(DynamicModelSerializer):

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = 'actor_dp',

    def to_representation(self, instance):
        actor = CustomUser.objects.get(pk=instance.actor_object_id)
        representation = super().to_representation(instance)
        author = AuthorStampSerializer(actor)
        representation['actor'] = author.data

        return representation
